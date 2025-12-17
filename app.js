async function carregarXML(path) {
  const res = await fetch(path);
  return await res.text();
}

function removerBloco(xml, tag) {
  const re = new RegExp(`<${tag}[\\s\\S]*?<\\/${tag}>`, "g");
  return xml.replace(re, "");
}

function substituir(xml, tag, valor) {
  if (!valor) return xml;
  const re = new RegExp(`<${tag}>[\\s\\S]*?<\\/${tag}>`, "g");
  return xml.replace(re, `<${tag}>${valor}</${tag}>`);
}

function substituirId(xml, prefixo, valor) {
  const re = new RegExp(`${prefixo}[0-9]{44}`, "g");
  return xml.replace(re, prefixo + valor);
}

async function gerar() {
  let cte = await carregarXML("base/cte_base.xml");
  let mdfe = await carregarXML("base/mdfe_base.xml");

  // limpar assinatura / protocolo
  cte = removerBloco(cte, "Signature");
  cte = removerBloco(cte, "protCTe");

  mdfe = removerBloco(mdfe, "Signature");
  mdfe = removerBloco(mdfe, "protMDFe");

  // substituições CTe
  cte = substituir(cte, "nCT", nCT.value);
  cte = substituir(cte, "chave", chNFe.value);
  cte = substituirId(cte, "CTe", chCTe.value);
  cte = substituir(cte, "chCTe", chCTe.value);

  // substituições MDFe
  mdfe = substituir(mdfe, "nMDF", nMDF.value);
  mdfe = substituirId(mdfe, "MDFe", chMDFe.value);
  mdfe = substituir(mdfe, "chMDFe", chMDFe.value);
  mdfe = substituir(mdfe, "chCTe", chCTe.value);

  const zip = new JSZip();
  zip.file("CTe_NOVO.xml", cte);
  zip.file("MDFe_NOVO.xml", mdfe);

  const blob = await zip.generateAsync({ type: "blob" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "cte_mdfe.zip";
  a.click();
}
