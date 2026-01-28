# database/db_factory.py
from .database_manager import SQLiteDatabaseManager


class DatabaseFactory:
    """
    Classe responsável por instanciar o banco de dados correto.
    Se no futuro você adicionar MySQL, a lógica de escolha fica aqui.
    O nome padrão está "sqlite" mas se no futuro for colocar outro banco de dado
    será necessário mudar o db_type
    """

    @staticmethod
    def get_database(db_type="sqlite"):
        if db_type.lower() == "sqlite":
            return SQLiteDatabaseManager()

        # Se você tivesse outro banco:
        # elif db_type.lower() == "mysql":
        #     return MySQLDatabaseManager()

        raise ValueError(f"Tipo de banco de dados '{db_type}' não suportado.")