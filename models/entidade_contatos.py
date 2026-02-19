class Contato:
    def __init__(self, tipo, numero, nome_contato, id=None):
        """
        Representa um contato telefônico ou eletrônico.
        ⚙️ Tipo agora é validado via menu numérico no Service.
        """
        self.id = id
        self.tipo = tipo
        self.numero = numero
        self.nome_contato = nome_contato