import xml.etree.ElementTree as ET
from pathlib import Path
import zipfile
import argparse
import re

def strip_ns(tag):
    return tag.split('}', 1)[-1]

def remove_nodes(root, tags):
    for elem in list(root.iter()):
        if strip_ns(elem.tag) in tags:
            parent = root.find(".//" + elem.tag + "/..")
            if parent is not None:
                parent.remove(elem)

def replace_text(root, tag_name, new_value):
    for elem in root.iter():
        if strip_ns(elem.tag) == tag_name:
            elem.text = str(new_value)

def replace_attribute(root, tag_name, attr, new_value):
    for elem in root.iter():
        if strip_ns(elem.tag) == tag_name and attr in elem.attrib:
            elem.attrib[attr] = new_value

def generate_pair(args):
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    # ===== CTe =====
    cte_tree = ET.parse(args.cte)
    cte_root = cte_tree.getroot()

    remove_nodes(cte_root, ["Signature", "protCTe"])

    replace_text(cte_root, "nCT", args.nCT)
    replace_text(cte_root, "chave", args.chNFe)
    replace_text(cte_root, "chCTe", args.chCTe)
    replace_attribute(cte_root, "infCte", "Id", "CTe" + args.chCTe)

    cte_path = out_dir / "CTe_NOVO.xml"
    cte_tree.write(cte_path, encoding="utf-8", xml_declaration=True)

    # ===== MDFe =====
    mdfe_tree = ET.parse(args.mdfe)
    mdfe_root = mdfe_tree.getroot()

    remove_nodes(mdfe_root, ["Signature", "protMDFe"])

    replace_text(mdfe_root, "nMDF", args.nMDF)
    replace_text(mdfe_root, "chCTe", args.chCTe)
    replace_text(mdfe_root, "chMDFe", args.chMDFe)
    replace_attribute(mdfe_root, "infMDFe", "Id", "MDFe" + args.chMDFe)

    mdfe_path = out_dir / "MDFe_NOVO.xml"
    mdfe_tree.write(mdfe_path, encoding="utf-8", xml_declaration=True)

    # ===== ZIP =====
    with zipfile.ZipFile(args.zip, "w") as z:
        z.write(cte_path, cte_path.name)
        z.write(mdfe_path, mdfe_path.name)

    print("✔ XMLs gerados e ZIP criado com sucesso")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cte", required=True)
    parser.add_argument("--mdfe", required=True)
    parser.add_argument("--out", default="output")
    parser.add_argument("--zip", default="output/par_xml.zip")
    parser.add_argument("--chNFe", required=True)
    parser.add_argument("--nCT", required=True)
    parser.add_argument("--chCTe", required=True)
    parser.add_argument("--nMDF", required=True)
    parser.add_argument("--chMDFe", required=True)

    args = parser.parse_args()
    generate_pair(args)
