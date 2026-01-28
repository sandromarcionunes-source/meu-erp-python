class PedidoRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def salvar(self, pedido, baixar_imediato=True):
        try:
            # 1. SALVAR PEDIDO
            sql_p = """INSERT INTO pedidos (entidade_id, data_emissao, valor_total_produtos, valor_frete, 
                       valor_total_pedido, forma_pagamento, status, cliente_nome_snap, 
                       cliente_documento_snap, cliente_endereco_snap, cliente_email_snap) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

            params_p = (
                int(pedido.entidade_id), pedido.data_emissao, pedido.valor_total_produtos,
                pedido.valor_frete, pedido.valor_total_pedido, pedido.forma_pagamento,
                "CONCLUIDO" if baixar_imediato else "RESERVADO",
                pedido.cliente_nome_snap, pedido.cliente_documento_snap,
                pedido.cliente_endereco_snap, pedido.cliente_email_snap
            )

            pedido_id = self.db.execute(sql_p, params_p)
            print(f"DEBUG: Pedido {pedido_id} salvo. Gravando {len(pedido.itens)} itens...")

            # 2. SALVAR ITENS
            # 3. SALVANDO OS ITENS E ATUALIZANDO ESTOQUE (LÓGICA OPÇÃO B)
            for item in pedido.itens:
                prod_id = int(str(item.produto_id).strip())

                # Inserir item na tabela pedido_itens
                sql_item = """
                            INSERT INTO pedido_itens (
                                pedido_id, produto_id, produto_nome_snap, 
                                quantidade, preco_unitario, desconto, subtotal
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                            """
                self.db.execute(sql_item, (
                    pedido_id, prod_id, item.produto_nome_snap,
                    item.quantidade, item.preco_unitario, item.desconto, item.subtotal
                ))

                # ATUALIZAÇÃO DE ESTOQUE - OPÇÃO B
                if baixar_imediato:
                    # Apenas retira do atual (Venda finalizada)
                    sql_est = "UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id = ?"
                    self.db.execute(sql_est, (item.quantidade, prod_id))
                else:
                    # RESERVA: Tira do 'Disponível' (Atual) e move para 'Reservado'
                    sql_est = """
                                    UPDATE produtos 
                                    SET estoque_atual = estoque_atual - ?, 
                                        estoque_reservado = estoque_reservado + ? 
                                    WHERE id = ?
                                """
                    self.db.execute(sql_est, (item.quantidade, item.quantidade, prod_id))

            return pedido_id

        except Exception as e:
            print(f"❌ Erro ao salvar pedido (Opção B): {e}")
            return None

    def listar_todos(self):
        return self.db.fetch_all("SELECT * FROM pedidos ORDER BY id DESC")

    def deletar(self, pedido_id):
        try:
            # 1. Deletar os itens do pedido primeiro (Segurança manual)
            self.db.execute("DELETE FROM pedido_itens WHERE pedido_id = ?", (pedido_id,))

            # 2. Deletar o cabeçalho do pedido
            self.db.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))

            return True
        except Exception as e:
            print(f"❌ Erro ao deletar pedido: {e}")
            return False

    def filtrar_pedidos(self, cliente=None, data=None, status=None):
        query = "SELECT * FROM pedidos WHERE 1=1"
        params = []

        if cliente:
            query += " AND cliente_nome_snap LIKE ?"
            params.append(f"%{cliente}%")

        if data:
            query += " AND data_emissao LIKE ?"
            params.append(f"%{data}%")

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY id DESC"
        return self.db.fetch_all(query, params)

    def deletar_com_estorno(self, pedido_id):
        """
        Deleta o pedido e devolve os produtos ao estoque
        baseado no status original (CONCLUIDO ou RESERVADO).
        """
        try:
            # 1. Busca o status do pedido e os itens antes de apagar tudo
            pedido_info = self.db.fetch_one("SELECT status FROM pedidos WHERE id = ?", (pedido_id,))
            if not pedido_info:
                print(f"❌ Pedido {pedido_id} não encontrado no banco.")
                return False

            status_origem = pedido_info['status']
            itens = self.db.fetch_all("SELECT produto_id, quantidade FROM pedido_itens WHERE pedido_id = ?",
                                      (pedido_id,))

            # 2. Loop de Devolução de Estoque
            for item in itens:
                p_id = item['produto_id']
                qtd = item['quantidade']

                if status_origem == "RESERVADO":
                    # Reverte Opção B: Tira do reservado e volta para o disponível (atual)
                    sql = """
                        UPDATE produtos 
                        SET estoque_atual = estoque_atual + ?, 
                            estoque_reservado = estoque_reservado - ? 
                        WHERE id = ?
                    """
                    self.db.execute(sql, (qtd, qtd, p_id))
                else:
                    # Reverte Venda Normal: Apenas devolve ao atual
                    sql = "UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?"
                    self.db.execute(sql, (qtd, p_id))

            # 3. Remove os registros do banco (O banco limpa pedido_itens se houver CASCADE)
            # Por segurança, limpamos manualmente os itens primeiro
            self.db.execute("DELETE FROM pedido_itens WHERE pedido_id = ?", (pedido_id,))
            self.db.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))

            return True

        except Exception as e:
            print(f"❌ Erro ao estornar estoque e deletar: {e}")
            return False