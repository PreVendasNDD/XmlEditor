const START = 654;
const CNPJ = "11158565000118";
const CUF = "41";

function modulo11(base) {
  let peso = 2, soma = 0;
  for (let i = base.length - 1; i >= 0; i--) {
    soma += Number(base[i]) * peso;
    peso = peso === 9 ? 2 : peso + 1;
  }
  const r = soma % 11;
  return (r === 0 || r === 1) ? "0" : String(11 - r);
}

function gerarChave(modelo, serie, numero) {
  const d = new Date();
  const aamm = String(d.getFullYear()).slice(2) + String(d.getMonth() + 1).padStart(2, "0");
  const n = String(numero).padStart(9, "0");
  const c = String(Math.floor(Math.random() * 1e8)).padStart(8, "0");
  const base = `${CUF}${aamm}${CNPJ}${modelo}${serie}${n}${c}`;
  return base + modulo11(base);
}

function baixar(nome, conteudo) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([conteudo], { type: "application/xml" }));
  a.download = nome;
  a.click();
}

document.getElementById("gerar").onclick = async () => {
  const numero = START + Math.floor(Math.random() * 100000);

  const chCTe = gerarChave("57", "001", numero);
  const chMDFe = gerarChave("58", "022", numero);

  let cte = await fetch("templates/cte_base.xml").then(r => r.text());
  let mdfe = await fetch("templates/mdfe_base.xml").then(r => r.text());

  // ===== CT-e =====
  cte = cte
    .replace(/<nCT>.*?<\/nCT>/g, `<nCT>${numero}</nCT>`)
    .replace(/CTe\d{44}/g, `CTe${chCTe}`)
    .replace(/<chCTe>\d{44}<\/chCTe>/g, `<chCTe>${chCTe}</chCTe>`)
    .replace(/chCTe=\d{44}/g, `chCTe=${chCTe}`)
    .replace(/<chave>\d{44}<\/chave>/g, `<chave>${chCTe}</chave>`);

  // ===== MDF-e =====
  mdfe = mdfe
    .replace(/<nMDF>.*?<\/nMDF>/g, `<nMDF>${numero}</nMDF>`)
    .replace(/MDFe\d{44}/g, `MDFe${chMDFe}`)
    .replace(/<chMDFe>\d{44}<\/chMDFe>/g, `<chMDFe>${chMDFe}</chMDFe>`)
    .replace(/chMDFe=\d{44}/g, `chMDFe=${chMDFe}`)
    .replace(/<chCTe>\d{44}<\/chCTe>/g, `<chCTe>${chCTe}</chCTe>`);

  baixar(`CTE_${numero}.xml`, cte);
  baixar(`MDFE_${numero}.xml`, mdfe);
};
