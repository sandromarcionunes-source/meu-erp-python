from .tbl_clientes import CREATE_TABLE as cliente_sql
from .tbl_produtos import CREATE_TABLE_PRODUTOS as produto_sql
from .tbl_pedidos import CREATE_TABLE_PEDIDOS_COMPLETO as pedidos_sql
from .formas_pagamento import CREATE_TABLE_FORMAS_PAGAMENTO as formas_pagamento_sql
from .tbl_entidades import CREATE_TABLE_ENTIDADES_COMPLETO as entidades_sql
from .estoque_movimentos import CREATE_TABLE_ESTOQUE_MOVIMENTOS as estoque_movimento_sql
from .tbl_configuracoes import CREATE_TABLE_CONFIGURACOES as configuracoes_sql
from .tbl_configuracoes import INSERT_DEFAULT_CONFIGS as inicializar_configs_sql
from .tbl_compras import CREATE_TABLE_COMPRAS_COMPLETO as compras_sql
from .formas_pagamento_compras import CREATE_TABLE_FORMAS_PAGAMENTO_COMPRAS as formas_pagto_compras

# Lista com todas as tabelas para criação em lote
ALL_TABLES = [
    cliente_sql,
    produto_sql,
    pedidos_sql,
    formas_pagamento_sql,
    entidades_sql,
    estoque_movimento_sql,
    configuracoes_sql,      # 🆕 Criar tabela de configurações
    inicializar_configs_sql, # 🆕 Inserir os parâmetros padrão
    compras_sql,
    formas_pagto_compras
]