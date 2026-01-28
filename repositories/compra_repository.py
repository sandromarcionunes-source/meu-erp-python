class CompraRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def salvar(self, compra):
        try:
            sql = """INSERT INTO compras (
                        fornecedor_id, fornecedor_nome_snap, data_emissao, 
                        valor_total, status, tipo_compra, observacao,
                        forma_pagamento, qtde_parcelas, intervalo_dias
                     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

            params = (compra.fornecedor_id, compra.fornecedor_nome_snap, compra.data_emissao,
                      compra.valor_total, 'DIGITADO', compra.tipo_compra, compra.observacao,
                      compra.forma_pagamento, compra.qtde_parcelas, compra.intervalo_dias)

            # O execute deve retornar o ID da última inserção
            compra_id = self.db.execute(sql, params)

            if not compra_id:
                raise Exception("Falha ao gerar ID da compra.")

            for item in compra.itens:
                # Importante: verifique se o nome da tabela é 'compra_itens' ou 'compras_itens'
                sql_i = """INSERT INTO compra_itens (
                               compra_id, produto_id, produto_nome_snap, 
                               quantidade, preco_custo, subtotal
                           ) VALUES (?, ?, ?, ?, ?, ?)"""

                # Usei 'item.valor_unitario' ou 'item.preco_custo' conforme sua classe estiver usando
                # Se der erro de atributo, verifique se no CompraItem você usou preco_custo ou valor_unitario
                self.db.execute(sql_i, (
                    int(compra_id),
                    item.produto_id,
                    item.produto_nome_snap,
                    item.quantidade,
                    item.valor_unitario,  # Altere para item.preco_custo se for o nome na sua classe
                    item.subtotal
                ))

            return compra_id
        except Exception as e:
            print(f"❌ Erro no Repository ao salvar pedido: {e}")
            return None

    def buscar_itens_por_compra(self, compra_id):
        return self.db.fetch_all("SELECT * FROM compra_itens WHERE compra_id = ?", (compra_id,))

    def filtrar_compras(self, busca=None, status=None):
        # Usamos TRIM para ignorar espaços em branco acidentais no banco
        query = "SELECT * FROM compras WHERE 1=1"
        params = []

        if busca and busca.strip():
            # Busca por ID, Nome ou Documento
            query += " AND (id = ? OR fornecedor_nome_snap LIKE ? OR observacao LIKE ?)"
            params.extend([busca, f"%{busca}%", f"%{busca}%"])

        if status and status.strip():
            # Usamos UPPER e TRIM para garantir que 'digitado' case com 'DIGITADO'
            query += " AND UPPER(TRIM(status)) = UPPER(TRIM(?))"
            params.append(status.strip())

        query += " ORDER BY id DESC"
        return self.db.fetch_all(query, params)

    def atualizar_status(self, compra_id, novo_status):
        return self.db.execute("UPDATE compras SET status = ? WHERE id = ?", (novo_status.upper(), compra_id))

    def atualizar_itens_compra(self, compra_id, novos_itens):
        self.db.execute("DELETE FROM compra_itens WHERE compra_id = ?", (compra_id,))
        for item in novos_itens:
            sql = """INSERT INTO compra_itens (compra_id, produto_id, produto_nome_snap, 
                     quantidade, preco_custo, subtotal) VALUES (?, ?, ?, ?, ?, ?)"""
            self.db.execute(sql, (compra_id, item.produto_id, item.produto_nome_snap,
                                  item.quantidade, item.preco_custo, item.subtotal))

    def atualizar_valores_compra(self, compra_id, total, forma, parc, intervalo):
        sql = """UPDATE compras SET valor_total = ?, forma_pagamento = ?, 
                 qtde_parcelas = ?, intervalo_dias = ? WHERE id = ?"""
        self.db.execute(sql, (total, forma, parc, intervalo, compra_id))

    def buscar_formas_pagamento_ativas(self):
        return self.db.fetch_all("SELECT * FROM formas_pagamento_compras WHERE ativo = 1")

    def buscar_itens_por_compra2(self, compra_id):
        sql = "SELECT * FROM compra_itens WHERE compra_id = ?"
        return self.db.fetch_all(sql, (compra_id,))

    def excluir_pedido(self, compra_id):
        try:
            # 1. Remove os itens primeiro
            self.db.execute("DELETE FROM compra_itens WHERE compra_id = ?", (compra_id,))
            # 2. Remove o pedido
            self.db.execute("DELETE FROM compras WHERE id = ?", (compra_id,))
            return True
        except Exception as e:
            print(f"Erro no banco: {e}")
            return False