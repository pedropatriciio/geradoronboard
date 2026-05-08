import pdfplumber
import re


# ======================================================
# EXTRAÇÃO BRUTA DO PDF
# ======================================================

def extrair_texto_pdf(caminho_pdf):
    texto = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            t = pagina.extract_text()
            if t:
                texto += "\n" + t
    return texto


# ======================================================
# HELPERS
# ======================================================

MESES = [
    "janeiro", "fevereiro", "março", "abril",
    "maio", "junho", "julho", "agosto",
    "setembro", "outubro", "novembro", "dezembro"
]


def normalizar(texto):
    return re.sub(r"\s+", " ", texto.lower())


def normalizar_numero(numero_str):
    """
    Converte '15.000' -> '15000'
    """
    return numero_str.replace(".", "")


def extrair_bloco(texto, inicio, paradas):
    padrao = rf"{inicio}(.*?)(?:{'|'.join(paradas)})"
    match = re.search(padrao, texto, re.IGNORECASE | re.DOTALL)
    return match.group(1) if match else ""


# ======================================================
# EXTRAÇÕES
# ======================================================

def extrair_vigencia(texto):
    texto = normalizar(texto)
    m = re.search(r"vigência do contrato:\s*(\d+)", texto)
    return f"{m.group(1)} meses" if m else "Não identificado"


def extrair_total_licencas(texto):
    texto = normalizar(texto)

    # Ex.: 15.000 (quinze mil) licenças
    m = re.search(r"total de licenças contratadas:\s*([\d\.]+)", texto)
    if m:
        return normalizar_numero(m.group(1))

    return "Não identificado"


def extrair_catalogos(texto):
    texto = normalizar(texto)
    catalogos = []

    # -----------------------
    # MEDICINA (bloco próprio)
    # -----------------------
    if re.search(r"\[\s*x\s*\]\s*medicina", texto):
        catalogos.append("Medicina")

    # -----------------------
    # DEMAIS CATÁLOGOS
    # -----------------------
    bloco = extrair_bloco(
        texto,
        "demais catálogos",
        [
            "valor unitário",
            "valor total",
            "forma de acesso",
            "pré-cadastro",
            "gestão de licenças"
        ]
    )

    marcados = re.findall(
        r"\[\s*x\s*\]\s*([a-zà-ú\s]+)",
        bloco
    )

    for cat in marcados:
        nome = cat.strip().title()
        if nome not in catalogos:
            catalogos.append(nome)

    return ", ".join(catalogos) if catalogos else "Não identificado"


def extrair_ambiente(texto):
    texto = normalizar(texto)
    if re.search(r"\[\s*x\s*\]\s*portal mb", texto):
        return "Portal MB"
    if re.search(r"\[\s*x\s*\]\s*web", texto):
        return "Web"
    return "Não identificado"


def extrair_app(texto):
    texto = normalizar(texto)
    return "Sim" if re.search(r"\[\s*x\s*\]\s*aplicativo", texto) else "Não"


def extrair_meses_gestao(texto):
    texto = normalizar(texto)
    bloco = extrair_bloco(
        texto,
        "gestão de licenças:",
        ["anexo", "cláusula", "d4sign"]
    )
    meses = [m for m in MESES if m in bloco]
    return ", ".join(meses) if meses else "Não identificado"


# ======================================================
# FUNÇÃO PRINCIPAL
# ======================================================

def parse_contrato_pdf(texto_pdf):
    return {
        "vigencia": extrair_vigencia(texto_pdf),
        "licencas": extrair_total_licencas(texto_pdf),
        "catalogos": extrair_catalogos(texto_pdf),
        "ambiente": extrair_ambiente(texto_pdf),
        "gestao_licencas": extrair_meses_gestao(texto_pdf),
        "app": extrair_app(texto_pdf),
    }
