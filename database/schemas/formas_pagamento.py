CREATE_TABLE_FORMAS_PAGAMENTO = """CREATE TABLE IF NOT EXISTS formas_pagamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    taxa REAL DEFAULT 0,
    ativo INTEGER DEFAULT 1 -- 1 para Sim, 0 para Não
);

-- Inserir valores padrão logo após a criação
INSERT OR IGNORE INTO formas_pagamento (nome) VALUES
('Dinheiro'), ('Cartão Crédito'), ('Cartão Débito'), ('PIX'), ('Boleto');

"""