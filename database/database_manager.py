import sqlite3
import os
from .db_interface import DatabaseInterface
from .schemas import ALL_TABLES # Importa a lista centralizada

class SQLiteDatabaseManager(DatabaseInterface):

    def __init__(self, db_name='empresa_sanxi.db'):
        # 1. Configuração do Caminho (Flexibilida de)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(base_dir, 'data', db_name)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # 2. Conexão
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Permite acessar row['nome']
        self.cursor = self.connection.cursor()

        # 3. Inicialização Automática
        self.create_tables()
        print(f"Banco conectado em: {self.db_path}")

    def execute(self, query, params=None):
        """Implementação obrigatória da Interface: Executa comandos SQL"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()

            # MUDANÇA AQUI: Retornar o ID gerado (lastrowid)
            # Se for um UPDATE ou DELETE, ele retornará None ou 0, o que não afeta nada.
            return self.cursor.lastrowid

        except Exception as e:
            self.connection.rollback()
            raise e

    def fetch_one(self, query, params=None):
        """Implementação obrigatória: Busca um registro único"""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchone()

    def fetch_all(self, query, params=None):
        """Busca todos os registros de uma consulta"""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def obter_detalhes_tabela(self, nome_tabela):
        """Executa o comando que retorna a lista de colunas do SQLite"""
        query = f"PRAGMA table_info({nome_tabela});"
        # Usamos o fetch_all que já criamos para pegar a lista de dicionários
        return self.fetch_all(query)

    def close(self):
        """Implementação obrigatória: Fecha o banco com segurança"""
        if self.connection:
            self.connection.close()
            print("Conexão com SQLite encerrada.")

    def create_tables(self):
        """Varre todos os arquivos registrados e executa o SQL"""
        for sql in ALL_TABLES:
            self.cursor.executescript(sql)
            self.connection.commit()

    def listar_tabelas_reais(self):
        """Consulta o dicionário interno do SQLite para ver o que existe de facto"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        # Usamos o fetch_all em vez de acessar o cursor diretamente
        return self.fetch_all(query)