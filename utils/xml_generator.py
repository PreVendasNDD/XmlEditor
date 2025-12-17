import xml.etree.ElementTree as ET
import os
from datetime import datetime
import re

def carregar_modelo(tipo):
    """Carregar modelo XML base"""
    caminho_modelo = os.path.join('modelos', f'{tipo}_base.xml')
    with open(caminho_modelo, 'r', encoding='utf-8') as f:
        return f.read()

def atualizar_cte(xml_content, dados):
    """Atualizar campos do CT-e"""
    namespaces = {
        'cte': 'http://www.portalfiscal.inf.br/cte',
        'ds': 'http://www.w3.org/2000/09/xmldsig#'
    }
    
    # Registrar namespaces
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    
    root = ET.fromstring(xml_content)
    
    # Encontrar e atualizar campos do CT-e
    # 1. Atualizar Id do infCte
    infCte = root.find('.//{http://www.portalfiscal.inf.br/cte}infCte')
    if infCte is not None:
        # Extrair parte da chave para construir novo ID
        novo_id = f"CTe{dados['nova_chave_cte']}"
        infCte.set('Id', novo_id)
    
    # 2. Atualizar número do CT-e (nCT)
    nCT = root.find('.//{http://www.portalfiscal.inf.br/cte}nCT')
    if nCT is not None:
        nCT.text = dados['novo_numero_cte'].zfill(9)
    
    # 3. Atualizar chave do CT-e no protocolo
    chCTe = root.find('.//{http://www.portalfiscal.inf.br/cte}chCTe')
    if chCTe is not None:
        chCTe.text = dados['nova_chave_cte']
    
    # 4. Atualizar chave da NF-e vinculada (se fornecida)
    if dados.get('chave_nfe_vinculada'):
        chaveNFe = root.find('.//{http://www.portalfiscal.inf.br/cte}chave')
        if chaveNFe is not None:
            chaveNFe.text = dados['chave_nfe_vinculada']
    
    # 5. Atualizar data de emissão
    dhEmi = root.find('.//{http://www.portalfiscal.inf.br/cte}dhEmi')
    if dhEmi is not None and dados.get('data_emissao'):
        dhEmi.text = dados['data_emissao']
    
    # 6. Atualizar data de vencimento da duplicata
    if dados.get('data_vencimento'):
        dVenc = root.find('.//{http://www.portalfiscal.inf.br/cte}dVenc')
        if dVenc is not None:
            dVenc.text = dados['data_vencimento']
    
    # 7. Atualizar número da duplicata (relacionado ao número do CT-e)
    nDup = root.find('.//{http://www.portalfiscal.inf.br/cte}nDup')
    if nDup is not None:
        nDup.text = f"{dados['novo_numero_cte']}G 1"
    
    # 8. Atualizar QR Code com nova chave
    qrCodCTe = root.find('.//{http://www.portalfiscal.inf.br/cte}qrCodCTe')
    if qrCodCTe is not None:
        # Extrair URL base e substituir chave
        qr_text = qrCodCTe.text
        if qr_text and 'chCTe=' in qr_text:
            # Usar regex para substituir a chave no QR Code
            nova_url = re.sub(r'chCTe=[^&]*', f'chCTe={dados["nova_chave_cte"]}', qr_text)
            qrCodCTe.text = nova_url
    
    return ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')

def atualizar_mdfe(xml_content, dados):
    """Atualizar campos do MDF-e"""
    namespaces = {
        'mdfe': 'http://www.portalfiscal.inf.br/mdfe',
        'ds': 'http://www.w3.org/2000/09/xmldsig#'
    }
    
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    
    root = ET.fromstring(xml_content)
    
    # 1. Atualizar Id do MDF-e
    infMDFe = root.find('.//{http://www.portalfiscal.inf.br/mdfe}infMDFe')
    if infMDFe is not None:
        novo_id = f"MDFe{dados['nova_chave_mdfe']}"
        infMDFe.set('Id', novo_id)
    
    # 2. Atualizar número do MDF-e (nMDF)
    nMDF = root.find('.//{http://www.portalfiscal.inf.br/mdfe}nMDF')
    if nMDF is not None:
        nMDF.text = dados['novo_numero_mdfe'].zfill(9)
    
    # 3. Atualizar chave do MDF-e no protocolo
    chMDFe = root.find('.//{http://www.portalfiscal.inf.br/mdfe}chMDFe')
    if chMDFe is not None:
        chMDFe.text = dados['nova_chave_mdfe']
    
    # 4. Atualizar chave do CT-e dentro do MDF-e
    chCTe = root.find('.//{http://www.portalfiscal.inf.br/mdfe}chCTe')
    if chCTe is not None:
        chCTe.text = dados['nova_chave_cte']
    
    # 5. Atualizar data/hora de emissão
    dhEmi = root.find('.//{http://www.portalfiscal.inf.br/mdfe}dhEmi')
    if dhEmi is not None and dados.get('data_emissao'):
        dhEmi.text = dados['data_emissao']
    
    # 6. Atualizar data/hora início viagem (opcional)
    dhIniViagem = root.find('.//{http://www.portalfiscal.inf.br/mdfe}dhIniViagem')
    if dhIniViagem is not None and dados.get('data_emissao'):
        dhIniViagem.text = dados['data_emissao']
    
    # 7. Atualizar QR Code
    qrCodMDFe = root.find('.//{http://www.portalfiscal.inf.br/mdfe}qrCodMDFe')
    if qrCodMDFe is not None:
        qr_text = qrCodMDFe.text
        if qr_text and 'chMDFe=' in qr_text:
            nova_url = re.sub(r'chMDFe=[^&]*', f'chMDFe={dados["nova_chave_mdfe"]}', qr_text)
            qrCodMDFe.text = nova_url
    
    # 8. Atualizar número do protocolo (gerar novo)
    infProt = root.find('.//{http://www.portalfiscal.inf.br/mdfe}infProt')
    if infProt is not None:
        # Gerar novo número de protocolo baseado no timestamp
        novo_protocolo = f"941{datetime.now().strftime('%y%m%d')}{dados['novo_numero_mdfe'][-6:]}"
        nProt = infProt.find('.//{http://www.portalfiscal.inf.br/mdfe}nProt')
        if nProt is not None:
            nProt.text = novo_protocolo
    
    return ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')

def gerar_novos_xmls(dados, id_processo):
    """Gerar novos XMLs CT-e e MDF-e"""
    import tempfile
    
    # Carregar modelos
    cte_base = carregar_modelo('cte')
    mdfe_base = carregar_modelo('mdfe')
    
    # Atualizar XMLs
    novo_cte = atualizar_cte(cte_base, dados)
    novo_mdfe = atualizar_mdfe(mdfe_base, dados)
    
    # Salvar arquivos temporários
    arquivos = []
    
    # Nome dos arquivos
    nome_cte = f"CTe_{dados['nova_chave_cte']}_{id_processo}.xml"
    nome_mdfe = f"MDFe_{dados['nova_chave_mdfe']}_{id_processo}.xml"
    
    # Caminhos completos
    from app import app
    cte_path = os.path.join(app.config['UPLOAD_FOLDER'], nome_cte)
    mdfe_path = os.path.join(app.config['UPLOAD_FOLDER'], nome_mdfe)
    
    # Salvar CT-e
    with open(cte_path, 'w', encoding='utf-8') as f:
        f.write(novo_cte)
    arquivos.append(cte_path)
    
    # Salvar MDF-e
    with open(mdfe_path, 'w', encoding='utf-8') as f:
        f.write(novo_mdfe)
    arquivos.append(mdfe_path)
    
    return arquivos
