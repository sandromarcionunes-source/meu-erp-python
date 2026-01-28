CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_pessoa TEXT NOT NULL,
    nome TEXT,
    razao_social TEXT,
    cpf TEXT UNIQUE,
    cnpj TEXT UNIQUE,
    cep TEXT NOT NULL,
    email TEXT NOT NULL,
    telefone TEXT NOT NULL,
    endereco TEXT NOT NULL,
    numero TEXT NOT NULL,
    complemento TEXT NOT NULL,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    data_cadastramento DATETIME,
    limite_credito REAL DEFAULT 0
);
"""