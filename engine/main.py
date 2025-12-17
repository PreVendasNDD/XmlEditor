import xml.etree.ElementTree as ET
from datetime import datetime
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

STATE_FILE = os.path.join(BASE_DIR, "state/contador.txt")
CTE_TEMPLATE = os.path.join(BASE_DIR, "templates/cte_base.xml")
MDFE_TEMPLATE = os.path.join(BASE_DIR, "templates/mdfe_base.xml")
OUT_DIR = os.path.join(BASE_DIR, "output")

NS_CTE = {"ns": "http://www.portalfiscal.inf.br/cte"}
NS_MDFE = {"ns": "http://www.portalfiscal.inf.br/mdfe"}

os.makedirs(OUT_DIR, exist_ok=True)

def modulo11(chave43):
    peso = 2
    soma = 0
    for d in reversed(chave43):
        soma += int(d) * peso
        peso = 2 if peso == 9 else peso + 1
    resto = soma % 11
    return "0" if resto in (0, 1) else str(11 - resto)

def gerar_chave(cUF, cnpj, modelo, serie, numero):
    aamm = datetime.now().strftime("%y%m")
    num = str(numero).zfill(9)
    codigo = str(random.randint(0, 99999999)).zfill(8)
    base = f"{cUF}{aamm}{cnpj}{modelo}{serie}{num}{codigo}"
    dv = modulo11(base)
    return base + dv, codigo

def ler_contador():
    with open(STATE_FILE) as f:
        return int(f.read().strip())

def salvar_contador(n):
    with open(STATE_FILE, "w") as f:
        f.write(str(n))

contador = ler_contador()

# === DADOS FIXOS (do template real) ===
CNPJ = "11158565000118"
CUF = "41"

# === CT-e ===
cte_tree = ET.parse(CTE_TEMPLATE)
cte_root = cte_tree.getroot()

chCTe, cCT = gerar_chave(CUF, CNPJ, "57", "001", contador)

cte_root.find(".//ns:ide/ns:nCT", NS_CTE).text = str(contador)
cte_root.find(".//ns:ide/ns:cCT", NS_CTE).text = cCT
cte_root.find(".//ns:infCte", NS_CTE).set("Id", f"CTe{chCTe}")
cte_root.find(".//ns:infCTeSupl/ns:qrCodCTe", NS_CTE).text = f"https://cte/qr?chCTe={chCTe}"

cte_tree.write(f"{OUT_DIR}/CTE_{contador}.xml", encoding="utf-8", xml_declaration=True)

# === MDF-e ===
mdfe_tree = ET.parse(MDFE_TEMPLATE)
mdfe_root = mdfe_tree.getroot()

chMDFe, cMDF = gerar_chave(CUF, CNPJ, "58", "022", contador)

mdfe_root.find(".//ns:ide/ns:nMDF", NS_MDFE).text = str(contador)
mdfe_root.find(".//ns:ide/ns:cMDF", NS_MDFE).text = cMDF
mdfe_root.find(".//ns:infMDFe", NS_MDFE).set("Id", f"MDFe{chMDFe}")
mdfe_root.find(".//ns:infDoc/ns:infMunDescarga/ns:infCTe/ns:chCTe", NS_MDFE).text = chCTe
mdfe_root.find(".//ns:infMDFeSupl/ns:qrCodMDFe", NS_MDFE).text = f"https://mdfe/qr?chMDFe={chMDFe}"

mdfe_tree.write(f"{OUT_DIR}/MDFE_{contador}.xml", encoding="utf-8", xml_declaration=True)

salvar_contador(contador + 1)
