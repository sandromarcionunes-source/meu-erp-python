class Endereco:
    def __init__(self, tipo, cep, endereco, numero, complemento, bairro, cidade, uf, cidade_ibge=None, id=None):
        """
        Representa um endereço vinculado a uma entidade.
        🆕 cidade_ibge adicionado para garantir a sincronia com o banco de dados.
        """
        self.id = id
        self.tipo = tipo  # ⚙️ Definido via menu (PRINCIPAL, COBRANÇA, etc)
        self.cep = cep
        self.endereco = endereco
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.uf = uf
        self.cidade_ibge = cidade_ibge # 🛠️ Este era o campo que o erro apontava como faltante