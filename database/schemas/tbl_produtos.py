CREATE_TABLE_PRODUTOS = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_interno TEXT UNIQUE,
    tipo_item TEXT NOT NULL,
    nome TEXT NOT NULL,
    unidade TEXT,
    categoria TEXT DEFAULT NULL,
    marca TEXT DEFAULT NULL,
    modelo_versao TEXT DEFAULT NULL,
    ncm TEXT,
    cest TEXT,
    origem INTEGER DEFAULT 0,
    peso_liquido REAL DEFAULT 0,
    peso_bruto REAL DEFAULT 0,
    preco_custo REAL DEFAULT 0,
    preco_venda REAL DEFAULT 0,
    estoque_atual REAL DEFAULT 0,
    estoque_reservado REAL DEFAULT 0,
    estoque_minimo REAL DEFAULT 0,
    observacoes TEXT,
    data_cadastramento TEXT,
    ativo INTEGER DEFAULT 1
);
"""
