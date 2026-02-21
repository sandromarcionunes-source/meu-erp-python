from models.constants import StatusCredito, SituacaoEstoque, SituacaoLogistica

class PedidoRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def salvar(self, pedido):
        try:

            # 🟥 ORDEM SINCRONIZADA COM SEU SCHEMA:
            sql_p = """INSERT INTO pedidos (
                entidade_id, cliente_nome_snap, cliente_documento_snap, 
                cliente_endereco_snap, cliente_email_snap, data_emissao, 
                forma_pagamento, total_parcelas, intervalo_dias, 
                valor_frete, valor_total_produtos, valor_total_pedido, status_credito, situacao_estoque, situacao_logistica
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

            params_p = (
                pedido.entidade_id, pedido.cliente_nome_snap, pedido.cliente_documento_snap,
                pedido.cliente_endereco_snap, pedido.cliente_email_snap, pedido.data_emissao,
                pedido.forma_pagamento, pedido.total_parcelas, pedido.intervalo_dias,
                pedido.valor_frete, pedido.valor_total_produtos, pedido.valor_total_pedido, pedido.status_credito,
                pedido.situacao_estoque,pedido.situacao_logistica
            )

            # 🟨 VACINA DO CURSOR (IGUAL COMPRAS)
            res = self.db.execute(sql_p, params_p)
            pedido_id = res if isinstance(res, (int, str)) else getattr(res, 'lastrowid', None)

            if not pedido_id:
                raise Exception("Não foi possível obter o ID do pedido.")

            for item in pedido.itens:
                sql_i = """INSERT INTO pedido_itens (
                            pedido_id, produto_id, produto_nome_snap, 
                            quantidade, preco_venda, desconto, subtotal
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)"""

                self.db.execute(sql_i, (
                    int(pedido_id), item.produto_id, item.produto_nome_snap,
                    item.quantidade, item.preco_venda, item.desconto, item.subtotal
                ))

                # 🟦 LÓGICA DE ESTOQUE: Usando o import StatusPedido
                if pedido.situacao_estoque == SituacaoEstoque.RESERVADO:
                    self.db.execute("UPDATE produtos SET estoque_reservado = estoque_reservado + ? WHERE id = ?",
                                    (item.quantidade, item.produto_id))

                elif pedido.situacao_estoque == SituacaoEstoque.BAIXADO:
                    self.db.execute("UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id = ?",
                                    (item.quantidade, item.produto_id))

            return pedido_id

        except Exception as e:
            print(f"❌ Erro ao salvar pedido: {e}")
            return None

    def listar_todos(self):
        return self.db.fetch_all("SELECT * FROM pedidos ORDER BY id DESC")


    def buscar_itens_por_pedido(self, pedido_id):
        return self.db.fetch_all("SELECT * FROM pedido_itens WHERE pedido_id = ?", (pedido_id,))

    def deletar_com_estorno(self, pedido_id):
        p = self.db.fetch_one("SELECT situacao_estoque FROM pedidos WHERE id = ?", (pedido_id,))
        if not p: return False

        sit_est = p['situacao_estoque'] if isinstance(p, dict) else p[0]
        itens = self.buscar_itens_por_pedido(pedido_id)

        for it in itens:
            if sit_est == SituacaoEstoque.RESERVADO:
                self.db.execute("UPDATE produtos SET estoque_reservado = estoque_reservado - ? WHERE id = ?",
                                (it['quantidade'], it['produto_id']))
            elif sit_est == SituacaoEstoque.BAIXADO:
                self.db.execute("UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?",
                                (it['quantidade'], it['produto_id']))

        self.db.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
        return True

    def buscar_cliente_para_pedido(self, termo=None, id_exato=None):
        try:
            if id_exato:
                return self.db.fetch_one("SELECT * FROM entidades WHERE id = ?", (id_exato,))

            if termo:
                sql = """SELECT * FROM entidades 
                         WHERE (id = ? OR documento = ? OR nome_fantasia LIKE ? OR razao_social LIKE ?)"""
                t = f"%{termo}%"
                return self.db.fetch_all(sql, (termo, termo, t, t))

            return None
        except Exception as e:
            print(f"❌ Erro na busca de cliente via PedidoRepository: {e}")
            return None

    def buscar_por_id(self, pedido_id):
        return self.db.fetch_one("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))