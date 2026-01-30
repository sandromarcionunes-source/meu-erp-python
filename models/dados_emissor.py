class DadosEmissor:
    def __init__(self, razao_social, cnpj, inscricao_estadual, email, telefone, cep,
                 endereco, numero, bairro, cidade, uf, ibge_municipio,
                 regime_tributario, nome_fantasia=None, id=1):
        self.id = id  # Sempre será 1
        self.razao_social = razao_social
        self.nome_fantasia = nome_fantasia
        self.cnpj = cnpj
        self.inscricao_estadual = inscricao_estadual
        self.email = email
        self.telefone = telefone
        self.cep = cep
        self.endereco = endereco
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        self.uf = uf
        self.ibge_municipio = ibge_municipio
        self.regime_tributario = regime_tributario

    def __str__(self):
        return f"Emissor: {self.razao_social} | CNPJ: {self.cnpj} | Regime: {self.regime_tributario}"