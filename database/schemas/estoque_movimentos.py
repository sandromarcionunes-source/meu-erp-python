CREATE_TABLE_ESTOQUE_MOVIMENTOS = """
CREATE TABLE IF NOT EXISTS estoque_movimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL,
    tipo TEXT NOT NULL, -- 'E' para Entrada, 'S' para Saída
    quantidade REAL NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT,
    usuario TEXT,
    FOREIGN KEY (id_produto) REFERENCES produtos (id)
);
"""