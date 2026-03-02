from models.constants import SituacaoLogistica, SituacaoEstoque, StatusCredito
class NotaFiscalRepository:
    def __init__(self, db):
        self.db = db

    def obter_proximo_numero(self):
        res = self.db.fetch_one("SELECT MAX(numero_nf) FROM notas_fiscais")
        return (res[0] if res and res[0] else 0) + 1

    def atualizar_status_pedido(self, pedido_id, status):
        # 🟢 Atualiza a situação logistica direto na tabela de pedidos
        sql = "UPDATE pedidos SET situacao_logistica = ? WHERE id = ?"
        return self.db.execute(sql, (status, pedido_id))

    def salvar_completa(self, nf_cabecalho, lista_itens):
        try:
            # 1. Cadastro do Cabeçalho
            query_cab = """
                INSERT INTO notas_fiscais (
                    pedido_id, numero_nf, serie, chave_acesso, data_emissao,
                    emissor_razao_snap, emissor_cnpj_snap, emissor_ie_snap,
                    cliente_nome_snap, cliente_doc_snap, cliente_end_snap,
                    valor_produtos, valor_frete, valor_total_nota,
                    peso_bruto_total, peso_liquido_total, status, protocolo
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """
            params_cab = (
                nf_cabecalho['pedido_id'], nf_cabecalho['numero_nf'], nf_cabecalho['serie'],
                nf_cabecalho['chave_acesso'], nf_cabecalho['data_emissao'],
                nf_cabecalho['emissor_razao'], nf_cabecalho['emissor_cnpj'], nf_cabecalho['emissor_ie'],
                nf_cabecalho['cli_nome'], nf_cabecalho['cli_doc'], nf_cabecalho['cli_end'],
                nf_cabecalho['v_prod'], nf_cabecalho['v_frete'], nf_cabecalho['v_total'],
                nf_cabecalho['p_bruto'], nf_cabecalho['p_liquido'], 'AUTORIZADA', nf_cabecalho['protocolo']
            )
            nf_id = self.db.execute(query_cab, params_cab)

            # 2. Cadastro dos Itens (CORRIGIDO: Agora com todas as colunas do seu Schema)
            query_item = """
                INSERT INTO nota_fiscal_itens (
                    nota_fiscal_id, produto_id, nome_produto_snap, ncm_snap,
                    quantidade, valor_unitario, valor_total_item, 
                    peso_bruto_unit, peso_liquido_unit
                ) VALUES (?,?,?,?,?,?,?,?,?)
            """

            for item in lista_itens:
                # Salva Item
                self.db.execute(query_item, (
                    nf_id, item['produto_id'], item['nome'], item['ncm'],
                    item['qtd'], item['valor_u'], item['valor_t'],
                    item['p_bruto_u'], item['p_liq_u']
                ))

                # 3. Baixa de Estoque Físico e Limpeza de Reserva
                sql_estoque = """
                    UPDATE produtos 
                    SET estoque_atual = estoque_atual - ?,
                        estoque_reservado = estoque_reservado - ?
                    WHERE id = ?
                """
                self.db.execute(sql_estoque, (item['qtd'], item['qtd'], item['produto_id']))

            # 4. Atualiza Pedido para FATURADO (Regra Logística)
            self.db.execute(
                "UPDATE pedidos SET situacao_logistica = ? WHERE id = ?",
                ("FATURADO", nf_cabecalho['pedido_id'])
            )

            return nf_id
        except Exception as e:
            print(f"❌ Erro Crítico no Repository: {e}")
            return None

    def buscar_nota_completa(self, nota_id):
        # Busca o cabeçalho
        cabecalho = self.db.fetch_one("SELECT * FROM notas_fiscais WHERE id = ?", (nota_id,))
        if not cabecalho:
            return None

        # Busca os itens vinculados
        itens = self.db.fetch_all("SELECT * FROM nota_fiscal_itens WHERE nota_fiscal_id = ?", (nota_id,))

        return {
            'cabecalho': cabecalho,
            'itens': itens
        }

    def estornar_faturamento(self, pedido_id, lista_itens):
        """
        🚩 Objetivo: Devolver produtos ao estoque e resetar o pedido
        para que ele volte para a fila de 'APROVADO' ou 'PENDENTE'.
        """
        try:
            # 1. Devolve o estoque (Soma no atual e Soma no reservado)
            for item in lista_itens:
                sql_estoque = """
                    UPDATE produtos 
                    SET estoque_atual = estoque_atual + ?,
                        estoque_reservado = estoque_reservado + ?
                    WHERE id = ?
                """
                self.db.execute(sql_estoque, (item['qtd'], item['qtd'], item['produto_id']))

            # 2. Reseta o Pedido
            # 🚩 Aqui ele volta a ser 'APROVADO' no crédito,
            # mas 'PENDENTE' na logística para ser faturado de novo.
            query_reset = """
                UPDATE pedidos 
                SET situacao_logistica = ?, 
                    situacao_estoque = ?, 
                    situacao_financeira = ?
                WHERE id = ?
            """
            self.db.execute(query_reset, (
                SituacaoLogistica.PENDENTE,
                SituacaoEstoque.RESERVADO,
                StatusCredito.APROVADO,  # 🚩 Volta para aprovado para reavaliar limite
                pedido_id
            ))

            # 3. Cancela a Nota Fiscal no banco (opcional, dependendo da sua regra)
            self.db.execute("UPDATE notas_fiscais SET status = 'CANCELADA' WHERE pedido_id = ?", (pedido_id,))

            return True
        except Exception as e:
            print(f"❌ Erro ao estornar: {e}")
            return False