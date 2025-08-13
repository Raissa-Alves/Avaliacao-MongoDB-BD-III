from conexaoAtlas import MongoDBConnection
from bson import ObjectId
import re

def formatar_preco(preco):
    """Função auxiliar para formatar o preço corretamente"""
    try:
        # Se for string, tenta converter para float
        if isinstance(preco, str):
            preco = float(preco.replace(',', '.'))
        
        # Formata com 2 casas decimais
        return f"R${float(preco):.2f}"
    except (ValueError, TypeError):
        return "R$0.00"

def cardapio_find():
    """Função principal de busca no cardápio"""
    try:
        db = MongoDBConnection().get_database("Restaurante")
        colecao = db["cardapio"]
        
        while True:
            print("\n" + "="*50)
            print("SISTEMA DE BUSCA DE CARDÁPIO".center(50))
            print("="*50)
            print("1. Buscar por nome do item")
            print("2. Buscar por categoria")
            print("3. Sair")
            print("="*50)
            
            opcao = input("Selecione o tipo de busca (1-3): ").strip()
            
            if opcao == "3":
                print("Saindo do sistema de busca...")
                break
                
            resultados = []
            
            if opcao == "1":
                termo = input("Digite o nome do item: ").strip()
                if not termo:
                    print("Erro: Nome não pode ser vazio!")
                    continue
                regex = re.compile(termo, re.IGNORECASE)
                resultados = list(colecao.find({"item": regex}))
                
            elif opcao == "2":
                termo = input("Digite a categoria: ").strip()
                if not termo:
                    print("Erro: Categoria não pode ser vazia!")
                    continue
                regex = re.compile(termo, re.IGNORECASE)
                resultados = list(colecao.find({"categoria": regex}))
                
            else:
                print("Opção inválida!")
                continue
                
            if not resultados:
                print("\nNenhum item encontrado.")
                continue
                
            print(f"\n{len(resultados)} iten(s) encontrado(s):")
            print("-"*50)
            
            for i, item in enumerate(resultados, 1):
                print(f"\nITEM {i}:")
                print(f"ID: {item['_id']}")
                print(f"Item: {item.get('item', 'Não informado')}")
                print(f"Preço: {formatar_preco(item.get('preço', 0))}")
                print(f"Descrição: {item.get('descricao', 'Não informada')}")
                
                cats = item.get('categoria', [])
                print("Categorias:", ", ".join(cats) if isinstance(cats, list) else cats)
                
                print("-"*50)
            
            input("\nPressione Enter para continuar...")
            
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == '__main__':
    cardapio_find()