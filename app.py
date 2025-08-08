from flask import Flask, request, jsonify, render_template
from conexaoAtlas import MongoDBConnection
from datetime import datetime

app = Flask(__name__)
db = MongoDBConnection()  # Esta conexão será mantida

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/insert', methods=['POST'])
def insert_document():
    try:
        data = request.get_json()
        print("Dados recebidos:", data)
        
        collection = db.get_database("Restaurante")["clientes"]
        data['data_cadastro'] = datetime.now()
        
        result = collection.insert_one(data)
        print("Documento inserido com ID:", result.inserted_id)
        
        return jsonify({
            "status": "success",
            "inserted_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        print("Erro na inserção:", str(e))
        return jsonify({
            "status": "error",
            "message": "Erro no servidor"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)