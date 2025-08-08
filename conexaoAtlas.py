from pymongo import MongoClient
import ssl

class MongoDBConnection:
    _client = None
    def __init__(self):
        if MongoDBConnection._client is None:
            try:
                uri = "mongodb+srv://caang2024119tads0024:12345@cluster0.ovf7cvj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
                
                # 2. Configuração especial para resolver o problema de ssl
                self.client = MongoClient(
                    uri,
                    tls=True,  # Habilita TLS/SSL
                    tlsAllowInvalidCertificates=True,  # Ignora erros de certificado (APENAS PARA DESENVOLVIMENTO)
                    connectTimeoutMS=30000,  # Aumenta o timeout
                    socketTimeoutMS=30000,
                    serverSelectionTimeoutMS=30000
                )
                
                # 3. Teste de conexão
                self.client.admin.command('ping')
                print("Conexão com MongoDB Atlas estabelecida com sucesso!")
                
            except Exception as e:
                print(f"Falha na conexão: {str(e)}")
                raise
    
    def get_database(self, db_name):
        """Retorna uma referência para o banco de dados especificado"""
        return self.client[db_name]
    
    @classmethod
    def close_connection(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            print("Conexão fechada.")
