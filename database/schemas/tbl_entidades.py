CREATE_TABLE_ENTIDADES_COMPLETO = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS entidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_pessoa TEXT NOT NULL CHECK(tipo_pessoa IN ('PF', 'PJ')),
        nome_fantasia TEXT NOT NULL,
        razao_social TEXT,
        documento TEXT UNIQUE NOT NULL,
        inscricao_estadual TEXT,
        inscricao_municipal TEXT,
        email_comercial TEXT,
        email_nfe TEXT,
        regime_tributario TEXT,
        indicador_ie TEXT DEFAULT '9',        
        limite_credito REAL DEFAULT 0,
        limite_validade TEXT,
        bloqueado INTEGER DEFAULT 0, -- 🛠️ CRUCIAL PARA O MOTOR DE CRÉDITO
        eh_cliente BOOLEAN DEFAULT 0,
        eh_fornecedor BOOLEAN DEFAULT 0,
        eh_transportadora BOOLEAN DEFAULT 0,
        eh_seguradora BOOLEAN DEFAULT 0,
        data_cadastramento DATETIME DEFAULT CURRENT_TIMESTAMP,
        observacoes TEXT
    );

    CREATE TABLE IF NOT EXISTS entidade_enderecos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entidade_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        cep TEXT,
        endereco TEXT,
        numero TEXT,
        complemento TEXT,
        bairro TEXT,
        cidade TEXT,
        uf TEXT,
        cidade_ibge INTEGER,
        FOREIGN KEY (entidade_id) REFERENCES entidades(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS entidade_contatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entidade_id INTEGER NOT NULL,
        tipo TEXT, 
        nome_contato TEXT,
        numero TEXT NOT NULL,
        FOREIGN KEY (entidade_id) REFERENCES entidades(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS socios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entidade_pai_id INTEGER NOT NULL,
    socio_entidade_id INTEGER NOT NULL,
    percentual_participacao REAL,
    data_entrada DATETIME NOT NULL,
    data_saida DATETIME,
    cargo TEXT DEFAULT 'Sócio',
    nome_snapshot TEXT,
    FOREIGN KEY (entidade_pai_id) REFERENCES entidades(id) ON DELETE CASCADE
);
"""