from datetime import datetime
from models.compra import Compra, CompraItem


class CompraService:
    def __init__(self, compra_repo, ent_repo, prod_repo, repo_config):
        self.repo = compra_repo
        self.ent_repo = ent_repo
        self.prod_repo = prod_repo
        self.repo_config = repo_config

    def ler_dados(self, obj, chaves):
        """Auxiliar para ler dados de dicionários ou objetos"""
        for c in chaves:
            if isinstance(obj, dict):
                if c in obj: return obj[c]
            else:
                if hasattr(obj, c): return getattr(obj, c)
        return ""

    def exibir_menu(self):
        while True:
            print("\n" + "=" * 45)
            print("      📦 MÓDULO DE COMPRAS")
            print("=" * 45)
            print("1. 📝 Novo Pedido")
            print("2. 📋 Listar Compras")
            print("3. ⚙️  Alterar Status")
            print("4. 🚚 Recebimento (Entrada Estoque)")
            print("5. 🚚 Revisar pedido")
            print("6. 🚚 Consulta completa pedido e itens")
            print("7. 🚚 Deletar pedido")
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
            elif op == "0":
                break

    def novo_pedido_compra(self):
        print("\n--- NOVO PEDIDO DE COMPRA ---")

        # 1. Fornecedor
        termo = input("🔍 Buscar Fornecedor: ").strip()
        forns = self.ent_repo.buscar_flexivel(termo)
        if not forns: return print("❌ Fornecedor não encontrado.")

        for f in forns:
            print(f"  [{self.ler_dados(f, ['id'])}] {self.ler_dados(f, ['nome', 'nome_fantasia'])}")

        id_f = input("👉 ID Fornecedor: ")
        f_sel = self.ent_repo.buscar_por_id(id_f)
        if not f_sel: return print("❌ Seleção inválida.")

        # 2. Criar objeto Compra (Isso resolve o "unresolved reference")
        forn_nome = self.ler_dados(f_sel, ['nome', 'nome_fantasia'])
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Inicializamos a variável COMPRA aqui!
        compra = Compra(fornecedor_id=id_f, fornecedor_nome_snap=forn_nome,
                        tipo_compra="REVENDA", data_emissao=data_atual)

        # 3. Adicionar Itens
        while True:
            busca_p = input("\n📦 Produto (Nome/ID) [F p/ fechar]: ").strip()
            if busca_p.upper() == 'F': break

            prods = self.prod_repo.buscar_por_id_ou_descricao(busca_p)
            if not prods: continue

            for p in prods:
                print(f"  [{self.ler_dados(p, ['id'])}] {self.ler_dados(p, ['nome'])}")

            id_p = input("👉 ID Produto: ")
            # ... (dentro do loop de busca de produtos)
            p_sel = self.prod_repo.buscar_por_id(id_p)
            if not p_sel:
                print("❌ Produto não encontrado!")
                continue

            # CORREÇÃO AQUI:
            # Como sqlite3.Row não aceita .get(), acessamos como se fosse uma lista/dicionário
            try:
                nome_produto = p_sel['nome']
            except (KeyError, IndexError, TypeError):
                # Caso a coluna não se chame 'nome', tentamos 'descricao'
                try:
                    nome_produto = p_sel['descricao']
                except:
                    nome_produto = "Produto sem nome"

            qtd = float(input("   Quantidade: ").replace(',', '.'))
            custo = float(input("   Preço Custo Unit: ").replace(',', '.'))

            # Criando o item com o nome garantido
            item = CompraItem(
                produto_id=id_p,
                produto_nome_snap=nome_produto,
                quantidade=qtd,
                valor_unitario=custo
            )
            compra.adicionar_item(item)
            print(f"✅ Item '{nome_produto}' adicionado.")

        if not compra.itens: return

        # 4. Financeiro
        print("\n--- FINANCEIRO ---")
        if not compra.itens:
            return print("⚠️ Pedido vazio. Operação cancelada.")

            # --- NOVA PARTE: COLHER DADOS FINANCEIROS E NF ---
        print("\n" + "─" * 45)
        print(f"{'💳 DADOS FINANCEIROS DA COMPRA':^45}")
        print("─" * 45)

        # Usamos a função de colheita que criamos
        compra.forma_pagamento = self.escolher_forma_pagamento()

        try:
            compra.qtde_parcelas = int(input("🔢 Quantidade de Parcelas [1]: ") or 1)
            if compra.qtde_parcelas > 1:
                compra.intervalo_dias = int(input("📅 Intervalo entre parcelas (dias) [30]: ") or 30)
            else:
                compra.intervalo_dias = 0
        except ValueError:
            compra.qtde_parcelas = 1
            compra.intervalo_dias = 0

        # Aproveitamos para colher o número da NF ou uma observação
        compra.observacao = input("📝 Nº da Nota Fiscal / Obs: ").strip()

        # Finalização
        print(f"\n💰 TOTAL DA COMPRA: R$ {compra.valor_total:.2f}")
        print(f"💳 PAGAMENTO: {compra.forma_pagamento} em {compra.qtde_parcelas}x")

        if input("\n🚀 Confirmar e Salvar Pedido? (S/N): ").upper() == 'S':
            id_compra = self.repo.salvar(compra)
            if id_compra:
                print(f"✅ PEDIDO #{id_compra} GERADO!")

    def listar_compras_filtrado(self):
        print("\n" + "─" * 60)
        print(f"{'🔍 CONSULTA DE PEDIDOS DE COMPRA':^60}")
        print("─" * 60)

        # Captura o termo (pode ser o ID '3' ou o nome do fornecedor)
        termo_busca = input("👤 Buscar por Nome do fornecedor ou ID do pedido (Enter para todos): ").strip()

        print("🚦 Status: [1] DIGITADO [2] LIBERADO [3] ENTRADA [4] CANCELADO")
        st_op = input("👉 Escolha o status (ou Enter para todos): ")

        status_map = {"1": "DIGITADO", "2": "LIBERADO", "3": "ENTRADA", "4": "CANCELADO"}
        f_status = status_map.get(st_op)

        # CORREÇÃO AQUI: Passando 'busca' em vez de 'fornecedor'
        compras = self.repo.filtrar_compras(busca=termo_busca, status=f_status)

        if not compras:
            print("\n⚠️ Nenhum pedido encontrado.")
            return
        # Exibição dos resultados
        print("\n" + "═" * 90)
        print(f"{'ID':<4} | {'DATA':<16} | {'FORNECEDOR':<25} | {'TOTAL':<12} | {'STATUS':<12}")
        print("═" * 90)

        for c in compras:
            # Tratamento de segurança para dados vindos do SQLite Row
            id_c = c['id']
            data = c['data_emissao'] if 'data_emissao' in c.keys() else "N/A"
            forn = (c['fornecedor_nome_snap'] or "Desconhecido")[:25]
            total = c['valor_total']
            status = c['status']

            print(f"{id_c:<4} | {data:<16} | {forn:<25} | R${total:>9.2f} | {status:<12}")

        print("═" * 90)
        input("\nPressione [ENTER] para continuar...")
    def gerenciar_fluxo_compra(self):
        id_c = input("\n👉 ID da Compra para alterar status: ")
        print("Opções: LIBERADO, EFETUADO, FATURADO, EM TRANSITO, CANCELADO")
        novo = input("Novo Status: ").upper()
        if self.repo.atualizar_status(id_c, novo):
            print("✅ Status atualizado!")

    def processar_recebimento(self):
        print("\n--- RECEBIMENTO DE MERCADORIA ---")
        id_c = input("👉 ID da Compra para dar ENTRADA: ")
        compra_db = self.repo.db.fetch_one("SELECT * FROM compras WHERE id = ?", (id_c,))

        if not compra_db or compra_db['status'] == 'ENTRADA':
            return print("❌ Compra não encontrada ou já processada.")

        itens = self.repo.buscar_itens_por_compra(id_c)
        if input(f"Confirmar entrada de {len(itens)} itens no estoque? (S/N): ").upper() == 'S':
            for i in itens:
                sql = "UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?"
                self.repo.db.execute(sql, (i['quantidade'], i['produto_id']))

            self.repo.atualizar_status(id_c, "ENTRADA")
            print("✅ Sucesso! Estoque atualizado.")

    def revisar_pedido_para_entrada(self):
        print("\n" + "═" * 55)
        print(f"{'📝 REVISÃO DE PEDIDO PARA CONFERÊNCIA NF':^55}")
        print("═" * 55)

        id_c = input("👉 ID do Pedido para revisar: ").strip()

        # 1. Busca cabeçalho (usando índices para evitar erro de Row/get)
        compra_db = self.repo.db.fetch_one("SELECT * FROM compras WHERE id = ?", (id_c,))

        if not compra_db:
            return print("❌ Pedido não encontrado.")

        # Travas de segurança
        if compra_db['status'] == 'ENTRADA':
            return print("⚠️ Este pedido já foi finalizado no estoque e não pode ser revisado.")
        if compra_db['status'] == 'CANCELADO':
            return print("🚫 Pedidos cancelados não podem ser revisados.")

        # 2. Busca os itens salvos no banco
        itens_atuais = self.repo.buscar_itens_por_compra(id_c)
        if not itens_atuais:
            return print("⚠️ Este pedido não possui itens registrados.")

        itens_revisados = []

        print("\n💡 Instrução: Pressione [ENTER] para manter o valor atual.")

        # 3. Loop de conferência item a item
        for i in itens_atuais:
            # Tratamento de nome para casos onde o snapshot está vazio
            nome = i['produto_nome_snap'] if i['produto_nome_snap'] else "Produto sem Nome"
            print(f"\n📦 Item: {nome}")

            # Revisão de Quantidade
            qtd_input = input(f"   Quantidade [{i['quantidade']}]: ").strip().replace(',', '.')
            nova_qtd = float(qtd_input) if qtd_input else i['quantidade']

            # Revisão de Preço (Tentando preco_custo ou valor_unitario conforme o banco)
            try:
                preco_atual = i['preco_custo']
            except:
                preco_atual = i['valor_unitario']

            custo_input = input(f"   Preço Unit. [R$ {preco_atual:.2f}]: ").strip().replace(',', '.')
            novo_custo = float(custo_input) if custo_input else preco_atual

            # Criando o objeto CompraItem (Snapshot do nome é mantido)
            item_rev = CompraItem(
                produto_id=i['produto_id'],
                produto_nome_snap=nome,
                quantidade=nova_qtd,
                valor_unitario=novo_custo
            )
            itens_revisados.append(item_rev)

        # 4. Recalcular Total Geral
        novo_total = sum(item.subtotal for item in itens_revisados)
        print(f"\n" + "─" * 55)
        print(f"💰 NOVO TOTAL DO PEDIDO: R$ {novo_total:.2f}")
        print("─" * 55)

        # 5. Revisão Financeira e Nota Fiscal
        print("\n💳 DADOS FINANCEIROS")

        alterar_pgto = input(f"   Deseja alterar a forma [{compra_db['forma_pagamento']}]? (S/N): ").upper()
        forma = self.escolher_forma_pagamento() if alterar_pgto == 'S' else compra_db['forma_pagamento']

        parc_input = input(f"   Quantidade de Parcelas [{compra_db['qtde_parcelas']}]: ").strip()
        novas_parc = int(parc_input) if parc_input else compra_db['qtde_parcelas']

        num_nf = input(f"   Número da NF / Observação [{compra_db['observacao'] or ''}]: ").strip()
        nova_obs = num_nf if num_nf else compra_db['observacao']

        # 6. Finalização e Persistência
        confirmar = input("\n⚠️ Confirmar todos os ajustes no Pedido e na NF? (S/N): ").upper()

        if confirmar == 'S':
            try:
                # Sincroniza com o Repository
                # Passo A: Atualiza Itens (Deleta antigos e insere novos)
                self.repo.atualizar_itens_compra(id_c, itens_revisados)

                # Passo B: Atualiza o Cabeçalho (Total e Financeiro)
                self.repo.atualizar_valores_compra(
                    id_c,
                    novo_total,
                    forma,
                    novas_parc,
                    compra_db['intervalo_dias']
                )

                # Passo C: Grava o Número da NF no campo observação
                self.repo.db.execute("UPDATE compras SET observacao = ? WHERE id = ?", (nova_obs, id_c))

                print("\n✅ PEDIDO ATUALIZADO E EQUIPARADO À NF!")

                # Pergunta se já quer liberar
                if input("🔓 Deseja LIBERAR este pedido para recebimento agora? (S/N): ").upper() == 'S':
                    self.repo.atualizar_status(id_c, "LIBERADO")
                    print("✨ Status alterado para LIBERADO!")

            except Exception as e:
                print(f"❌ Erro ao salvar revisão: {e}")
        else:
            print("\n↩️ Revisão descartada. Nada foi alterado.")

    def escolher_forma_pagamento(self):
        formas = self.repo.buscar_formas_pagamento_ativas()
        if not formas:
            print("⚠️ Nenhuma forma de pagamento cadastrada. Usando 'DINHEIRO' por padrão.")
            return "DINHEIRO"

        print("\n--- 💳 SELECIONE A FORMA DE PAGAMENTO ---")
        for i, f in enumerate(formas, 1):
            print(f"   [{i}] {f['nome']}")

        try:
            op = int(input("👉 Escolha o número: "))
            if 1 <= op <= len(formas):
                return formas[op - 1]['nome']
        except ValueError:
            pass

        return formas[0]['nome']  # Retorna a primeira se houver erro

    def visualizar_detalhes_pedido(self):
        id_c = input("\n🔎 Digite o ID do pedido para ver detalhes: ")
        compra = self.repo.db.fetch_one("SELECT * FROM compras WHERE id = ?", (id_c,))

        if not compra:
            return print("❌ Pedido não encontrado.")

        # --- CABEÇALHO ---
        print("\n" + "═" * 60)
        print(f"{'📄 DETALHES DO PEDIDO #' + str(compra['id']):^60}")
        print("═" * 60)
        print(f"👤 Fornecedor: {compra['fornecedor_nome_snap']}")
        print(f"📅 Data: {compra['data_emissao']}   | Status: {compra['status']}")
        print(f"💳 Pagamento: {compra['forma_pagamento']} ({compra['qtde_parcelas']}x)")
        print(f"📝 Obs/NF: {compra['observacao']}")
        print("─" * 60)

        # --- ITENS ---
        itens = self.repo.buscar_itens_por_compra2(id_c)
        print(f"{'PRODUTO':<30} | {'QTD':>6} | {'UNIT':>10} | {'TOTAL':>10}")
        print("─" * 60)

        for it in itens:
            nome = it['produto_nome_snap'] or "Produto s/ nome"
            print(f"{nome[:30]:<30} | {it['quantidade']:>6.2f} | {it['preco_custo']:>10.2f} | {it['subtotal']:>10.2f}")

        print("─" * 60)
        print(f"{'💰 TOTAL GERAL:':<49} R$ {compra['valor_total']:>8.2f}")
        print("═" * 60)
        input("\n[ENTER] para voltar...")

    def excluir_pedido_compra(self):
        print("\n" + "❌" * 20)
        print(f"{'EXCLUSÃO DE PEDIDO':^40}")
        print("❌" * 20)

        id_c = input("\n🗑️ ID do pedido que deseja EXCLUIR: ").strip()

        # Busca o status antes para validar a regra de segurança
        compra = self.repo.db.fetch_one("SELECT status FROM compras WHERE id = ?", (id_c,))

        if not compra:
            return print("⚠️ Pedido não encontrado.")

        # Regra de Segurança: Não apagar o que já entrou no estoque
        if compra['status'] == "ENTRADA":
            return print("🚫 Proibido excluir: Este pedido já deu ENTRADA no estoque.")

        # Confirmação para evitar acidentes
        confirmar = input(f"⚠️ TEM CERTEZA que deseja apagar o pedido #{id_c} e todos os seus itens? (S/N): ").upper()

        if confirmar == 'S':
            sucesso = self.repo.excluir_pedido(id_c)
            if sucesso:
                print(f"✅ Pedido #{id_c} removido com sucesso!")
            else:
                print("❌ Falha ao tentar excluir o pedido.")