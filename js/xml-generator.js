class XmlEditor {
    constructor() {
        this.cteTemplate = null;
        this.mdfeTemplate = null;
    }
    
    carregarTemplate(file, tipo) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                if (tipo === 'cte') {
                    this.cteTemplate = e.target.result;
                } else {
                    this.mdfeTemplate = e.target.result;
                }
                resolve();
            };
            reader.readAsText(file);
        });
    }
    
    gerarNovoCte(dados) {
        if (!this.cteTemplate) throw new Error('Template CT-e não carregado');
        
        let xml = this.cteTemplate;
        
        // Substituir campos
        xml = xml.replace(/CTe\d{44}/g, `CTe${dados.chaveCte}`);
        xml = xml.replace(/<nCT>.*<\/nCT>/, `<nCT>${dados.numeroCte.padStart(9, '0')}</nCT>`);
        xml = xml.replace(/<chCTe>.*<\/chCTe>/, `<chCTe>${dados.chaveCte}</chCTe>`);
        
        if (dados.chaveNfe) {
            xml = xml.replace(/<chave>.*<\/chave>/, `<chave>${dados.chaveNfe}</chave>`);
        }
        
        // Atualizar QR Code
        xml = xml.replace(/chCTe=[^&]*/g, `chCTe=${dados.chaveCte}`);
        
        return xml;
    }
    
    gerarNovoMdfe(dados) {
        if (!this.mdfeTemplate) throw new Error('Template MDF-e não carregado');
        
        let xml = this.mdfeTemplate;
        
        // Substituir campos
        xml = xml.replace(/MDFe\d{44}/g, `MDFe${dados.chaveMdfe}`);
        xml = xml.replace(/<nMDF>.*<\/nMDF>/, `<nMDF>${dados.numeroMdfe.padStart(9, '0')}</nMDF>`);
        xml = xml.replace(/<chMDFe>.*<\/chMDFe>/, `<chMDFe>${dados.chaveMdfe}</chMDFe>`);
        xml = xml.replace(/<chCTe>.*<\/chCTe>/, `<chCTe>${dados.chaveCte}</chCTe>`);
        
        // Atualizar QR Code
        xml = xml.replace(/chMDFe=[^&]*/g, `chMDFe=${dados.chaveMdfe}`);
        
        return xml;
    }
}

// Exportar para uso global
window.XmlEditor = XmlEditor;
