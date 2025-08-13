from flask import Flask, request, jsonify, render_template
from conexaoAtlas import MongoDBConnection
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)
db = MongoDBConnection()

@app.route('/delete/<collction_name>/<documents_id>', methods=['DELETE'])
def deletar_documente(collection_name, document_id):
    try:
        colecoes_validas = ["clientes", "cardapio", "pedido", "reserva"]
        if collection_name not in colecoes_validas:
         return jsonify({
            "status": "erro!",
            "mensagem": "Coleção {collection_name} invalida!"
        }), 400
        
        colecao = db.get_database("Restaurante")[collection_name]
        
        from bson import ObjectId
        delete_documento = {"_id": ObjectId (document_id)}
        result = colecao.delete_one(delete_documento)
        
        if result.deleted_count == 1:
            return jsonify({
                "status": "success",
                "message": f"Documento {document_id} deletado com sucesso!",
                "collection": collection_name
            }), 200
            
        else:
            return jsonify({
                "status": "erro!",
                "message": f"Documento {document_id} não encontrado!"
            }), 404
            
    except Exception as e:
        print(f"Erro ao tentar deletar: {collection_name}", str(e))
        return jsonify({
            "status": "erro!",
            "message": f"Erro ao deletar documento!",
            "details": str(e)
        }), 500
            