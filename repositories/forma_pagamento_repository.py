class FormaPagamentoRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def listar_ativas(self):
        # Ajuste o nome da coluna conforme o seu banco (ex: nome ou descricao)
        return self.db.fetch_all("SELECT id, nome FROM formas_pagamento WHERE ativo = 1")

    def buscar_por_id(self, id_forma):
        """Busca uma forma específica para gravar o nome correto no cabeçalho do pedido."""
        query = "SELECT * FROM formas_pagamento WHERE id = ?"
        return self.db.fetch_one(query, (id_forma,))