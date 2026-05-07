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
# FUNÇÕES AUXILIARES
# ======================================================

MESES = [
    "janeiro", "fevereiro", "março", "abril",
    "maio", "junho", "julho", "agosto",
    "setembro", "outubro", "novembro", "dezembro"
]


def normalizar_texto(texto):
    return re.sub(r"\s+", " ", texto.lower())


# ======================================================
# EXTRAÇÕES ESPECÍFICAS
# ======================================================

def extrair_vigencia(texto):
    texto = normalizar_texto(texto)

    # Ex: "vigência do contrato: 12 (doze) meses"
    match = re.search(r"vigência.*?(\d{1,2})\s*\(?.*?\)?\s*meses", texto)
    if match:
        return f"{match.group(1)} meses"

    return "Não identificado"


def extrair_quantidade_licencas(texto):
    texto = normalizar_texto(texto)

    # Ex: "total de licenças contratadas: 100"
    match = re.search(r"(\d{1,4})\s*\(?.*?\)?\s*licenças", texto)
    if match:
        return match.group(1)

    return "Não identificado"


def extrair_ambiente(texto):
    texto = normalizar_texto(texto)

    if "portal mb" in texto:
        return "Portal MB"
    if "web" in texto:
        return "Web"
    if "aplicativo" in texto:
        return "Aplicativo"

    return "Não identificado"


def extrair_catalogos(texto):
    texto = normalizar_texto(texto)

    catalogos = []
    possiveis = [
        "ciências jurídicas",
        "ciências exatas",
        "letras e artes",
        "ciências pedagógicas",
        "ciências sociais aplicadas",
        "saúde",
        "técnico completo",
        "medicina"
    ]

    for cat in possiveis:
        if cat in texto:
            catalogos.append(cat.title())

    if catalogos:
        return ", ".join(catalogos)

    return "Não identificado"


def extrair_app(texto):
    texto = normalizar_texto(texto)

    # Contrato geralmente marca [x] WEB [ ] Aplicativo
    if "aplicativo" in texto and "[ x ] aplicativo" in texto:
        return "Sim"

    # Se só WEB estiver marcado
    if "forma de acesso" in texto and "web" in texto and "aplicativo" in texto:
        return "Não"

    return "Não identificado"


def extrair_meses_gestao_licencas(texto):
    """
    Extrai meses de gestão de licenças de forma semântica.
    Funciona para frases longas e linguagem jurídica.
    """
    texto = normalizar_texto(texto)

    # Só tenta se existir contexto de gestão de licenças
    if "gestão de licenças" not in texto:
        return "Não identificado"

    encontrados = [
        mes for mes in MESES if mes in texto
    ]

    if not encontrados:
        return "Não identificado"

    # Remove duplicados e mantém ordem natural dos meses
    meses_ordenados = [
        mes for mes in MESES if mes in set(encontrados)
    ]

    return ", ".join(meses_ordenados)


# ======================================================
# FUNÇÃO PRINCIPAL (USADA PELO APP)
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
