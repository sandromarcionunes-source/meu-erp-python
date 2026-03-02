CREATE_TABLE_NOTA_FISCAL_VENDAS = """
CREATE TABLE IF NOT EXISTS notas_fiscais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER,
    numero_nf INTEGER NOT NULL,
    serie INTEGER DEFAULT 1,
    chave_acesso TEXT UNIQUE,
    data_emissao TEXT,

    -- Dados do Emissor (Snapshot)
    emissor_razao_snap TEXT,
    emissor_cnpj_snap TEXT,
    emissor_ie_snap TEXT,

    -- Dados do Cliente (Snapshot vindo do Pedido)
    cliente_nome_snap TEXT,
    cliente_doc_snap TEXT,
    cliente_end_snap TEXT,

    -- Totais da Nota
    valor_produtos REAL,
    valor_frete REAL,
    valor_total_nota REAL,
    peso_bruto_total REAL,
    peso_liquido_total REAL,

    status TEXT, -- 'AUTORIZADA', 'CANCELADA'
    protocolo TEXT,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);

CREATE TABLE IF NOT EXISTS nota_fiscal_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nota_fiscal_id INTEGER,
    produto_id INTEGER,
    nome_produto_snap TEXT,
    ncm_snap TEXT,
    quantidade REAL,
    valor_unitario REAL,
    valor_total_item REAL,
    peso_bruto_unit REAL,
    peso_liquido_unit REAL,
    FOREIGN KEY (nota_fiscal_id) REFERENCES notas_fiscais(id)
);
"""





# Entidades
# CNPJ/CPF, Inscrição Estadual, Razão Social, Endereço Completo, código_ibge, CEP e E-mail.
#
# produtos
# Descrição, Unidade (UN, KG), Preço de Venda, NCM
#
# Origem produto NAcional
#
# Pedidos
# Quantidades vendidas, Descontos aplicados, Valor do Frete e Valor Total.
