from conexaoAtlas import MongoDBConnection
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import re

def reserva_find():
    """
    Função interativa para busca de reservas por:
    1. id_cliente
    2. serviços adicionais
    3. local com número mínimo de pessoas
    """
    try:
        db = MongoDBConnection().get_database("Restaurante")
        colecao = db["reservas"]
        
        while True:
            print("\n" + "="*50)
            print("SISTEMA DE BUSCA DE RESERVAS")
            print("="*50)
            print("1. Buscar por ID do cliente")
            print("2. Buscar por serviços adicionais")
            print("3. Buscar por local com número mínimo de pessoas")
            print("4. Sair")
            print("="*50)
            
            opcao = input("Selecione o tipo de busca (1-4): ").strip()
            
            if opcao == "4":
                print("Saindo do sistema de busca de reservas...")
                break
                
            resultados = []
            
            if opcao == "1":  # Busca por id_cliente (armazenado como string)
                termo_busca = input("Digite o ID do cliente: ").strip()
                if not termo_busca:
                    print("Erro: ID do cliente não pode estar vazio!")
                    continue
                    
                try:
                    obj_id = ObjectId(termo_busca)
                    resultados = list(colecao.find({"id_cliente": str(obj_id)}))
                except InvalidId:
                    print("Erro: ID do cliente inválido! Deve ser um ObjectId de 24 caracteres hexadecimais.")
                    continue
                    
            elif opcao == "2":  # Busca por serviços adicionais
                termo_busca = input("Digite o serviço adicional: ").strip()
                if not termo_busca:
                    print("Erro: Serviço adicional não pode estar vazio!")
                    continue
                    
                regex = re.compile(termo_busca, re.IGNORECASE)
                resultados = list(colecao.find({"Serviços adicionais": regex}))
                
            elif opcao == "3":  # Busca por local com mínimo de pessoas (string)
                local = input("Digite o local: ").strip()
                if not local:
                    print("Erro: Local não pode estar vazio!")
                    continue
                    
                try:
                    min_pessoas = int(input("Digite o número mínimo de pessoas: ").strip())
                    if min_pessoas < 1:
                        raise ValueError
                except ValueError:
                    print("Erro: Número de pessoas deve ser um inteiro positivo!")
                    continue
                    
                regex = re.compile(local, re.IGNORECASE)
                
                # Busca considerando que num_pessoas pode ser string ou número
                resultados = list(colecao.find({
                    "local": regex,
                    "$expr": {
                        "$gte": [
                            {"$toInt": "$num_pessoas"},  # Converte para inteiro
                            min_pessoas
                        ]
                    }
                }))
                
            else:
                print("Opção inválida! Tente novamente.")
                continue
                
            if not resultados:
                print("\nNenhuma reserva encontrada com esses critérios.")
                continue
                
            print(f"\n{len(resultados)} reserva(s) encontrada(s):")
            print("-" * 50)
            
            for i, reserva in enumerate(resultados, 1):
                print(f"\nRESERVA {i}:")
                print(f"ID: {reserva['_id']}")
                print(f"ID Cliente: {reserva.get('id_cliente')}")
                
                # Formatação da data/hora
                data_hora = reserva.get('data_hora')
                if data_hora:
                    if isinstance(data_hora, datetime):
                        data_formatada = data_hora.strftime("%d/%m/%Y %H:%M")
                    else:
                        data_formatada = str(data_hora)
                else:
                    data_formatada = "Não informada"
                    
                print(f"Data/Hora: {data_formatada}")
                
                # Tratamento para num_pessoas (pode ser string ou número)
                num_pessoas = reserva.get('num_pessoas')
                if isinstance(num_pessoas, str):
                    try:
                        num_pessoas = int(num_pessoas)
                    except ValueError:
                        pass
                print(f"Número de Pessoas: {num_pessoas}")
                
                print(f"Local: {reserva.get('local')}")
                
                # Serviços adicionais formatados corretamente
                servicos = reserva.get('Serviços adicionais', [])
                if servicos:
                    print("Serviços Adicionais:")
                    if isinstance(servicos, str):
                        print(f" - {servicos}")
                    elif isinstance(servicos, list):
                        # Verifica se é uma lista de caracteres individuais
                        if all(isinstance(item, str) and len(item) == 1 for item in servicos):
                            print(f" - {''.join(servicos)}")
                        else:
                            for servico in servicos:
                                print(f" - {servico}")
                else:
                    print("Serviços Adicionais: Nenhum")
                
                print("-" * 50)
            
            input("\nPressione Enter para continuar...")
            
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")

if __name__ == '__main__':
    reserva_find()