import pdfplumber
import re


# ======================================================
# EXTRAÇÃO BRUTA DO TEXTO
# ======================================================

def extrair_texto_pdf(caminho_pdf):
    texto = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for página in pdf.pages:
            t = página.extract_text()
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


def extrair_bloco(texto, inicio, paradas):
    """
    Extrai um bloco textual entre um título e o próximo título conhecido.
    """
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


def extrair_licencas(texto):
    texto = normalizar(texto)

    # Prioridade: total de licenças contratadas
    m = re.search(r"total de licenças contratadas:\s*(\d+)", texto)
    if m:
        return m.group(1)

    # Fallback
    m = re.search(r"(\d+)\s*licenças", texto)
    return m.group(1) if m else "Não identificado"


def extrair_catalogos(texto):
    texto = normalizar(texto)

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

    marcados = re.findall(r"\[\s*x\s*\]\s*([a-zà-ú\s]+)", bloco)
    catalogos = [c.strip().title() for c in marcados]

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
        [
            "d4sign",
            "pré-cadastro",
            "anexo",
            "cláusula"
        ]
    )

    encontrados = [m for m in MESES if m in bloco]
    return ", ".join(encontrados) if encontrados else "Não identificado"


# ======================================================
# FUNÇÃO PRINCIPAL
# ======================================================

def parse_contrato_pdf(texto_pdf):
    return {
        "vigencia": extrair_vigencia(texto_pdf),
        "licencas": extrair_licencas(texto_pdf),
        "catalogos": extrair_catalogos(texto_pdf),
        "ambiente": extrair_ambiente(texto_pdf),
        "gestao_licencas": extrair_meses_gestao(texto_pdf),
        "app": extrair_app(texto_pdf),
    }
