CREATE_TABLE_DADOS_EMISSOR = """
CREATE TABLE IF NOT EXISTS dados_emissor (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    razao_social TEXT NOT NULL,
    nome_fantasia TEXT,
    cnpj TEXT UNIQUE NOT NULL,
    inscricao_estadual TEXT NOT NULL,
    email TEXT NOT NULL,
    telefone TEXT NOT NULL,
    cep TEXT NOT NULL,
    endereco TEXT NOT NULL,
    numero TEXT NOT NULL,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    ibge_municipio INTEGER NOT NULL,
    regime_tributario INTEGER NOT NULL
);
"""