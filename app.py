from flask import Flask, render_template, request, send_file, jsonify
from utils.xml_generator import gerar_novos_xmls
import os
import uuid
import zipfile
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp_xmls'

# Criar pasta temporária se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar-xmls', methods=['POST'])
def gerar_xmls():
    try:
        # Receber dados do formulário
        dados = {
            'novo_numero_cte': request.form.get('novo_numero_cte'),
            'nova_chave_cte': request.form.get('nova_chave_cte'),
            'novo_numero_mdfe': request.form.get('novo_numero_mdfe'),
            'nova_chave_mdfe': request.form.get('nova_chave_mdfe'),
            'chave_nfe_vinculada': request.form.get('chave_nfe_vinculada'),
            'data_emissao': request.form.get('data_emissao') or datetime.now().strftime('%Y-%m-%dT%H:%M:%S-03:00'),
            'data_vencimento': request.form.get('data_vencimento')
        }
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['novo_numero_cte', 'nova_chave_cte', 'novo_numero_mdfe', 'nova_chave_mdfe']
        for campo in campos_obrigatorios:
            if not dados[campo]:
                return jsonify({'error': f'Campo {campo} é obrigatório'}), 400
        
        # Gerar IDs únicos para os arquivos
        id_processo = str(uuid.uuid4())[:8]
        
        # Gerar novos XMLs
        arquivos = gerar_novos_xmls(dados, id_processo)
        
        # Criar arquivo ZIP com os dois XMLs
        zip_filename = f'xmls_viagem_{id_processo}.zip'
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for arquivo in arquivos:
                zipf.write(arquivo, os.path.basename(arquivo))
        
        # Retornar o arquivo ZIP para download
        return send_file(zip_path, 
                        as_attachment=True, 
                        download_name=zip_filename,
                        mimetype='application/zip')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/limpar-temp', methods=['POST'])
def limpar_temp():
    """Limpar arquivos temporários"""
    try:
        import shutil
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
            os.makedirs(app.config['UPLOAD_FOLDER'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
