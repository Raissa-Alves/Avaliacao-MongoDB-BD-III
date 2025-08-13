import argparse
from conexaoAtlas import MongoDBConnection
from bson import ObjectId
from bson.errors import InvalidId
import sys

def deletar_documento(collection_name: str, document_id: str):

    colecoes_validas = ["clientes", "pedido", "cardapio", "reserva"]
    
    if collection_name not in colecoes_validas:
        print(f"Erro: Coleção inválida! Coleções permitidas: {', '.join(colecoes_validas)}")
        return False

    try:
        db = MongoDBConnection().get_database("Restaurante")
        colecao = db[collection_name]

        try:
            obj_id = ObjectId(document_id)
        except InvalidId:
            print("Erro: Formato de ID inválido!")
            print("O ID deve ser um ObjectId válido (ex: 507f1f77bcf86cd799439011)")
            return False
        
        documento = colecao.find_one({"_id": obj_id})
        if not documento:
            print("Documento não encontrado!")
            return False
            
        print(f"\nDocumento encontrado na coleção '{collection_name}':")
        
        if collection_name == "clientes":
            print(f"Nome: {documento.get('nome', 'Não informado')}")
            print(f"Email: {documento.get('email', 'Não informado')}")
        elif collection_name == "pedido":
            print(f"Número: {documento.get('numero_pedido', 'Não informado')}")
            print(f"Cliente: {documento.get('cliente_id', 'Não informado')}")
        elif collection_name == "cardapio":
            print(f"Item: {documento.get('nome_item', 'Não informado')}")
            print(f"Preço: R${documento.get('preco', 'Não informado')}")
        elif collection_name == "reserva":
            print(f"Data: {documento.get('data_reserva', 'Não informado')}")
            print(f"Mesa: {documento.get('numero_mesa', 'Não informado')}")
        
        confirmacao = input("\nTem certeza que deseja deletar este documento? (s/n): ")
        if confirmacao.lower() != 's':
            print("Operação cancelada pelo usuário")
            return False
        
        result = colecao.delete_one({"_id": obj_id})
        
        if result.deleted_count == 1:
            print("Documento deletado com sucesso!")
            return True
        else:
            print("Erro ao deletar documento (não encontrado após confirmação)")
            return False
            
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Deletar documentos do banco de dados',
        usage='python %(prog.py [coleção] [ID_DOCUMENTO]'
    )
    parser.add_argument(
        'collection',
        nargs='?',
        help='Nome da coleção (clientes, pedido, cardapio, reserva)'
    )
    parser.add_argument(
        'document_id',
        nargs='?',
        help='ID do documento a ser deletado'
    )
    
    if len(sys.argv) == 1:
        print("Modo interativo ativado")
        print("-----------------------")
        print("Coleções disponíveis: clientes, pedido, cardápio, reserva")
        collection = input("Digite o nome da coleção: ")
        document_id = input("Digite o ID do documento: ")
        deletar_documento(collection, document_id)
    else:
        args = parser.parse_args()
        deletar_documento(args.collection, args.document_id)
        