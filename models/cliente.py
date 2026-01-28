class Cliente:
    def __init__(self, tipo_pessoa, nome, razao_social, cpf, cnpj, cep, email, telefone, endereco, numero, complemento, bairro, cidade, uf, data_cadastramento, limite_credito = 0, id=None):
        self.id = id
        self.tipo_pessoa = tipo_pessoa
        self.nome = nome
        self.razao_social = razao_social
        self.cpf = cpf
        self.cnpj = cnpj
        self.cep = cep
        self.email = email
        self.telefone = telefone
        self.endereco = endereco
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.uf = uf
        self.data_cadastramento = data_cadastramento
        self.limite_credito = limite_credito

    def __str__(self):
        nome_exibicao = self.nome if self.tipo_pessoa == 'pf' else self.razao_social
        doc_exibicao = self.cpf if self.tipo_pessoa == 'pf' else self.cnpj
        return f"ID: {self.id or 'Novo'} | {self.tipo_pessoa.upper()} | {nome_exibicao} | Doc: {doc_exibicao}"