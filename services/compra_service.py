from datetime import datetime
from models.compra import Compra, CompraItem


class CompraService:
    def __init__(self, compra_repo, ent_repo, prod_repo, repo_config):
        self.repo = compra_repo
        self.ent_repo = ent_repo
        self.prod_repo = prod_repo
        self.repo_config = repo_config

    def ler_dados(self, obj, chaves):
        """Lê dados de forma segura de Rows (DB) ou Objetos (Classes)"""
        for c in chaves:
            try:
                return obj[c]
            except:
                try:
                    return getattr(obj, c)
                except:
                    continue
        return ""


    # =========================================================================
    # 🟢 [INÍCIO DA NOVA FUNÇÃO] - ADICIONE ESTE BLOCO ABAIXO:
    # =========================================================================
    def _buscar_fornecedor_soberano(self, termo):
        """
        MÉTODO INDEPENDENTE: Busca fornecedores sem depender do EntidadeRepository.
        Isso garante que mudanças em Entidades não quebrem o módulo de Compras.
        """
        sql = """
            SELECT id, nome_fantasia, razao_social, documento 
            FROM entidades 
            WHERE (id = ? OR documento = ? OR nome_fantasia LIKE ? OR razao_social LIKE ?)
            AND eh_fornecedor = 1
        """
        params = (termo, termo, f"%{termo}%", f"%{termo}%")

        try:
            # Acessamos o banco diretamente via gerenciador do repositório
            return self.ent_repo.db.fetch_all(sql, params)
        except Exception as e:
            print(f"❌ Erro na busca soberana de fornecedor: {e}")
            return []
    # =========================================================================
    # 🔴 [FIM DA NOVA FUNÇÃO]
    # =========================================================================


    def exibir_menu(self):
        while True:
            print("\n" + "=" * 45)
            print("      📦 MÓDULO DE COMPRAS")
            print("=" * 45)
            print("1. 📝 Novo Pedido")
            print("2. 📋 Listar Compras")
            print("3. ⚙️  Alterar Status")
            print("4. 🚚 Recebimento (Entrada Estoque)")
            print("5. 🚚 Revisar Pedido (Equiparar NF)")
            print("6. 🔎 Consulta Detalhada")
            print("7. 🗑️  Deletar Pedido")
            print("8. 🗑️  Consultar todos os Pedido")
            print("0. ⬅️  Voltar")

            op = input("\nEscolha: ")
            if op == "1":
                self.novo_pedido_compra()
            elif op == "2":
                self.listar_compras_filtrado()
            elif op == "3":
                self.gerenciar_fluxo_compra()
            elif op == "4":
                self.processar_recebimento()
            elif op == "5":
                self.revisar_pedido_para_entrada()
            elif op == "6":
                self.visualizar_detalhes_pedido()
            elif op == "7":
                self.excluir_pedido_compra()
            elif op == "8":
                self.consultar_todos_pedidos()
            elif op == "0":
                break

    def novo_pedido_compra(self):
        print("\n--- NOVO PEDIDO DE COMPRA ---")
        termo = input("🔍 Buscar Fornecedor: ").strip()
        # =====================================================================
        # 🟡 [ALTERAÇÃO AQUI] - SUBSTITUA AS LINHAS DE BUSCA ANTIGAS POR ESTAS:
        # =====================================================================
        # CHAMADA DA NOVA FUNÇÃO SOBERANA
        forns = self._buscar_fornecedor_soberano(termo)

        if not forns:
            return print("❌ Fornecedor não encontrado ou não marcado como Fornecedor.")

        for f in forns:
            # Note que agora usamos as chaves diretas do SQL da função soberana
            print(f"  [{f['id']}] {f['nome_fantasia'] or f['razao_social']}")

        id_f = input("👉 ID Fornecedor: ")

        # BUSCA O SELECIONADO DIRETAMENTE
        f_sel = self.ent_repo.db.fetch_one("SELECT id, nome_fantasia, razao_social FROM entidades WHERE id = ?",
                                           (id_f,))

        if not f_sel: return print("❌ Seleção inválida.")

        nome_forn_snap = f_sel['nome_fantasia'] or f_sel['razao_social']

        compra = Compra(id_f, nome_forn_snap, "REVENDA",
                        datetime.now().strftime("%d/%m/%Y %H:%M"))
        # =====================================================================
        # 🔴 [FIM DA ALTERAÇÃO]
        # =====================================================================

        while True:
            busca_p = input("\n📦 Produto (Nome/ID) [F p/ fechar]: ").strip()
            if busca_p.upper() == 'F': break

            prods = self.prod_repo.buscar_por_id_ou_descricao(busca_p)
            if not prods: continue

            for p in prods:
                print(f"  [{self.ler_dados(p, ['id'])}] {self.ler_dados(p, ['nome', 'descricao'])}")

            id_p = input("👉 ID Produto: ")
            p_sel = self.prod_repo.buscar_por_id(id_p)
            if not p_sel: continue

            nome_p = self.ler_dados(p_sel, ['nome', 'descricao', 'produto_nome_snap']) or "Produto s/ nome"
            qtd = float(input(f"   Quantidade para {nome_p}: ").replace(',', '.'))
            custo = float(input("   Preço Custo Unit: ").replace(',', '.'))

            compra.adicionar_item(CompraItem(id_p, nome_p, qtd, custo))
            print(f"✅ Item '{nome_p}' adicionado.")

        if not compra.itens: return

        # FINANCEIRO COMPLETO
        print("\n--- FINANCEIRO ---")
        compra.forma_pagamento = self.escolher_forma_pagamento()
        try:
            compra.qtde_parcelas = int(input("🔢 Quantidade de Parcelas [1]: ") or 1)
            if compra.qtde_parcelas > 1:
                compra.intervalo_dias = int(input("📅 Intervalo (dias) [30]: ") or 30)
        except:
            compra.qtde_parcelas, compra.intervalo_dias = 1, 0

        compra.observacao = input("📝 Nº da Nota Fiscal / Obs: ").strip()

        print(f"\n💰 TOTAL: R$ {compra.valor_total:.2f}")
        if input("🚀 Salvar Pedido? (S/N): ").upper() == 'S':
            id_c = self.repo.salvar(compra)
            if id_c: print(f"✅ PEDIDO #{id_c} GERADO!")

    def escolher_forma_pagamento(self):
        formas = self.repo.buscar_formas_pagamento_ativas()
        if not formas: return "DINHEIRO"
        print("\n💳 SELECIONE A FORMA:")
        for i, f in enumerate(formas, 1):
            print(f"   [{i}] {self.ler_dados(f, ['nome'])}")
        try:
            op = int(input("👉 Escolha o nº: "))
            return self.ler_dados(formas[op - 1], ['nome'])
        except:
            return self.ler_dados(formas[0], ['nome'])

    # def listar_compras_filtrado22(self):
    #     termo = input("\n🔍 Buscar ID ou Fornecedor: ").strip()
    #     compras = self.repo.filtrar_compras(busca=termo)
    #     if not compras: return print("⚠️ Nada encontrado.")
    #
    #     print("\n" + "═" * 85)
    #     print(f"{'ID':<5} | {'DATA':<16} | {'FORNECEDOR':<25} | {'TOTAL':<12} | {'STATUS':<12}")
    #     print("─" * 85)
    #     for c in compras:
    #         id_c = self.ler_dados(c, ['id'])
    #         data = self.ler_dados(c, ['data_emissao'])
    #         forn = self.ler_dados(c, ['fornecedor_nome_snap'])[:25]
    #         total = self.ler_dados(c, ['valor_total'])
    #         status = self.ler_dados(c, ['status'])
    #         print(f"{id_c:<5} | {data:<16} | {forn:<25} | R${total:>9.2f} | {status:<12}")

    def listar_compras_filtrado(self):
        """
        LISTAGEM FLEXÍVEL: Agora permite buscar por ID, Nome ou CPF/CNPJ do fornecedor.
        """
        termo = input("\n🔍 Buscar (ID, Fornecedor ou CPF/CNPJ): ").strip()
        compras = self.repo.filtrar_compras(busca=termo)

        if not compras:
            print("⚠️ Nenhum pedido encontrado para este critério.")
            return

        # Ajuste de larguras para incluir o documento
        L_ID, L_DATA, L_FORN, L_DOC, L_TOTAL, L_STATUS = 5, 12, 25, 15, 12, 12
        TAM_TOTAL = 95

        print("\n" + "═" * TAM_TOTAL)
        print(
            f"{'ID':<{L_ID}} | {'DATA':<{L_DATA}} | {'FORNECEDOR':<{L_FORN}} | {'CPF/CNPJ':<{L_DOC}} | {'TOTAL':<{L_TOTAL}} | {'STATUS':<{L_STATUS}}")
        print("─" * TAM_TOTAL)

        for c in compras:
            id_c = self.ler_dados(c, ['id'])
            # Formata data resumida para caber
            data = self.ler_dados(c, ['data_emissao'])[:10]
            forn = self.ler_dados(c, ['fornecedor_nome_snap'])[:L_FORN]
            # O documento vem do JOIN que fizemos no repositório
            doc = self.ler_dados(c, ['forn_doc']) or "N/A"
            total = self.ler_dados(c, ['valor_total'])
            status = self.ler_dados(c, ['status'])

            print(
                f"{id_c:<{L_ID}} | "
                f"{data:<{L_DATA}} | "
                f"{forn:<{L_FORN}} | "
                f"{doc:<{L_DOC}} | "
                f"R${total:>9.2f} | "
                f"{status:<{L_STATUS}}"
            )

        print("═" * TAM_TOTAL)
        input("\n[Pressione Enter para voltar]")





    def revisar_pedido_para_entrada(self):
        print("\n--- REVISÃO DE PEDIDO (NF) ---")
        id_c = input("👉 ID do Pedido: ").strip()
        compra_db = self.repo.db.fetch_one("SELECT * FROM compras WHERE id = ?", (id_c,))
        if not compra_db: return print("❌ Não encontrado.")

        itens_db = self.repo.buscar_itens_por_compra(id_c)
        itens_revisados = []

        for i in itens_db:
            nome = self.ler_dados(i, ['produto_nome_snap']) or "Sem Nome"
            print(f"\n📦 Item: {nome}")
            qtd_orig = self.ler_dados(i, ['quantidade'])
            qtd_in = input(f"   Qtd [{qtd_orig}]: ").strip().replace(',', '.')
            nova_qtd = float(qtd_in) if qtd_in else float(qtd_orig)

            prec_orig = self.ler_dados(i, ['preco_custo'])
            prec_in = input(f"   Preço [R$ {float(prec_orig):.2f}]: ").strip().replace(',', '.')
            novo_prec = float(prec_in) if prec_in else float(prec_orig)
            itens_revisados.append(CompraItem(i['produto_id'], nome, nova_qtd, novo_prec))

        novo_total = sum(it.subtotal for it in itens_revisados)
        print(f"\n💰 NOVO TOTAL: R$ {novo_total:.2f}")

        # REVISÃO FINANCEIRA COMPLETA
        alterar_f = input(f"   Alterar Forma [{compra_db['forma_pagamento']}]? (S/N): ").upper()
        forma = self.escolher_forma_pagamento() if alterar_f == 'S' else compra_db['forma_pagamento']

        parc_in = input(f"   Parcelas [{compra_db['qtde_parcelas']}]: ").strip()
        novas_parc = int(parc_in) if parc_in else compra_db['qtde_parcelas']

        int_in = input(f"   Intervalo [{compra_db['intervalo_dias']}]: ").strip()
        novo_int = int(int_in) if int_in else compra_db['intervalo_dias']

        nova_obs = input(f"   Obs/NF [{compra_db['observacao']}]: ").strip() or compra_db['observacao']

        if input("\n⚠️ Confirmar Atualização? (S/N): ").upper() == 'S':
            self.repo.atualizar_itens_compra(id_c, itens_revisados)
            self.repo.atualizar_valores_compra(id_c, novo_total, forma, novas_parc, novo_int)
            self.repo.db.execute("UPDATE compras SET observacao = ? WHERE id = ?", (nova_obs, id_c))
            print("✅ Pedido e Financeiro atualizados!")

    def visualizar_detalhes_pedido(self):
        id_c = input("\n🔎 ID do pedido: ")
        c = self.repo.db.fetch_one("SELECT * FROM compras WHERE id = ?", (id_c,))
        if not c: return print("❌ Não encontrado.")
        print(f"\n📄 PEDIDO #{c['id']} | NF: {c['observacao']}")
        print(f"👤 Fornecedor: {c['fornecedor_nome_snap']}")
        print(f"💳 Pagamento: {c['forma_pagamento']} | {c['qtde_parcelas']}x | {c['intervalo_dias']} dias")
        print("-" * 65)
        itens = self.repo.buscar_itens_por_compra(id_c)
        for it in itens:
            nome = self.ler_dados(it, ['produto_nome_snap'])
            print(f"  - {nome[:30]:<30} | Qtd: {it['quantidade']:>6.2f} | R$ {it['subtotal']:>10.2f}")
        print("-" * 65)
        print(f"💰 TOTAL GERAL: R$ {c['valor_total']:>10.2f}")
        input("\n[ENTER] para voltar...")

    def gerenciar_fluxo_compra(self):
        id_c = input("\n👉 ID da Compra: ")
        novo = input("Novo Status (LIBERADO/CANCELADO/FATURADO): ").upper()
        self.repo.atualizar_status(id_c, novo)

    def processar_recebimento(self):
        id_c = input("\n👉 ID da Compra para ENTRADA: ")
        compra = self.repo.db.fetch_one("SELECT status FROM compras WHERE id = ?", (id_c,))
        if not compra or compra['status'] == 'ENTRADA': return print("❌ Já processado ou não encontrado.")
        itens = self.repo.buscar_itens_por_compra(id_c)
        if input(f"Confirmar entrada de {len(itens)} itens? (S/N): ").upper() == 'S':
            for i in itens:
                self.repo.db.execute("UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?",
                                     (i['quantidade'], i['produto_id']))
            self.repo.atualizar_status(id_c, "ENTRADA")
            print("✅ Sucesso! Estoque atualizado.")

    def excluir_pedido_compra(self):
        id_c = input("\n🗑️  ID para EXCLUIR: ")
        if input("⚠️  CERTEZA? (S/N): ").upper() == 'S':
            self.repo.excluir_pedido(id_c)
            print("✅ Removido.")

    def consultar_todos_pedidos(self):
        """
        CONSULTA MESTRE: Lista todos os pedidos de compra com detalhes financeiros.
        Independente de filtros, mostra o panorama completo do banco.
        """
        try:
            # Busca direta no banco para garantir que nada seja suprimido por filtros de repositório
            sql = """
                SELECT id, data_emissao, fornecedor_nome_snap, valor_total, status, forma_pagamento 
                FROM compras 
                ORDER BY id DESC
            """
            pedidos = self.repo.db.fetch_all(sql)

            if not pedidos:
                print("\n⚠️ Nenhum pedido de compra encontrado no sistema.")
                return input("\n[Pressione Enter para voltar]")

            # Definição de Larguras para alinhamento perfeito
            L_ID = 5
            L_DATA = 18
            L_FORN = 30
            L_TOTAL = 15
            L_STATUS = 12
            L_PGTO = 15
            TAM_TOTAL = 105

            print("\n" + "═" * TAM_TOTAL)
            print(f"{'RELATÓRIO GERAL DE PEDIDOS DE COMPRA':^105}")
            print("═" * TAM_TOTAL)

            # Cabeçalho
            header = (
                f"{'ID':<{L_ID}} | "
                f"{'DATA EMISSÃO':<{L_DATA}} | "
                f"{'FORNECEDOR':<{L_FORN}} | "
                f"{'FORMA PGTO':<{L_PGTO}} | "
                f"{'STATUS':<{L_STATUS}} | "
                f"{'TOTAL':>{L_TOTAL}}"
            )
            print(header)
            print("─" * TAM_TOTAL)

            soma_geral = 0.0

            for p in pedidos:
                id_p = f"{p['id']:03d}"
                data = p['data_emissao']
                forn = (p['fornecedor_nome_snap'] or "N/A")[:L_FORN]
                pgto = (p['forma_pagamento'] or "N/A")[:L_PGTO]
                status = p['status']
                total = p['valor_total'] if p['valor_total'] else 0.0
                soma_geral += total

                print(
                    f"{id_p:<{L_ID}} | "
                    f"{data:<{L_DATA}} | "
                    f"{forn:<{L_FORN}} | "
                    f"{pgto:<{L_PGTO}} | "
                    f"{status:<{L_STATUS}} | "
                    f"R$ {total:>{L_TOTAL - 3}.2f}"
                )

            print("─" * TAM_TOTAL)
            print(f"{'VALOR TOTAL ACUMULADO EM COMPRAS:':>{TAM_TOTAL - L_TOTAL}} R$ {soma_geral:>{L_TOTAL - 3}.2f}")
            print("═" * TAM_TOTAL)

            input("\n[Pressione Enter para voltar ao menu]")

        except Exception as e:
            print(f"\n❌ Erro ao gerar consulta de pedidos: {e}")
            input()