from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import os
import tempfile

from models import init_db, buscar_colaborador, listar_colaboradores
from pdf_parser import extrair_texto_pdf, parse_contrato_pdf
from ppt_generator import generate_ppt

app = Flask(__name__)
CORS(app)

# Inicializa banco
init_db()

BASE_DIR = os.path.dirname(__file__)


# --------------------------------------------------
# ENDPOINT: LISTAR COLABORADORES
# --------------------------------------------------
@app.route("/colaboradores", methods=["GET"])
def colaboradores():
    return jsonify(listar_colaboradores())


# --------------------------------------------------
# ENDPOINT: GERAR PPTX
# --------------------------------------------------
@app.route("/generate", methods=["POST"])
def generate():
    # -------- Dados do formulário --------
    instituicao = request.form.get("instituicao")
    possui_app = request.form.get("app")
    comercial_nome = request.form.get("comercial")
    cs_nome = request.form.get("cs")

    email_1 = request.form.get("email_1")
    email_2 = request.form.get("email_2")
    email_3 = request.form.get("email_3")

    emails = [e for e in [email_1, email_2, email_3] if e]

    pdf_file = request.files.get("contrato_pdf")

    if not instituicao or not possui_app or not comercial_nome or not cs_nome or not pdf_file or not emails:
        return jsonify({"error": "Todos os campos obrigatórios devem ser preenchidos"}), 400

    # -------- Buscar responsáveis --------
    comercial = buscar_colaborador(comercial_nome, "Comercial")
    cs = buscar_colaborador(cs_nome, "CS")

    if not comercial:
        return jsonify({"error": "Comercial responsável não encontrado"}), 422
    if not cs:
        return jsonify({"error": "CS responsável não encontrado"}), 422

    # -------- Salvar PDF temporário --------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_file.save(tmp.name)
        caminho_pdf = tmp.name

    # -------- Parse PDF --------
    try:
        texto_pdf = extrair_texto_pdf(caminho_pdf)
        dados_pdf = parse_contrato_pdf(texto_pdf)
    except Exception as e:
        return jsonify({"error": f"Erro ao ler PDF: {str(e)}"}), 500
    finally:
        if os.path.exists(caminho_pdf):
            os.remove(caminho_pdf)

    # -------- Payload final --------
    payload = {
        "instituicao": instituicao,
        "data": datetime.now().strftime("%d/%m/%Y"),

        # Slide 5
        "vigencia": dados_pdf.get("vigencia", "Não identificado"),
        "ambiente": dados_pdf.get("ambiente", "Não identificado"),
        "licencas": dados_pdf.get("licencas", "Não identificado"),
        "catalogos": dados_pdf.get("catalogos", "Não identificado"),
        "gestao_licencas": dados_pdf.get("gestao_licencas", "Não identificado"),
        "app": possui_app,

        # Slide 9
        "comercial": comercial,
        "cs": cs,

        # Slide 17
        "emails_acesso": emails
    }

    # -------- Gerar PPT --------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(BASE_DIR, f"Onboarding_CS_{timestamp}.pptx")
    template_path = os.path.join(BASE_DIR, "template.pptx")

    try:
        generate_ppt(template_path, output_path, payload)
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar PPTX: {str(e)}"}), 500

    return send_file(
        output_path,
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
