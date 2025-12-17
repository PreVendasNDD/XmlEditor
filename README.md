# CT-e / MDF-e XML Generator

Geração automática de pares XML CT-e + MDF-e **sem emissão**.

## Como usar

1. Coloque seus XMLs padrão em `/templates`
2. Rode:

```bash
python generator.py \
 --cte templates/cte_template.xml \
 --mdfe templates/mdfe_template.xml \
 --chNFe 123... \
 --nCT 1001 \
 --chCTe 4123... \
 --nMDF 2001 \
 --chMDFe 4123...
