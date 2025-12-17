const startNumber = 654;

function modulo11(base43) {
  let peso = 2, soma = 0;
  for (let i = base43.length - 1; i >= 0; i--) {
    soma += parseInt(base43[i]) * peso;
    peso = peso === 9 ? 2 : peso + 1;
  }
  const resto = soma % 11;
  return (resto === 0 || resto === 1) ? "0" : String(11 - resto);
}

function gerarChave(cUF, cnpj, modelo, serie, numero) {
  const now = new Date();
  const aamm = String(now.getFullYear()).slice(2) + String(now.getMonth()+1).padStart(2,"0");
  const num = String(numero).padStart(9, "0");
  const codigo = String(Math.floor(Math.random()*1e8)).padStart(8,"0");
  const base = `${cUF}${aamm}${cnpj}${modelo}${serie}${num}${codigo}`;
  const dv = modulo11(base);
  return base + dv;
}

async function carregar(path) {
  return fetch(path).then(r => r.text());
}

function download(nome, conteudo) {
  const blob = new Blob([conteudo], { type: "application/xml" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = nome;
  a.click();
  URL.revokeObjectURL(a.href);
}

document.getElementById("gerar").onclick = async () => {
  const numero = startNumber + Math.floor(Math.random()*100000);

  const cUF = "41";
  const CNPJ = "11158565000118";

  const chCTe = gerarChave(cUF, CNPJ, "57", "001", numero);
  const chMDFe = gerarChave(cUF, CNPJ, "58", "022", numero);

  let cte = await carregar("templates/cte_base.xml");
  let mdfe = await carregar("templates/mdfe_base.xml");

  cte = cte
    .replaceAll("CHAVE_CTE", chCTe)
    .replaceAll("NUMERO_CTE", numero);

  mdfe = mdfe
    .replaceAll("CHAVE_MDFE", chMDFe)
    .replaceAll("NUMERO_MDFE", numero)
    .replaceAll("CHAVE_CTE", chCTe);

  download(`CTE_${numero}.xml`, cte);
  download(`MDFE_${numero}.xml`, mdfe);
};
