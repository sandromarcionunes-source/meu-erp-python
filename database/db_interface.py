from abc import ABC, abstractmethod


class DatabaseInterface(ABC):
    """
    Interface que define o que qualquer gerenciador de banco
    deve ser capaz de fazer. Não contém lógica, apenas as 'promessas'.
    """

    @abstractmethod
    def execute(self, query, params=None):
        """Deve executar um comando (Insert, Update, Delete)"""
        pass

    @abstractmethod
    def fetch_one(self, query, params=None):
        """Deve retornar apenas uma linha do banco"""
        pass

    @abstractmethod
    def fetch_all(self, query, params=None):
        """Deve retornar apenas uma linha do banco"""
        pass



    @abstractmethod
    def close(self):
        """Deve fechar a conexão com segurança"""
        pass