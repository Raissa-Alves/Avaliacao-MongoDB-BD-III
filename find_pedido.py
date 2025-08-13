from conexaoAtlas import MongoDBConnection
from bson import ObjectId
from bson.errors import InvalidId
import re

def pedido_find():
    """
    Função interativa para busca de pedidos por:
    1. client_id (armazenado como string)
    2. forma_de_pagamento
    """
    try:
        db = MongoDBConnection().get_database("Restaurante")
        colecao = db["pedidos"]
        
        while True:
            print("\n" + "="*50)
            print("SISTEMA DE BUSCA DE PEDIDOS")
            print("="*50)
            print("1. Buscar por client_id")
            print("2. Buscar por forma de pagamento")
           
            print("3. Sair")
            print("="*50)
            
            opcao = input("Selecione o tipo de busca (1-3): ").strip()
            
            if opcao == "3":
                print("Saindo do sistema de busca de pedidos...")
                break
                
            resultados = []
            
            if opcao == "1":  # Busca por client_id (string)
                termo_busca = input("Digite o ID do cliente: ").strip()
                if not termo_busca:
                    print("Erro: ID do cliente não pode estar vazio!")
                    continue
                    
                try:
                    # Valida se é um ObjectId válido (mesmo armazenado como string)
                    obj_id = ObjectId(termo_busca)
                    # Converte para string na consulta
                    resultados = list(colecao.find({"cliente_id": str(obj_id)}))
                except InvalidId:
                    print("Erro: ID do cliente inválido! Deve ser um ObjectId de 24 caracteres hexadecimais.")
                    continue
                    
            elif opcao == "2":  # Busca por forma de pagamento
                termo_busca = input("Digite a forma de pagamento: ").strip()
                if not termo_busca:
                    print("Erro: Forma de pagamento não pode estar vazia!")
                    continue
                    
                regex = re.compile(termo_busca, re.IGNORECASE)
                resultados = list(colecao.find({"pagamento": regex}))
                
        
                
            else:
                print("Opção inválida! Tente novamente.")
                continue
                
            if not resultados:
                print("\nNenhum pedido encontrado com esses critérios.")
                continue
                
            print(f"\n{len(resultados)} pedido(s) encontrado(s):")
            print("-" * 50)
            
            for i, pedido in enumerate(resultados, 1):
                print(f"\nPEDIDO {i}:")
                print(f"ID: {pedido['_id']}")
                print(f"Cliente ID: {pedido.get('cliente_id')}")
                
                # Itens e quantidades
                itens_ids = pedido.get('item_id', [])
                quantidades = pedido.get('quantidade', [])
                
                print("Itens do pedido:")
                if itens_ids:
                    for idx, item_id in enumerate(itens_ids):
                        qtd = quantidades[idx] if idx < len(quantidades) else "Quantidade não informada"
                        print(f" - Item ID: {item_id}, Quantidade: {qtd}")
                else:
                    print(" - Nenhum item encontrado")
                
                print(f"Forma de pagamento: {pedido.get('pagamento', 'Não informada')}")
                print(f"Observações: {pedido.get('observacoes', 'Nenhuma')}")
                print("-" * 50)
            
            input("\nPressione Enter para continuar...")
            
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")

if __name__ == '__main__':
    pedido_find()