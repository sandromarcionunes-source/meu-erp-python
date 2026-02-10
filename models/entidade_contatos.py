class Contato:
    def __init__(self, tipo, numero, nome_contato=None, id=None):
        self.id = id
        self.tipo = tipo
        self.numero = numero
        self.nome_contato = nome_contato