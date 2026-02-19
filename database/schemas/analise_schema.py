CREATE_TABLE_ANALISE_CREDITO = """
-- 1. TABELA DE CONFIGURAÇÃO (O Cérebro)
CREATE TABLE IF NOT EXISTS config_credito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bloquear_automatico INTEGER DEFAULT 1,
    limite_padrao_novos_clientes REAL DEFAULT 0,
    dias_tolerancia_atraso INTEGER DEFAULT 0
);

INSERT OR IGNORE INTO config_credito (id, bloquear_automatico) VALUES (1, 1);

-- 2. TABELA DE LOGS (A Memória/Auditoria)
CREATE TABLE IF NOT EXISTS analise_credito_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER,
    entidade_id INTEGER NOT NULL,
    data_hora TEXT NOT NULL,
    valor_pedido REAL,
    limite_na_epoca REAL,
    resultado TEXT NOT NULL,
    motivo TEXT,
    FOREIGN KEY (entidade_id) REFERENCES entidades (id)
);
"""