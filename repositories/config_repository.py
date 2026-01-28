class ConfigRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    # --- MÉTODOS QUE VOCÊ JÁ TINHA (Parâmetros) ---
    def get_valor(self, chave: str, padrao: str = None) -> str:
        query = "SELECT valor FROM configuracoes_sistema WHERE chave = ?"
        resultado = self.db.fetch_one(query, (chave,))
        return resultado['valor'] if resultado else padrao

    def atualizar_valor(self, chave: str, novo_valor: str):
        query = "UPDATE configuracoes_sistema SET valor = ? WHERE chave = ?"
        self.db.execute(query, (novo_valor, chave))

    # --- NOVOS MÉTODOS (Tabelas de Apoio - Formas de Pagamento) ---
    def listar_formas_pagamento(self, apenas_ativas=True):
        sql = "SELECT * FROM formas_pagamento_compras"
        if apenas_ativas:
            sql += " WHERE ativo = 1"
        return self.db.fetch_all(sql + " ORDER BY nome ASC")

    def salvar_forma_pagamento(self, nome):
        sql = "INSERT OR IGNORE INTO formas_pagamento_compras (nome, ativo) VALUES (?, 1)"
        return self.db.execute(sql, (nome.upper().strip(),))

    def alterar_status_forma(self, id_forma, status):
        """status 1 para Ativo, 0 para Inativo"""
        sql = "UPDATE formas_pagamento_compras SET ativo = ? WHERE id = ?"
        return self.db.execute(sql, (status, id_forma))