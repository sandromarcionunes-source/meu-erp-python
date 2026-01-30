CREATE_TABLE_SEGUROS = """
CREATE TABLE IF NOT EXISTS seguros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entidade_seguradora_id INTEGER NOT NULL, -- ID da Seguradora (um Fornecedor)
    numero_apolice TEXT NOT NULL,
    valor_premio REAL NOT NULL, -- Valor que vai para a NF
    data_emissao_apolice DATE,
    vigencia_inicio DATE,
    vigencia_fim DATE,
    status TEXT DEFAULT 'ATIVO', -- ATIVO, CANCELADO, ENCERRADO
    FOREIGN KEY (entidade_seguradora_id) REFERENCES entidades (id)
);
"""