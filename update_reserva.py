import argparse
from conexaoAtlas import MongoDBConnection
from bson import ObjectId
from bson.errors import InvalidId
import sys

def reserva_updateinfo(document_id: str):
    """
    Atualiza serviços adicionais de uma reserva
    """
    try:
        db = MongoDBConnection().get_database("Restaurante")
        colecao = db["reserva"]

        try:
            obj_id = ObjectId(document_id)
        except InvalidId:
            print("Erro: Formato de ID inválido!")
            print("O ID deve ser um ObjectId válido (ex: 507f1f77bcf86cd799439011)")
            return False
        
        
        print(f"Buscando por ID: {obj_id} (tipo: {type(obj_id)})")
        print(f"Total de documentos na coleção: {colecao.count_documents({})}")

        documento = colecao.find_one({"_id": obj_id})
        if not documento:
            print("Reserva não encontrada!")
            return False
            
        print("\nReserva encontrada:")
        print(f"ID: {documento['_id']}")
        print(f"Data: {documento.get('data_reserva', 'Não informada')}")
        print(f"Mesa: {documento.get('numero_mesa', 'Não informado')}")
        print(f"Serviços Adicionais: {', '.join(documento.get('servicos_adicionais', []))}")
        
        print("\nOpções para serviços adicionais:")
        print("1 - Adicionar novo serviço (push)")
        print("2 - Substituir um serviço existente (set)")
        
        opcao = input("Digite o número da opção (1-2): ")
        
        update_data = {}
        
        if opcao == "1":
            novo_servico = input("Digite o novo serviço para adicionar: ").strip()
            if novo_servico:
                update_data = {"$push": {"servicos_adicionais": novo_servico}}
        
        elif opcao == "2":
            servicos = documento.get("servicos_adicionais", [])
            if not servicos:
                print("Reserva não tem serviços para substituir!")
                return False
            
            print("\nServiços existentes:")
            for i, servico in enumerate(servicos, 1):
                print(f"{i} - {servico}")
            
            try:
                indice = int(input("Digite o número do serviço a substituir: ")) - 1
                if indice < 0 or indice >= len(servicos):
                    raise ValueError
                
                novo_servico = input("Digite o novo serviço: ").strip()
                if novo_servico:
                    update_data = {"$set": {f"servicos_adicionais.{indice}": novo_servico}}
            except ValueError:
                print("Erro: Número de serviço inválido!")
                return False
        else:
            print("Opção inválida!")
            return False
        
        if not update_data:
            print("Nenhum serviço foi especificado!")
            return False
            
        confirmacao = input("\nTem certeza que deseja atualizar esta reserva? (s/n): ")
        if confirmacao.lower() != 's':
            print("Operação cancelada pelo usuário")
            return False
        
        result = colecao.update_one({"_id": obj_id}, update_data)
        
        if result.modified_count == 1:
            print("Reserva atualizada com sucesso!")
            return True
        else:
            print("Nenhuma modificação foi realizada (possivelmente os dados são iguais aos existentes)")
            return False
            
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Atualizar serviços adicionais de reservas',
        usage='python %(prog.py [ID_DOCUMENTO]'
    )
    parser.add_argument(
        'document_id',
        nargs='?',
        help='ID da reserva a ser atualizada'
    )
    
    if len(sys.argv) == 1:
        print("Modo interativo ativado")
        print("-----------------------")
        document_id = input("Digite o ID da reserva: ")
        reserva_updateinfo(document_id)
    else:
        args = parser.parse_args()
        reserva_updateinfo(args.document_id)