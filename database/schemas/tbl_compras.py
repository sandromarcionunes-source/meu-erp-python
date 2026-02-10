CREATE_TABLE_COMPRAS_COMPLETO = """
CREATE TABLE IF NOT EXISTS compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor_id INTEGER NOT NULL,
    fornecedor_nome_snap TEXT,
    data_emissao TEXT NOT NULL,
    valor_total REAL DEFAULT 0,
    status TEXT DEFAULT 'DIGITADO', 
    tipo_compra TEXT,
    forma_pagamento TEXT,
    qtde_parcelas INTEGER DEFAULT 1,
    intervalo_dias INTEGER DEFAULT 0,
    observacao TEXT
);

CREATE TABLE IF NOT EXISTS compra_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compra_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    produto_nome_snap TEXT,
    quantidade REAL NOT NULL,
    preco_custo REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (compra_id) REFERENCES compras (id) ON DELETE CASCADE
);

"""