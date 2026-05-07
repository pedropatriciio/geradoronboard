import pdfplumber
import re


def extrair_texto_pdf(caminho_pdf: str) -> str:
    texto = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texto += page_text + "\n"
    return texto


def parse_contrato_pdf(texto: str) -> dict:
    dados = {}

    # -------------------------------------------------
    # VIGÊNCIA (DURAÇÃO)
    # -------------------------------------------------
    m_vigencia = re.search(
        r"Vigência do contrato:\s*(\d+)\s*\(", texto, re.IGNORECASE
    )
    if m_vigencia:
        dados["vigencia"] = f"{m_vigencia.group(1)} meses"

    # -------------------------------------------------
    # TOTAL DE LICENÇAS
    # -------------------------------------------------
    m_licencas = re.search(
        r"Total de licenças contratadas:\s*(\d+)", texto, re.IGNORECASE
    )
    if m_licencas:
        dados["licencas"] = m_licencas.group(1)

    # -------------------------------------------------
    # TIPO DE INTEGRAÇÃO
    # -------------------------------------------------
    if "[ x ] Portal MB" in texto or "[x] Portal MB" in texto:
        dados["ambiente"] = "Portal MB"
    elif "[ x ] API" in texto or "[x] API" in texto:
        dados["ambiente"] = "API"

    # -------------------------------------------------
    # CATÁLOGOS CONTRATADOS (CHECKBOX)
    # -------------------------------------------------
    catalogos = []

    mapa_catalogos = {
        "Ciências Exatas": r"\[\s*x\s*\]\s*Ciências Exatas",
        "Ciências Jurídicas": r"\[\s*x\s*\]\s*Ciências Jurídicas",
        "Letras e Artes": r"\[\s*x\s*\]\s*Letras e Artes",
        "Ciências Pedagógicas": r"\[\s*x\s*\]\s*Ciências Pedagógicas",
        "Saúde": r"\[\s*x\s*\]\s*Saúde",
        "Ciências Sociais Aplicadas": r"\[\s*x\s*\]\s*Ciências Sociais Aplicadas",
    }

    for nome, pattern in mapa_catalogos.items():
        if re.search(pattern, texto):
            catalogos.append(nome)

    if catalogos:
        dados["catalogos"] = ", ".join(catalogos)

    # -------------------------------------------------
    # MESES DE GESTÃO DE LICENÇAS
    # -------------------------------------------------
    m_gestao = re.search(
        r"meses de\s*(.+?)\.", texto, re.IGNORECASE
    )
    if m_gestao:
        dados["gestao_licencas"] = m_gestao.group(1).strip()

    return dados