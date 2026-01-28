CREATE_TABLE_ENTIDADES_COMPLETO = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS entidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_pessoa TEXT NOT NULL CHECK(tipo_pessoa IN ('PF', 'PJ')),
        nome_fantasia TEXT NOT NULL,
        razao_social TEXT,
        documento TEXT UNIQUE NOT NULL,
        email TEXT,
        telefone TEXT,
        cep TEXT,
        endereco TEXT,
        numero TEXT,
        complemento TEXT,
        bairro TEXT,
        cidade TEXT,
        uf TEXT,
        limite_credito REAL DEFAULT 0,
        eh_cliente BOOLEAN DEFAULT 0,
        eh_fornecedor BOOLEAN DEFAULT 0,
        eh_transportadora BOOLEAN DEFAULT 0,
        data_cadastramento DATETIME DEFAULT CURRENT_TIMESTAMP,
        observacoes TEXT
    );

    CREATE TABLE IF NOT EXISTS socios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entidade_pai_id INTEGER NOT NULL,
    socio_entidade_id INTEGER NOT NULL,
    percentual_participacao REAL,
    data_entrada DATETIME NOT NULL,
    data_saida DATETIME,
    cargo TEXT DEFAULT 'Sócio',
    nome_snapshot TEXT -- 👈 ADICIONE ESTA LINHA AQUI
    );
"""