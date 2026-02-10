CREATE_TABLE_FORMAS_PAGAMENTO_COMPRAS = """
CREATE TABLE IF NOT EXISTS formas_pagamento_compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,  -- Adicionamos UNIQUE aqui para não permitir nomes repetidos
    ativo INTEGER DEFAULT 1
);

-- Usamos INSERT OR IGNORE: se o nome já existir, o banco simplesmente ignora o comando
INSERT OR IGNORE INTO formas_pagamento_compras (nome, ativo) VALUES ('BOLETO BANCÁRIO', 1);
INSERT OR IGNORE INTO formas_pagamento_compras (nome, ativo) VALUES ('PIX', 1);
INSERT OR IGNORE INTO formas_pagamento_compras (nome, ativo) VALUES ('TRANSFERÊNCIA', 1);
INSERT OR IGNORE INTO formas_pagamento_compras (nome, ativo) VALUES ('DINHEIRO', 1);
INSERT OR IGNORE INTO formas_pagamento_compras (nome, ativo) VALUES ('CARTÃO CORPORATIVO', 1);
"""