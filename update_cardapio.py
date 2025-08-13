import argparse
from conexaoAtlas import MongoDBConnection
from bson import ObjectId
from bson.errors import InvalidId
import sys

def cardapio_updateinfo(document_id: str):
    try:
        db = MongoDBConnection().get_database("Restaurante")
        colecao = db["cardapio"]
        
        # Validação do ID
        try:
            obj_id = ObjectId(document_id)
        except InvalidId:
            print("Erro: ID inválido! Deve ser um ObjectId (ex: 507f1f77bcf86cd799439011)")
            return False
        
        # Busca documento
        documento = colecao.find_one({"_id": obj_id})
        if not documento:
            print("Item não encontrado!")
            return False
            
        # Exibe dados atuais
        print("\nDados atuais:")
        print(f"ID: {documento['_id']}")
        print(f"Nome: {documento.get('nome_item',)}")
        print(f"Preço: R${documento.get('preco')}")
        print(f"Descrição: {documento.get('descricao_item')}")
        print(f"Categorias: {', '.join(documento.get('categoria'))}")
        
        # Menu de atualização
        print("\nOpções de atualização:")
        print("1. Atualizar Nome")
        print("2. Atualizar Preço")
        print("3. Atualizar Descrição")
        print("4. Atualizar Categorias (substituir todas)")
        
        opcao = input("\nEscolha uma opção (1-4): ")
        
        # Processa escolha
        campos_validos = {
            "1": "nome_item",
            "2": "preco",
            "3": "descricao_item",
            "4": "categoria"
        }
        
        if opcao not in campos_validos:
            print("Opção inválida!")
            return False
            
        campo = campos_validos[opcao]
        novo_valor = input(f"\nNovo valor para '{campo}': ").strip()
        
        # Validações específicas
        if campo == "preco":
            try:
                novo_valor = float(novo_valor)
            except ValueError:
                print("Erro: Preço deve ser um número (ex: 29.99)")
                return False
        elif campo == "categoria":
            novo_valor = [cat.strip() for cat in novo_valor.split(",") if cat.strip()]
        
        # Confirmação
        print(f"\nConfirmar atualização:")
        print(f"Campo: {campo}")
        print(f"Novo valor: {novo_valor}")
        if input("\nConfirmar? (s/n): ").lower() != 's':
            print("Cancelado!")
            return False
        
        # Executa update
        result = colecao.update_one(
            {"_id": obj_id},
            {"$set": {campo: novo_valor}}
        )
        
        if result.modified_count == 1:
            print("Item atualizado com sucesso!")
            return True
        else:
            print("Nenhuma alteração realizada (possíveis dados idênticos)")
            return False
            
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Atualiza itens do cardápio')
    parser.add_argument('document_id', nargs='?', help='ID do item (ObjectId)')
    
    args = parser.parse_args()
    
    if not args.document_id:
        print("Modo interativo ativado")
        document_id = input("ID do item: ")
        cardapio_updateinfo(document_id)
    else:
        cardapio_updateinfo(args.document_id)