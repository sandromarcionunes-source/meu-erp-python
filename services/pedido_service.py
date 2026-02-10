from datetime import datetime
from models.pedido import Pedido, PedidoItem


class PedidoService:
    def __init__(self, pedido_repo, entidade_repo, produto_repo, pagamento_repo, config_repo=None):
        self.repo = pedido_repo
        self.ent_repo = entidade_repo
        self.prod_repo = produto_repo
        self.pag_repo = pagamento_repo
        self.config_repo = config_repo

    def exibir_menu(self):
        while True:
            print("\n" + "═" * 45)
            print(f"{'🛒 MÓDULO DE VENDAS E PEDIDOS':^45}")
            print("═" * 45)
            print("1. 📝 Lançar Novo Pedido / Reserva")
            print("2. 📋 Listar Todos os Pedidos")
            print("3. 📋 Listar pedidos por filtro")
            print("4. 📋 Deletar Pedido com estorno do estoque")
            print("0. ⬅️  Voltar ao Menu Principal")

            op = input("\nEscolha uma opção: ")

            if op == "1":
                self.novo_pedido()
            elif op == "2":
                self.listar_pedidos()
            elif op == "3":
                self.listar_pedidos_filtro()
            elif op == "4":
                self.excluir_pedido()
            elif op == "0":
                break

    def ler_dados(self, obj, chaves_possiveis):
        if obj is None: return ""

        # Se for um dicionário ou SQLite Row
        if isinstance(obj, dict) or "Row" in str(type(obj)):
            for chave in chaves_possiveis:
                # Tenta a chave como está, em maiúsculo e em minúsculo
                for c in [chave, chave.upper(), chave.lower()]:
                    try:
                        if obj[c] is not None: return obj[c]
                    except:
                        continue

        # Se for um Objeto
        for chave in chaves_possiveis:
            for c in [chave, chave.upper(), chave.lower()]:
                val = getattr(obj, c, None)
                if val is not None: return val

        return "???"  # Se chegar aqui, realmente não achou nada

    def novo_pedido(self):
        print("\n--- INICIANDO NOVO PEDIDO ---")

        # 1. BUSCA DE CLIENTE
        termo_cli = input("🔍 Buscar Cliente (Nome ou Documento): ").strip()
        clientes = self.ent_repo.buscar_flexivel(termo_cli)

        if not clientes:
            print("❌ Cliente não encontrado!")
            return

        for c in clientes:
            cid = self.ler_dados(c, ['id', 'ID'])
            cnome = self.ler_dados(c, ['nome_fantasia', 'NOME_FANTASIA', 'nome', 'NOME'])
            print(f"   [{cid}] {cnome}")

        id_cli = input("\n👉 Digite o ID do Cliente: ").strip()
        ent = self.ent_repo.buscar_por_id(id_cli)
        if not ent:
            print("❌ Seleção inválida.")
            return

        # 2. INICIALIZA PEDIDO E CAPTURA SNAPS
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        pedido = Pedido(entidade_id=id_cli, data_emissao=data_atual)

        pedido.cliente_nome_snap = self.ler_dados(ent, ['nome_fantasia', 'nome'])
        pedido.cliente_documento_snap = self.ler_dados(ent, ['documento', 'cpf', 'cnpj'])
        pedido.cliente_endereco_snap = self.ler_dados(ent, ['endereco', 'logradouro'])
        pedido.cliente_email_snap = self.ler_dados(ent, ['email'])

        # 3. ADIÇÃO DE ITENS
        while True:
            busca_p = input("\n📦 Produto (Nome ou ID) [F p/ fechar]: ").strip()
            if busca_p.upper() == 'F': break

            produtos_encontrados = self.prod_repo.buscar_por_id_ou_descricao(busca_p)

            if not produtos_encontrados:
                print("❌ Produto não localizado.")
                continue

            for p in produtos_encontrados:
                pid = self.ler_dados(p, ['id', 'ID'])
                pnome = self.ler_dados(p, ['nome', 'NOME'])
                ppreco = self.ler_dados(p, ['preco_venda', 'PRECO_VENDA'])
                print(f"   [{pid}] {pnome} | Preço: R${ppreco}")

            id_p = input("👉 Confirme o ID do Produto: ").strip()
            p_sel = self.prod_repo.buscar_por_id(id_p)

            if not p_sel:
                print("⚠️ ID não encontrado.")
                continue

            try:
                # Captura dados finais do produto selecionado
                pid_f = self.ler_dados(p_sel, ['id', 'ID'])
                pnome_f = self.ler_dados(p_sel, ['nome', 'NOME'])
                ppreco_sug = float(self.ler_dados(p_sel, ['preco_venda', 'PRECO_VENDA']) or 0)

                qtd = float(input(f"   Quantidade: ").replace(',', '.'))
                preco_in = input(f"   Preço Unit. [R$ {ppreco_sug:.2f}]: ").strip()
                preco = float(preco_in.replace(',', '.')) if preco_in else ppreco_sug
                desc = float(input("   Desconto Unitário R$ [0]: ") or 0)

                # Cria o item garantindo que o ID não vá vazio
                if pid_f:
                    item = PedidoItem(pid_f, pnome_f, qtd, preco, desc)
                    pedido.adicionar_item(item)
                    print(f"✅ {pnome_f} adicionado!")
                else:
                    print("❌ Falha ao capturar dados do produto.")

            except Exception as e:
                print(f"❌ Erro nos valores do item: {e}")

        if not pedido.itens:
            print("⚠️ Pedido vazio. Operação cancelada.")
            return

        # --- 4. FINALIZAÇÃO E PAGAMENTO ---
        print("\n" + "─" * 40)
        print("⚙️  TIPO DE LANÇAMENTO:")
        print("1. SAÍDA IMEDIATA (Baixa Estoque)")
        print("2. RESERVA (Bloqueia p/ Veículos)")
        opcao_saida = input("Escolha [1]: ").strip() or "1"
        baixar_agora = True if opcao_saida == "1" else False

        print("\n💳 FORMAS DE PAGAMENTO DISPONÍVEIS:")
        formas = self.pag_repo.listar_ativas()
        if not formas:
            print("⚠️ Nenhuma forma de pagamento cadastrada! Usando 'DINHEIRO' por padrão.")
            pedido.forma_pagamento = "DINHEIRO"
        else:
            for f in formas:
                f_id = self.ler_dados(f, ['id', 'ID'])
                f_nome = self.ler_dados(f, ['nome', 'NOME', 'descricao'])
                print(f"   [{f_id}] {f_nome}")

            id_pgto = ""
            while not id_pgto:
                id_pgto = input("\n👉 Digite o ID da Forma de Pagamento: ").strip()
                pgto_sel = self.pag_repo.buscar_por_id(id_pgto)
                if pgto_sel:
                    pedido.forma_pagamento = self.ler_dados(pgto_sel, ['nome', 'descricao'])
                else:
                    print("❌ ID Inválido. Escolha uma forma da lista.")
                    id_pgto = ""

        # --- 5. LÓGICA DE PARCELAMENTO ---
        if pedido.forma_pagamento.upper() != "DINHEIRO":
            try:
                print(f"\n📝 Configuração de Prazo ({pedido.forma_pagamento}):")
                parc_in = input("   Quantidade de Parcelas [1]: ").strip()
                pedido.total_parcelas = int(parc_in) if parc_in else 1

                if pedido.total_parcelas > 1:
                    prazo_in = input("   Intervalo entre parcelas (dias) [30]: ").strip()
                    pedido.intervalo_dias = int(prazo_in) if prazo_in else 30
            except ValueError:
                print("⚠️ Entrada inválida. Definindo como 1 parcela à vista.")
                pedido.total_parcelas = 1
        else:
            pedido.total_parcelas = 1
            pedido.intervalo_dias = 0

        # --- 6. TOTAIS E CONFIRMAÇÃO ---
        val_frete = input("\n🚚 Valor do Frete R$ [0,00]: ").strip().replace(',', '.')
        pedido.valor_frete = float(val_frete) if val_frete else 0.0

        pedido.calcular_totais()

        print("\n" + "═" * 40)
        print(f"💰 RESUMO DO PEDIDO")
        print(f"   Cliente: {pedido.cliente_nome_snap}")
        print(f"   Pagamento: {pedido.forma_pagamento}")
        if pedido.total_parcelas > 1:
            v_parc = pedido.valor_total_pedido / pedido.total_parcelas
            print(
                f"   Parcelamento: {pedido.total_parcelas}x de R$ {v_parc:.2f} (a cada {pedido.intervalo_dias} dias)")
        print(f"   TOTAL A PAGAR: R$ {pedido.valor_total_pedido:.2f}")
        print("═" * 40)

        if input("\n🚀 Confirmar e Gravar Pedido? (S/N): ").upper() == 'S':
            id_final = self.repo.salvar(pedido, baixar_imediato=baixar_agora)
            if id_final:
                print(f"✅ PEDIDO #{id_final} FINALIZADO COM SUCESSO!")
            else:
                print("❌ Erro ao salvar no banco de dados.")

    def listar_pedidos(self):
        pedidos = self.repo.listar_todos()
        if not pedidos:
            print("\n📭 Nenhum pedido encontrado.")
            return

        print("\n" + "═" * 100)
        print(f"{'📋 RELATÓRIO DETALHADO DE VENDAS':^100}")
        print("═" * 100)

        for p in pedidos:
            pid = self.ler_dados(p, ['id', 'ID'])
            pdata = self.ler_dados(p, ['data_emissao'])
            pcli = str(self.ler_dados(p, ['cliente_nome_snap', 'nome'])).upper()
            ptotal = float(self.ler_dados(p, ['valor_total_pedido']) or 0)
            pstat = self.ler_dados(p, ['status'])
            ppag = self.ler_dados(p, ['forma_pagamento']).upper()
            pfrete = float(self.ler_dados(p, ['valor_frete']) or 0)

            # --- CABEÇALHO DO PEDIDO ---
            print(f"\n📦 PEDIDO: #{str(pid).zfill(4):<6} | DATA: {pdata:<16} | STATUS: {pstat}")
            print(f"👤 CLIENTE: {pcli}")
            print(f"💳 PGTO: {ppag:<18} | FRETE: R$ {pfrete:>8.2f} | TOTAL: R$ {ptotal:>9.2f}")

            # --- BUSCA ITENS ---
            itens = self.repo.buscar_itens_por_pedido(pid)
            if itens:
                print(f"   {'   ' + '─' * 82}")
                # Cabeçalho da tabela de itens com DESCONTO
                print(f"   {'   | PRODUTO':<38} | {'QTD':<6} | {'PREÇO':<10} | {'DESC.':<9} | {'SUBTOTAL'}")

                for i in itens:
                    nome = self.ler_dados(i, ['produto_nome_snap'])[:33]
                    qtd = float(self.ler_dados(i, ['quantidade']))
                    preco = float(self.ler_dados(i, ['preco_venda']))
                    desc = float(self.ler_dados(i, ['desconto']) or 0)
                    sub = float(self.ler_dados(i, ['subtotal']))

                    # Linha do item com alinhamento preciso
                    print(f"   {"   • " + nome:<38} | {qtd:<6.2f} | {preco:>10.2f} | {desc:>9.2f} | {sub:>10.2f}")

                print(f"   {'   ' + '─' * 82}")
            else:
                print("   ⚠️ (Nenhum item encontrado)")

            print("-" * 100)

        input("\nPressione [ENTER] para voltar ao menu...")

    def excluir_pedido(self):
        print("\n" + "─" * 45)
        print(f"{'🗑️  EXCLUIR E ESTORNAR PEDIDO':^45}")
        print("─" * 45)

        id_ped = input("👉 Digite o ID do pedido para exclusão: ").strip()
        if not id_ped: return

        # Pequena busca para confirmar dados na tela antes de deletar
        todos = self.repo.listar_todos()
        p_sel = next((p for p in todos if str(self.ler_dados(p, ['id', 'ID'])) == id_ped), None)

        if not p_sel:
            print("❌ Pedido não localizado.")
            return

        cliente = self.ler_dados(p_sel, ['cliente_nome_snap'])
        total = self.ler_dados(p_sel, ['valor_total_pedido'])
        status = self.ler_dados(p_sel, ['status'])

        print(f"\n⚠️  CONFIRMAÇÃO DE ESTORNO:")
        print(f"   Pedido: #{id_ped} | Cliente: {cliente}")
        print(f"   Status Atual: {status} | Valor: R$ {total:.2f}")
        print(f"\n   Isso devolverá os produtos ao estoque disponível.")

        confirma = input("\n❗ Confirmar exclusão definitiva? (S/N): ").upper()

        if confirma == 'S':
            if self.repo.deletar_com_estorno(id_ped):
                print(f"✅ Pedido #{id_ped} excluído e estoque atualizado!")
            else:
                print("❌ Falha na operação de banco de dados.")
        else:
            print("🚫 Operação abortada pelo usuário.")

    def listar_pedidos_filtro(self):
        print("\n" + "═" * 60)
        print(f"{'📋 CONSULTA DE PEDIDOS':^60}")
        print("═" * 60)
        print("Deixe em branco para ignorar o filtro.")

        f_cli = input("👤 Nome do cliente: ").strip()
        f_data = input("📅 Data (DD/MM/AAAA): ").strip()
        print("1. CONCLUIDO | 2. RESERVADO")
        f_status_op = input("🚦 Status (Opção): ").strip()

        f_status = ""
        if f_status_op == "1":
            f_status = "CONCLUIDO"
        elif f_status_op == "2":
            f_status = "RESERVADO"

        pedidos = self.repo.filtrar_pedidos(f_cli, f_data, f_status)

        if not pedidos:
            print("\n🔍 Nenhum pedido encontrado com esses filtros.")
            return

        print("\n" + "-" * 95)
        header = f"{'ID':<4} | {'DATA':<16} | {'CLIENTE':<25} | {'TOTAL':<12} | {'STATUS':<10} | {'PAGTO':<10}"
        print(header)
        print("-" * 95)

        for p in pedidos:
            pid = self.ler_dados(p, ['id', 'ID'])
            # Pega apenas a data, ignorando a hora se necessário
            pdata = self.ler_dados(p, ['data_emissao'])[:16]
            pcli = str(self.ler_dados(p, ['cliente_nome_snap']))[:25]
            ptotal = float(self.ler_dados(p, ['valor_total_pedido']) or 0)
            pstat = self.ler_dados(p, ['status'])
            ppag = self.ler_dados(p, ['forma_pagamento'])[:10]

            print(f"{pid:<4} | {pdata:<16} | {pcli:<25} | R${ptotal:>9.2f} | {pstat:<10} | {ppag:<10}")
        print("-" * 95)

        # Opção rápida para ver detalhes ou sair
        input("\nPressione [ENTER] para voltar...")