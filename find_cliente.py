from conexaoAtlas import MongoDBConnection
from bson import ObjectId
import re

def cliente_find():
    """
    Função interativa para busca de clientes por:
    1. Nome
    2. Bairro (no array de endereços)
    3. Número de telefone (no array de telefones)
    """
    try:
        db = MongoDBConnection().get_database("Restaurante")
        colecao = db["clientes"]
        
        while True:
            print("\n" + "="*50)
            print("SISTEMA DE BUSCA DE CLIENTES")
            print("="*50)
            print("1. Buscar por nome")
            print("2. Buscar por bairro")
            print("3. Buscar por telefone")
            print("4. Sair")
            print("="*50)
            
            opcao = input("Selecione o tipo de busca (1-4): ")
            
            if opcao == "4":
                print("Saindo do sistema de busca...")
                break
                
            termo_busca = input("Digite o termo de busca: ").strip()
            if not termo_busca:
                print("Erro: Termo de busca não pode estar vazio!")
                continue
                
            resultados = []
            
            if opcao == "1": # Busca por nome
                regex = re.compile(termo_busca, re.IGNORECASE)
                resultados = list(colecao.find({"nome": regex}))
                
            elif opcao == "2": # Busca por bairro
                regex = re.compile(termo_busca, re.IGNORECASE)
                resultados = list(colecao.find({"Endereco.bairro": regex}))
                
            elif opcao == "3": # Busca por telefone
                # Remove caracteres não numéricos para melhor busca
                numero_limpo = re.sub(r'\D', '', termo_busca)
                if numero_limpo:
                    regex = re.compile(f'.*{re.escape(numero_limpo)}.*')
                    resultados = list(colecao.find({"telefone": regex}))
                else:
                    print("Erro: Digite um número de telefone válido!")
                    continue
                    
            else:
                print("Opção inválida! Tente novamente.")
                continue
                
            if not resultados:
                print("\nNenhum cliente encontrado com esses critérios.")
                continue
                
            print(f"\n{len(resultados)} cliente(s) encontrado(s):")
            print("-" * 50)
            
            for i, cliente in enumerate(resultados, 1):
                print(f"\nCLIENTE {i}:")
                print(f"ID: {cliente['_id']}")
                print(f"Nome: {cliente.get('nome', 'Não informado')}")
                print(f"Email: {cliente.get('email', 'Não informado')}")
                
                # Telefones
                telefones = cliente.get('telefone', [])
                print("Telefones:")
                for tel in telefones:
                    print(f" - {tel}")
                
                # Endereços
                enderecos = cliente.get('Endereco', [])
                print("Endereços:")
                for end in enderecos:
                    print(f" - Rua: {end.get('rua', 'Não informada')}")
                    print(f" Bairro: {end.get('bairro', 'Não informado')}")
                    print(f" Complemento: {end.get('complemento', 'Não informado')}")
                
                print("-" * 50)
            
            input("\nPressione Enter para continuar...")
            
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")

if __name__ == '__main__':
    cliente_find()