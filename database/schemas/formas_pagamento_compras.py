CREATE_TABLE_FORMAS_PAGAMENTO_COMPRAS = """
CREATE TABLE IF NOT EXISTS formas_pagamento_compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL, -- Ex: Boleto 30 dias, Depósito, Dinheiro
    ativo INTEGER DEFAULT 1
);

"""