CREATE_TABLE_PRODUTOS = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_interno TEXT UNIQUE,        -- O seu campo original (essencial para ERP)
    tipo_item TEXT NOT NULL,           -- Inteligência (00, 09, etc)
    nome TEXT NOT NULL,                -- Mudamos 'descricao' para 'nome' (opcional, mas comum)
    unidade TEXT,                      -- UN, KG, PC, MT
    ncm TEXT,                          -- Novo campo fiscal
    peso_liquido REAL DEFAULT 0,
    peso_bruto REAL DEFAULT 0,
    preco_custo REAL DEFAULT 0,
    preco_venda REAL DEFAULT 0,
    estoque_atual REAL DEFAULT 0,      -- Físico
    estoque_reservado REAL DEFAULT 0,  -- Comprometido
    estoque_minimo REAL DEFAULT 0,
    observacoes TEXT,                  -- Antiga 'categoria' (agora temos Tipo de Item)
    data_cadastramento TEXT,
    ativo INTEGER DEFAULT 1            -- Controle para exclusão lógica
);
"""
