from flask import Flask, request, jsonify, render_template
from conexaoAtlas import MongoDBConnection
from datetime import datetime
import traceback
from bson.errors import InvalidId


app = Flask(__name__)
db = MongoDBConnection() 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cadastro_cliente')
def cadastro_cliente():
    return render_template('cadastro_cliente.html')

@app.route('/cadastro_cardapio')
def cadastro_cardapio():
    return render_template('cadastro_cardapio.html')

@app.route('/registrar_pedido')
def registrar_pedido():
    return render_template('registrar_pedido.html')

@app.route('/reserva_mesa')
def reserva_mesa():
    return render_template('reserva_mesa.html')

def validate_cliente_data(data):
    if not all(key in data for key in ['nome', 'email']):
        raise ValueError("Dados do cliente incompletos. São necessários nome e email.")
    
    structured_data = {
        'nome': data['nome'],
        'email': data['email'],
        'data_cadastro': datetime.now()
    }
    
    if 'telefone' in data:
        if isinstance(data['telefone'], list):
            structured_data['telefone'] = data['telefone']
        else:
            structured_data['telefone'] = [data['telefone']]
    
    endereco_fields = {}
    if 'rua' in data:
        endereco_fields['rua'] = data['rua']
    if 'bairro' in data:
        endereco_fields['bairro'] = data['bairro']
    if 'complemento' in data:
        endereco_fields['complemento'] = data['complemento']
    
    if endereco_fields:
        structured_data['Endereco'] = [endereco_fields]
    
    return structured_data

def validate_cardapio_data(data):
    print("Dados recebidos no validador:", data)  
    
    field_mapping = {
        'nome': 'item',
        'descricao': 'descrição',
        'preco': 'preço'
    }
    
    for html_field, db_field in field_mapping.items():
        if html_field in data:
            data[db_field] = data.pop(html_field)

    if 'item' not in data or not data['item'].strip():
        raise ValueError("O nome do item é obrigatório")
    
    if 'preço' not in data:
        raise ValueError("O preço do item é obrigatório")
    
    try:
        preco_str = str(data['preço']).replace('R$', '').replace('$', '').strip()
        
        preco = float(preco_str.replace(',', '.'))
        if preco <= 0:
            raise ValueError("O preço deve ser maior que zero")
        data['preço'] = preco  
    except (ValueError, TypeError):
        raise ValueError("Preço inválido. Use números (ex: 29.90 ou 29,90)")
    
    structured_data = {
        'item': data['item'].strip(),
        'preço': data['preço'],
        'data_cadastro': datetime.now()
    }
    
    if 'descrição' in data and data['descrição'].strip():
        structured_data['descrição'] = data['descrição'].strip()
    
    if 'categoria' in data and data['categoria']:
        if isinstance(data['categoria'], str):
            
            structured_data['categoria'] = [
                cat.strip() for cat in data['categoria'].split(',') 
                if cat.strip()
            ]
        elif isinstance(data['categoria'], list):
            structured_data['categoria'] = [
                cat.strip() for cat in data['categoria'] 
                if isinstance(cat, str) and cat.strip()
            ]
    
    print("Dados estruturados:", structured_data)  
    return structured_data

VALIDATORS = {
    'clientes': validate_cliente_data,
    'cardapio': validate_cardapio_data,
    
}

def insert_data(collection_name):
    try:
        data = request.get_json()
        print(f"Dados recebidos para {collection_name}:", data)
        
        if collection_name in VALIDATORS:
            data = VALIDATORS[collection_name](data)
        else:
            
            data['data_cadastro'] = datetime.now()
        
        collection = db.get_database("Restaurante")[collection_name]
        result = collection.insert_one(data)
        print(f"Documento inserido em {collection_name} com ID:", result.inserted_id)
        
        return jsonify({
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "collection": collection_name
        }), 201
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": "Dados inválidos",
            "details": str(e)
        }), 400
    except Exception as e:
        print("Erro na inserção:", str(e))
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": "Erro no servidor",
            "details": str(e)
        }), 500

@app.route('/insert/cliente', methods=['POST'])
def insert_cliente():
    return insert_data("clientes")

@app.route('/insert/cardapio', methods=['POST'])
def insert_cardapio():
    return insert_data("cardapio")

@app.route('/insert/pedido', methods=['POST'])
def insert_pedido():
    return insert_data("pedidos")

@app.route('/insert/reserva', methods=['POST'])
def insert_reserva():
    return insert_data("reservas")

@app.route('/view/<collection_name>')
def view_collection(collection_name):
    try:
        collection = db.get_database("Restaurante")[collection_name]
        data = list(collection.find().limit(50))
        
        for item in data:
            item['_id'] = str(item['_id'])
            if 'data_cadastro' in item and isinstance(item['data_cadastro'], datetime):
                item['data_cadastro'] = item['data_cadastro'].isoformat()
        
        return jsonify({
            "status": "success",
            "collection": collection_name,
            "count": len(data),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)