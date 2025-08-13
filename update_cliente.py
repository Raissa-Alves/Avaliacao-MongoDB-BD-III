import argparse
from conexaoAtlas import MongoDBConnection
from bson import ObjectId
from bson.errors import InvalidId
import sys

def cliente_updateinfo(document_id: str):
    """
    Atualiza informações de um cliente
    """
    try:
        db = MongoDBConnection().get_database("Restaurante")
        colecao = db["clientes"]

        try:
            obj_id = ObjectId(document_id)
        except InvalidId:
            print("Erro: Formato de ID inválido!")
            print("O ID deve ser um ObjectId válido (ex: 507f1f77bcf86cd799439011)")
            return False
        
        print(f"\nBuscando cliente por ID: {obj_id}")
        print(f"Total de clientes na coleção: {colecao.count_documents({})}")

        documento = colecao.find_one({"_id": obj_id})
        if not documento:
            print("Cliente não encontrado!")
            return False
            
        print("\nCliente encontrado:")
        print(f"ID: {documento['_id']}")
        print(f"Nome: {documento.get('nome', 'Não informado')}")
        print(f"Email: {documento.get('email', 'Não informado')}")
        print(f"Telefones: {', '.join(documento.get('telefone', []))}")
        print("Endereços:")
        for i, endereco in enumerate(documento.get('Endereco', []), 1):
            print(f"  {i} - {endereco.get('rua', '')}, {endereco.get('bairro', '')} - {endereco.get('complemento', '')}")
        
        print("\nOpções de atualização:")
        print("1 - Atualizar nome")
        print("2 - Atualizar email")
        print("3 - Adicionar telefone")
        print("4 - Adicionar endereço")
        print("5 - Atualizar endereço existente")
        
        opcao = input("Digite o número da opção (1-5): ")
        
        update_data = {}
        
        if opcao == "1":
            novo_nome = input("Digite o novo nome: ").strip()
            if novo_nome:
                update_data = {"$set": {"nome": novo_nome}}
        
        elif opcao == "2":
            novo_email = input("Digite o novo email: ").strip()
            if novo_email:
                update_data = {"$set": {"email": novo_email}}
        
        elif opcao == "3":
            novo_telefone = input("Digite o novo telefone para adicionar: ").strip()
            if novo_telefone:
                update_data = {"$push": {"telefone": novo_telefone}}
        
        elif opcao == "4":
            print("\nNovo endereço:")
            rua = input("Rua: ").strip()
            bairro = input("Bairro: ").strip()
            complemento = input("Complemento: ").strip()
            
            if rua and bairro:  # Pelo menos rua e bairro são obrigatórios
                novo_endereco = {
                    "rua": rua,
                    "bairro": bairro,
                    "complemento": complemento
                }
                update_data = {"$push": {"Endereco": novo_endereco}}
            else:
                print("Erro: Rua e bairro são obrigatórios!")
                return False
        
        elif opcao == "5":
            enderecos = documento.get("Endereco", [])
            if not enderecos:
                print("Cliente não tem endereços para atualizar!")
                return False
            
            print("\nEndereços existentes:")
            for i, endereco in enumerate(enderecos, 1):
                print(f"{i} - {endereco.get('rua', '')}, {endereco.get('bairro', '')}")
            
            try:
                indice = int(input("Digite o número do endereço a atualizar: ")) - 1
                if indice < 0 or indice >= len(enderecos):
                    raise ValueError
                
                print("\nDeixe em branco para manter o valor atual")
                rua = input(f"Rua [{enderecos[indice].get('rua', '')}]: ").strip() or enderecos[indice].get('rua', '')
                bairro = input(f"Bairro [{enderecos[indice].get('bairro', '')}]: ").strip() or enderecos[indice].get('bairro', '')
                complemento = input(f"Complemento [{enderecos[indice].get('complemento', '')}]: ").strip() or enderecos[indice].get('complemento', '')
                
                update_data = {
                    "$set": {
                        f"Endereco.{indice}.rua": rua,
                        f"Endereco.{indice}.bairro": bairro,
                        f"Endereco.{indice}.complemento": complemento
                    }
                }
            except ValueError:
                print("Erro: Número de endereço inválido!")
                return False
        else:
            print("Opção inválida!")
            return False
        
        if not update_data:
            print("Nenhuma alteração foi especificada!")
            return False
            
        confirmacao = input("\nTem certeza que deseja atualizar este cliente? (s/n): ")
        if confirmacao.lower() != 's':
            print("Operação cancelada pelo usuário")
            return False
        
        result = colecao.update_one({"_id": obj_id}, update_data)
        
        if result.modified_count == 1:
            print("\nCliente atualizado com sucesso!")
            return True
        else:
            print("\nNenhuma modificação foi realizada (possivelmente os dados são iguais aos existentes)")
            return False
            
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Atualizar informações de clientes',
        usage='python %(prog.py [ID_DOCUMENTO]'
    )
    parser.add_argument(
        'document_id',
        nargs='?',
        help='ID do cliente a ser atualizado'
    )
    
    if len(sys.argv) == 1:
        print("Modo interativo ativado")
        print("-----------------------")
        document_id = input("Digite o ID do cliente: ")
        cliente_updateinfo(document_id)
    else:
        args = parser.parse_args()
        cliente_updateinfo(args.document_id)