import argparse
from conexaoAtlas import MongoDBConnection
from bson import ObjectId
from bson.errors import InvalidId
import sys
from datetime import datetime

def validar_pedido(data):
    """Valida os dados do pedido antes de inserir no banco"""
    required_fields = ['cliente_id', 'item_id', 'item_nome', 'quantidade', 'pagamento']
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Campo obrigatório faltando: {field}")
    
    if len(data['item_id']) != len(data['item_nome']) or len(data['item_id']) != len(data['quantidade']):
        raise ValueError("Número de itens, nomes e quantidades inconsistentes")
    
    try:
        cliente_id = ObjectId(data['cliente_id'])
    except InvalidId:
        raise ValueError("ID do cliente inválido")
    
    for i, item_id in enumerate(data['item_id']):
        try:
            ObjectId(item_id)
        except InvalidId:
            raise ValueError(f"ID do item {i+1} inválido")
        
        try:
            quantidade = int(data['quantidade'][i])
            if quantidade <= 0:
                raise ValueError(f"Quantidade do item {i+1} deve ser maior que zero")
        except ValueError:
            raise ValueError(f"Quantidade do item {i+1} inválida")

def processar_pedido(data):
    """Processa e registra um novo pedido no banco de dados"""
    try:
        db = MongoDBConnection().get_database("Restaurante")
        colecao_pedidos = db["pedidos"]
        colecao_clientes = db["clientes"]
        colecao_cardapio = db["cardapio"]

        # Validação inicial
        validar_pedido(data)

        # Verifica se cliente existe
        cliente_id = ObjectId(data['cliente_id'])
        if not colecao_clientes.find_one({"_id": cliente_id}):
            raise ValueError("Cliente não encontrado")

        # Processa itens do pedido
        itens = []
        total = 0.0
        
        for i in range(len(data['item_id'])):
            item_id = ObjectId(data['item_id'][i])
            item_nome = data['item_nome'][i]
            quantidade = int(data['quantidade'][i])
            
            # Busca preço no cardápio
            item_cardapio = colecao_cardapio.find_one({"_id": item_id})
            preco = item_cardapio['preco'] if item_cardapio else 0.0
            
            itens.append({
                "item_id": item_id,
                "item": item_nome,
                "quantidade": quantidade
            })
            
            total += preco * quantidade

        # Cria documento do pedido
        pedido = {
            "cliente_id": cliente_id,
            "data_pedido": datetime.now(),
            "itens": itens,
            "total": total,
            "pagamento": data['pagamento'],
            "observacoes": data.get('observacoes', ''),
            "status": "pendente"
        }

        # Insere no banco
        result = colecao_pedidos.insert_one(pedido)
        return result.inserted_id

    except Exception as e:
        raise ValueError(f"Erro ao processar pedido: {str(e)}")

def registrar_pedido():
    """Função principal para registrar pedido via linha de comando"""
    try:
        print("\n--- Registrar Novo Pedido ---")
        
        # Coleta dados do pedido
        data = {
            'cliente_id': input("ID do Cliente: ").strip(),
            'item_id': [],
            'item_nome': [],
            'quantidade': [],
            'pagamento': '',
            'observacoes': ''
        }

        # Coleta itens do pedido
        while True:
            print("\nItem do Pedido:")
            data['item_id'].append(input("ID do Item: ").strip())
            data['item_nome'].append(input("Nome do Item: ").strip())
            data['quantidade'].append(input("Quantidade: ").strip())
            
            if input("\nAdicionar outro item? (s/n): ").lower() != 's':
                break

        # Forma de pagamento
        print("\nFormas de pagamento disponíveis:")
        print("1 - Pix")
        print("2 - Cartão")
        print("3 - Em espécie")
        opcao_pagamento = input("Escolha a forma de pagamento (1-3): ").strip()
        
        if opcao_pagamento == '1':
            data['pagamento'] = 'Pix'
        elif opcao_pagamento == '2':
            data['pagamento'] = 'Cartão'
        elif opcao_pagamento == '3':
            data['pagamento'] = 'Em espécie'
        else:
            raise ValueError("Opção de pagamento inválida")

        # Observações
        data['observacoes'] = input("\nObservações (opcional): ").strip()

        # Processa pedido
        pedido_id = processar_pedido(data)
        print(f"\nPedido registrado com sucesso! ID: {pedido_id}")
        return True

    except ValueError as e:
        print(f"\nErro: {str(e)}")
        return False
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Registrar novo pedido',
        usage='python %(prog)s [--interativo]'
    )
    parser.add_argument(
        '--interativo',
        action='store_true',
        help='Modo interativo para registrar pedido'
    )
    
    args = parser.parse_args()
    
    if args.interativo:
        registrar_pedido()
    else:
        print("Use --interativo para registrar um novo pedido")