CREATE_TABLE_PEDIDOS_COMPLETO = """
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entidade_id INTEGER NOT NULL,
    cliente_nome_snap TEXT,
    cliente_documento_snap TEXT,
    cliente_endereco_snap TEXT,
    cliente_email_snap TEXT,
    data_emissao TEXT NOT NULL,
    forma_pagamento TEXT NOT NULL,
    total_parcelas INTEGER DEFAULT 1,
    intervalo_dias INTEGER DEFAULT 30,
    valor_frete REAL DEFAULT 0,
    valor_total_produtos REAL DEFAULT 0,
    valor_total_pedido REAL DEFAULT 0,
    status TEXT DEFAULT 'CONCLUIDO', -- 'CONCLUIDO' ou 'RESERVADO'
    FOREIGN KEY (entidade_id) REFERENCES entidades (id)
);

CREATE TABLE IF NOT EXISTS pedido_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    produto_nome_snap TEXT, -- Nome do produto na hora da venda
    quantidade REAL NOT NULL,
    preco_unitario REAL NOT NULL,
    desconto REAL DEFAULT 0, -- Padronizado com seu PedidoItem
    subtotal REAL NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);
"""