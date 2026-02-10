class Endereco:
    def __init__(self, tipo, endereco, numero, cep, bairro, cidade, uf, cidade_ibge, complemento=None, id=None):
        self.id = id
        self.tipo = tipo
        self.cep = cep
        self.endereco = endereco
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.uf = uf
        self.cidade_ibge = cidade_ibge