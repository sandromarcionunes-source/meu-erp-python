class FormaPagamentoRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def listar_ativas(self):
        """Retorna todas as formas de pagamento para o menu de escolha do vendedor."""
        query = "SELECT * FROM formas_pagamento WHERE ativo = 1 ORDER BY nome ASC"
        return self.db.fetch_all(query)

    def buscar_por_id(self, id_forma):
        """Busca uma forma específica para gravar o nome correto no cabeçalho do pedido."""
        query = "SELECT * FROM formas_pagamento WHERE id = ?"
        return self.db.fetch_one(query, (id_forma,))