import pdfplumber
import re


# ======================================================
# EXTRAÇÃO DO TEXTO DO PDF
# ======================================================

def extrair_texto_pdf(caminho_pdf):
    texto = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            conteudo = pagina.extract_text()
            if conteudo:
                texto += "\n" + conteudo
    return texto


# ======================================================
# CONSTANTES E HELPERS
# ======================================================

MESES = [
    "janeiro", "fevereiro", "março", "abril",
    "maio", "junho", "julho", "agosto",
    "setembro", "outubro", "novembro", "dezembro"
]


def normalizar_texto(texto):
    return re.sub(r"\s+", " ", texto.lower())


# ======================================================
# EXTRAÇÕES
# ======================================================

def extrair_vigencia(texto):
    texto = normalizar_texto(texto)
    match = re.search(
        r"vigência.*?(\d{1,2})\s*\(?.*?\)?\s*meses",
        texto
    )
    if match:
        return f"{match.group(1)} meses"
    return "Não identificado"


def extrair_quantidade_licencas(texto):
    texto = normalizar_texto(texto)
    match = re.search(
        r"(\d{1,4})\s*\(?.*?\)?\s*licenças",
        texto
    )
    if match:
        return match.group(1)
    return "Não identificado"


# ------------------------------------------------------
# CATÁLOGOS — APENAS OS MARCADOS COM [x]
# ------------------------------------------------------

def extrair_catalogos(texto):
    texto = normalizar_texto(texto)

    # Captura SOMENTE itens marcados com [x]
    marcados = re.findall(
        r"\[\s*x\s*\]\s*([a-zà-ú\s]+)",
        texto,
        re.IGNORECASE
    )

    catalogos = [c.strip().title() for c in marcados]

    if catalogos:
        return ", ".join(catalogos)

    return "Não identificado"


# ------------------------------------------------------
# AMBIENTE
# ------------------------------------------------------

def extrair_ambiente(texto):
    texto = normalizar_texto(texto)

    if "portal mb" in texto:
        return "Portal MB"
    if re.search(r"\[\s*x\s*\]\s*web", texto):
        return "Web"
    if re.search(r"\[\s*x\s*\]\s*aplicativo", texto):
        return "Aplicativo"

    return "Não identificado"


# ------------------------------------------------------
# APP (SIM / NÃO)
# ------------------------------------------------------

def extrair_app(texto):
    texto = normalizar_texto(texto)

    # Só retorna SIM se o aplicativo estiver explicitamente marcado
    if re.search(r"\[\s*x\s*\]\s*aplicativo", texto):
        return "Sim"

    return "Não"


# ------------------------------------------------------
# MESES DE GESTÃO DE LICENÇAS — CONTEXTO CONTROLADO
# ------------------------------------------------------

def extrair_meses_gestao_licencas(texto):
    texto = normalizar_texto(texto)

    # Isola apenas o trecho referente à gestão de licenças
    match = re.search(
        r"gestão de licenças:(.*?)(?:\.|\n)",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return "Não identificado"

    trecho = match.group(1)

    encontrados = [
        mes for mes in MESES if mes in trecho
    ]

    if not encontrados:
        return "Não identificado"

    return ", ".join(encontrados)


# ======================================================
# FUNÇÃO PRINCIPAL
# ======================================================

def parse_contrato_pdf(texto_pdf):
    return {
        "vigencia": extrair_vigencia(texto_pdf),
        "ambiente": extrair_ambiente(texto_pdf),
        "licencas": extrair_quantidade_licencas(texto_pdf),
        "catalogos": extrair_catalogos(texto_pdf),
        "gestao_licencas": extrair_meses_gestao_licencas(texto_pdf),
        "app": extrair_app(texto_pdf),
    }