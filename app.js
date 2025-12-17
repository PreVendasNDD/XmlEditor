/* =========================================================
   BANCO LOCAL (IndexedDB) — SEQUÊNCIAS
========================================================= */

const DB_NAME = "cte_mdfe_saas";
const STORE_NAME = "sequencias";

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);

    req.onupgradeneeded = e => {
      const db = e.target.result;
      const store = db.createObjectStore(STORE_NAME, { keyPath: "tipo" });

      store.put({ tipo: "NFE", ultimo: 1666666 });
      store.put({ tipo: "CTE", ultimo: 2666666 });
      store.put({ tipo: "MDFE", ultimo: 1666666 });
    };

    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function nextNumero(tipo) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const req = store.get(tipo);

    req.onsuccess = () => {
      const reg = req.result;
      reg.ultimo += 1;
      store.put(reg);
      resolve(reg.ultimo.toString().padStart(9, "0"));
    };

    req.onerror = () => reject(req.error);
  });
}

/* =========================================================
   UTILIDADES XML
========================================================= */

async function loadXML(path) {
  const res = await fetch(path);
  return await res.text();
}

function removeBlock(xml, tag) {
  const re = new RegExp(`<${tag}[\\s\\S]*?<\\/${tag}>`, "g");
  return xml.replace(re, "");
}

function replaceTag(xml, tag, value) {
  const re = new RegExp(`<${tag}>[\\s\\S]*?<\\/${tag}>`, "g");
  return xml.replace(re, `<${tag}>${value}</${tag}>`);
}

function replaceKey(xml, prefix, key) {
  const re = new RegExp(`${prefix}[0-9]{44}`, "g");
  return xml.replace(re, prefix + key);
}

/* =========================================================
   CÁLCULO DV (CHAVE FISCAL)
========================================================= */

function calcDV(ch43) {
  const pesos = [4,3,2,9,8,7,6,5,4,3,2];
  let soma = 0;
  let p = 0;

  for (let i = ch43.length - 1; i >= 0; i--) {
    soma += Number(ch43[i]) * pesos[p];
    p = (p + 1) % pesos.length;
  }

  const mod = soma % 11;
  return mod === 0 || mod === 1 ? "0" : String(11 - mod);
}

function random8() {
  return Math.floor(10000000 + Math.random() * 90000000).toString();
}

/* =========================================================
   GERAÇÃO DE CHAVES
========================================================= */

function gerarChave({ cUF, anoMes, CNPJ, modelo, serie, numero }) {
  const tpEmis = "1";
  const cod = random8();
  const base43 =
    cUF +
    anoMes +
    CNPJ +
    modelo +
    serie.padStart(3, "0") +
    numero.padStart(9, "0") +
    tpEmis +
    cod;

  return base43 + calcDV(base43);
}

/* =========================================================
   FUNÇÃO PRINCIPAL — BOTÃO
========================================================= */

async function gerar() {
  let cte = await loadXML("base/cte_base.xml");
  let mdfe = await loadXML("base/mdfe_base.xml");

  // limpar protocolos / assinaturas
  cte = removeBlock(cte, "Signature");
  cte = removeBlock(cte, "protCTe");
  mdfe = removeBlock(mdfe, "Signature");
  mdfe = removeBlock(mdfe, "protMDFe");

  // sequências
  const nCT = await nextNumero("CTE");
  const nMDF = await nextNumero("MDFE");
  const nNFE = await nextNumero("NFE");

  // dados base do XML
  const cUF = cte.match(/<cUF>(\d+)<\/cUF>/)[1];
  const CNPJ = cte.match(/<CNPJ>(\d+)<\/CNPJ>/)[1];
  const anoMes = cte.match(/<dhEmi>(\d{4})-(\d{2})/);
  const aamm = anoMes[1].slice(2) + anoMes[2];

  // chaves
  const chaveCTe = gerarChave({
    cUF,
    anoMes: aamm,
    CNPJ,
    modelo: "57",
    serie: "1",
    numero: nCT
  });

  const chaveMDFe = gerarChave({
    cUF,
    anoMes: aamm,
    CNPJ,
    modelo: "58",
    serie: "22",
    numero: nMDF
  });

  // aplicar CT-e
  cte = replaceTag(cte, "nCT", nCT);
  cte = replaceTag(cte, "chCTe", chaveCTe);
  cte = replaceKey(cte, "CTe", chaveCTe);

  // aplicar NF-e (se existir)
  cte = replaceTag(cte, "chave", gerarChave({
    cUF,
    anoMes: aamm,
    CNPJ,
    modelo: "55",
    serie: "1",
    numero: nNFE
  }));

  // aplicar MDF-e
  mdfe = replaceTag(mdfe, "nMDF", nMDF);
  mdfe = replaceTag(mdfe, "chCTe", chaveCTe);
  mdfe = replaceKey(mdfe, "MDFe", chaveMDFe);

  // ZIP
  const zip = new JSZip();
  zip.file("CTe_NOVO.xml", cte);
  zip.file("MDFe_NOVO.xml", mdfe);

  const blob = await zip.generateAsync({ type: "blob" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "cte_mdfe.zip";
  a.click();
}
