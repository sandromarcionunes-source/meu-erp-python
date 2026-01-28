CREATE_TABLE_CONFIGURACOES = """
CREATE TABLE IF NOT EXISTS configuracoes_sistema (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL,
    descricao TEXT
);
"""

# Script para popular as configurações iniciais
INSERT_DEFAULT_CONFIGS = """
INSERT OR IGNORE INTO configuracoes_sistema (chave, valor, descricao) 
VALUES ('MODO_ESTOQUE', 'RESERVA', 'Define se o pedido gera RESERVA ou BAIXA DIRETA');
"""