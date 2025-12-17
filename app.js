const byId = id => document.getElementById(id);

function readFile(file){
  return new Promise(res=>{
    const r = new FileReader();
    r.onload = () => res(r.result);
    r.readAsText(file);
  });
}

function removeBlocks(xml, names){
  names.forEach(n=>{
    const re = new RegExp(`<${n}[\\s\\S]*?<\\/${n}>`,'g');
    xml = xml.replace(re,'');
  });
  return xml;
}

function replaceTag(xml, tag, value){
  if(!value) return xml;
  const re = new RegExp(`<${tag}>([\\s\\S]*?)<\\/${tag}>`,'g');
  return xml.replace(re, `<${tag}>${value}</${tag}>`);
}

function replaceId(xml, root, prefix, value){
  if(!value) return xml;
  const re = new RegExp(`<${root}([^>]*?)Id="[^"]+"`,'g');
  return xml.replace(re, `<${root}$1Id="${prefix}${value}"`);
}

byId("generate").onclick = async () => {
  const cteF = byId("cteFile").files[0];
  const mdfeF = byId("mdfeFile").files[0];
  if(!cteF || !mdfeF) return alert("Selecione CT-e e MDF-e");

  let cte = await readFile(cteF);
  let mdfe = await readFile(mdfeF);

  cte = removeBlocks(cte, ["Signature","protCTe"]);
  mdfe = removeBlocks(mdfe, ["Signature","protMDFe"]);

  cte = replaceTag(cte,"nCT",byId("nCT").value);
  cte = replaceTag(cte,"chCTe",byId("chCTe").value);
  cte = replaceTag(cte,"chave",byId("chNFe").value);
  cte = replaceId(cte,"infCte","CTe",byId("chCTe").value);

  mdfe = replaceTag(mdfe,"nMDF",byId("nMDF").value);
  mdfe = replaceTag(mdfe,"chCTe",byId("chCTe").value);
  mdfe = replaceTag(mdfe,"chMDFe",byId("chMDFe").value);
  mdfe = replaceId(mdfe,"infMDFe","MDFe",byId("chMDFe").value);

  const zip = new JSZip();
  zip.file("CTe_NOVO.xml", cte);
  zip.file("MDFe_NOVO.xml", mdfe);
  const blob = await zip.generateAsync({type:"blob"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "par_cte_mdfe.zip";
  a.click();
};
