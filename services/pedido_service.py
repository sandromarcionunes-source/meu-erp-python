from datetime import datetime
from models.pedido import Pedido, PedidoItem
from models.constants import StatusCredito, SituacaoEstoque, SituacaoLogistica

class PedidoService:
    def __init__(self, pedido_repo, ent_repo, produto_repo, pag_repo, analise_service, config_repo=None):
        self.repo = pedido_repo
        self.ent_repo = ent_repo
        self.prod_repo = produto_repo
        self.pag_repo = pag_repo
        self.analisador = analise_service
        self.config_repo = config_repo

    def ler_dados(self, obj, chaves_possiveis):
        if obj is None: return ""
        if isinstance(obj, dict) or "Row" in str(type(obj)):
            for chave in chaves_possiveis:
                for c in [chave, chave.upper(), chave.lower()]:
                    try:
                        if obj[c] is not None: return obj[c]
                    except:
                        continue
        for chave in chaves_possiveis:
            for c in [chave, chave.upper(), chave.lower()]:
                val = getattr(obj, c, None)
                if val is not None: return val
        return ""

    def exibir_menu(self):
        while True:
            print("\n" + "═" * 60)
            print(f"{'🛒 GESTÃO DE VENDAS COMPLETA':^60}")
            print("═" * 60)
            print("1. 📝 Novo Pedido")
            print("2. 📋 Listar Todos")
            print("3. 🗑️  Excluir e Estornar")
            print("0. ⬅️  Sair")
            op = input("\nEscolha: ")
            if op == "1":
                self.novo_pedido()
            elif op == "2":
                self.listar_pedidos()
            elif op == "3":
                self.excluir_pedido()
            elif op == "0":
                break

    def novo_pedido(self):
        print("\n" + "─" * 20 + " NOVO PEDIDO " + "─" * 20)

        tipo_op = input("Tipo: (V)enda ou (O)rçamento: ").upper()

        movimenta = "N"
        if tipo_op == "V":
            movimenta = input("📦 Movimentar/Baixar estoque fisicamente agora? (S/N): ").upper()[0]


        termo = input("🔍 Buscar Cliente (Nome/ID): ").strip()

        clis = self.repo.buscar_cliente_para_pedido(termo=termo)
        if not clis: return print("❌ Não encontrado.")

        for c in clis:
            id_c = self.ler_dados(c, ['id'])
            nome_c = self.ler_dados(c, ['nome_fantasia', 'razao_social', 'nome'])
            print(f"   ID: {id_c} | {nome_c}")

        id_cli = input("\n👉 ID Cliente: ").strip()

        # 🚨 ATENÇÃO: Chamamos o banco, que pode retornar uma LISTA de 1 item.
        resultado_busca = self.repo.buscar_cliente_para_pedido(id_exato=id_cli)

        # 🛠️ CONSERTO 1: Garantimos que 'ent' seja o OBJETO e não uma LISTA []
        if isinstance(resultado_busca, list) and len(resultado_busca) > 0:
            ent = resultado_busca[0]
        else:
            ent = resultado_busca

        if not ent:
            print("❌ Seleção inválida.")
            return

        # Criando o pedido
        pedido = Pedido(entidade_id=id_cli, data_emissao=datetime.now().strftime("%d/%m/%Y %H:%M"))

        # Preenchendo snapshots usando o 'ent' já extraído da lista acima
        pedido.cliente_nome_snap = self.ler_dados(ent, ['nome_fantasia', 'razao_social', 'nome'])
        pedido.cliente_documento_snap = self.ler_dados(ent, ['documento', 'cpf_cnpj'])
        pedido.cliente_endereco_snap = self.ler_dados(ent, ['endereco', 'logradouro'])
        pedido.cliente_email_snap = self.ler_dados(ent, ['email_comercial', 'email'])

        # Loop de Produtos
        while True:
            busca = input("\n📦 Produto (F para finalizar): ").strip()
            if busca.upper() == 'F': break

            prods = self.prod_repo.buscar_por_id_ou_descricao(busca)
            if not prods:
                print("❌ Produto não encontrado.")
                continue
            for p in prods:
                m_list = self.ler_dados(p, ['modelo_versao', 'modelo'])
                # Fazemos o cálculo em tempo real (Estoque Lógico)
                fisico = p.estoque_atual
                reservado = p.estoque_reservado
                disponivel = fisico - reservado

                print(f"   [ID: {p.id}] {p.nome} {m_list}")
                print(f"   💰 R$ {p.preco_venda:.2f} | ✅ DISPONÍVEL: {disponivel} (No pátio: {fisico})")

            id_p = input("👉 ID Produto: ").strip()
            p_sel = self.prod_repo.buscar_por_id(id_p)
            if p_sel:
                modelo_sel = self.ler_dados(p_sel, ['modelo_versao', 'modelo'])
                print(f"   Selecionado: {p_sel.nome} {modelo_sel}")
                qtd = float(input(f"   Quantidade: ").replace(',', '.') or 1)
                preco_in = input(f"   Preço Unit. [R$ {p_sel.preco_venda:.2f}]: ").strip().replace(',', '.')
                preco = float(preco_in) if preco_in else p_sel.preco_venda
                desc = float(input("   Desconto Unit. R$: ").replace(',', '.') or 0)
                nome_completo_venda = f"{p_sel.nome} {modelo_sel}".strip()
                pedido.adicionar_item(PedidoItem(
                    produto_id=p_sel.id,
                    produto_nome_snap=nome_completo_venda,
                    quantidade=qtd,
                    preco_venda=preco,
                    desconto=desc
                ))
                print("✅ Adicionado.")

        if not pedido.itens: return print("⚠️ Pedido vazio.")

        # Frete e Pagamento
        val_frete = input("\n🚚 Frete R$ [0]: ").strip().replace(',', '.')
        pedido.valor_frete = float(val_frete) if val_frete else 0.0

        formas = self.pag_repo.listar_ativas()
        for f in formas: print(f"   [{self.ler_dados(f, ['id'])}] {self.ler_dados(f, ['nome'])}")

        id_pgto = input("👉 ID Pagamento: ").strip()
        f_sel = self.pag_repo.buscar_por_id(id_pgto)
        pedido.forma_pagamento = self.ler_dados(f_sel, ['nome']) if f_sel else "DINHEIRO"

        # 🔵 INCLUSÃO SOLICITADA: Parcelamento
        # 🔵 INCLUSÃO: Parcelas e Prazo (Sempre pergunta o intervalo)
        pedido.total_parcelas = int(input("   Total de Parcelas [1]: ") or 1)
        pedido.intervalo_dias = int(
            input(f"   Prazo/Intervalo em dias [{pedido.intervalo_dias}]: ") or pedido.intervalo_dias)

        pedido.calcular_totais()


###############PAREI AQUI#########
        # ⚖️ ANÁLISE DE CRÉDITO
        print("\n⚖️  Analisando crédito...")

        # 🛠️ CONSERTO 2: Passamos o ID_CLI para o avaliador, não o objeto 'ent'
        # O motor de análise vai usar esse ID para buscar os dados frescos no banco.
        analise = self.analisador.avaliar(id_cli, pedido.valor_total_pedido)

        if analise.aprovado:
            pedido.status_credito = StatusCredito.APROVADO

        pedido.status_credito = StatusCredito.APROVADO if analise.aprovado else StatusCredito.BLOQUEADO
        if tipo_op == "O":
            pedido.situacao_estoque = SituacaoEstoque.NAO_MOVIMENTADO
        elif tipo_op == "V":
            if movimenta == "S":
                pedido.situacao_estoque = SituacaoEstoque.BAIXADO
            else:
                pedido.situacao_estoque = SituacaoEstoque.RESERVADO
        pedido.situacao_logistica = SituacaoLogistica.PENDENTE

        print(f"🚦 CRÉDITO: {pedido.status_credito} | ESTOQUE: {pedido.situacao_estoque}")
        print(f"📝 {analise.motivo}")



        if input("\n🚀 Confirmar Gravação? (S/N): ").upper() == 'S':
            id_f = self.repo.salvar(pedido)
            if id_f:
                print(f"✅ Pedido #{id_f} gravado!")
            else:
                print("❌ Erro ao gravar no banco de dados.")

    def listar_pedidos(self):
        # 🟢 Usa o seu repository para buscar a lista simplificada
        pedidos = self.repo.listar_todos()

        print("\n" + "═" * 70)
        print(f"{'📋 LISTAGEM DE PEDIDOS':^70}")
        print("═" * 70)
        print(f"{'ID':<4} | {'CLIENTE':<25} | {'TOTAL':>12} | {'CRÉDITO':<15}")
        print("-" * 70)

        for p in pedidos:
            pid = self.ler_dados(p, ['id'])
            cli = self.ler_dados(p, ['cliente_nome_snap'])
            tot = self.ler_dados(p, ['valor_total_pedido'])
            st_c = self.ler_dados(p, ['status_credito'])

            print(f"{pid:<4} | {cli[:25]:<25} | R${tot:>10.2f} | {st_c}")

        # 🟡 Atalho inteligente: Após listar, já oferece a impressão
        op = input("\n🖨️  Deseja imprimir os detalhes de algum ID? (S/N): ").upper()
        if op == 'S':
            id_imp = input("👉 Digite o ID do Pedido: ")
            self.imprimir_pedido_detalhado(id_imp)

    def imprimir_pedido_detalhado(self, pedido_id):
        # 🔍 1. Busca o cabeçalho (dados do cliente e totais)
        cabecalho = self.repo.buscar_por_id(pedido_id)
        if not cabecalho:
            return print("❌ Erro: Pedido não encontrado!")

        # 🔍 2. Busca os itens (AQUI chamamos a sua função que já existe!)
        itens = self.repo.buscar_itens_por_pedido(pedido_id)

        # 🎨 3. "Desenha" o relatório na tela
        print("\n" + "█" * 65)
        print(f"{'📄 COMPROVANTE DE PEDIDO DETALHADO':^65}")
        print("█" * 65)

        # Dados da Venda
        print(f" PEDIDO: #{pedido_id:<10} DATA: {self.ler_dados(cabecalho, ['data_emissao'])}")
        print(f" CLIENTE: {self.ler_dados(cabecalho, ['cliente_nome_snap'])}")
        print(f" DOC/CPF: {self.ler_dados(cabecalho, ['cliente_documento_snap'])}")
        print("-" * 65)

        # Listagem de Itens (Onde aparece o Modelo_Versão que corrigimos)
        print(f"{'PRODUTO / MODELO':<35} {'QTD':>5} {'UNIT':>10} {'SUB':>11}")
        for it in itens:
            nome = self.ler_dados(it, ['produto_nome_snap'])
            qtd = self.ler_dados(it, ['quantidade'])
            prc = self.ler_dados(it, ['preco_venda'])
            sub = self.ler_dados(it, ['subtotal'])
            print(f"{nome[:33]:<35} {qtd:>5.1f} {prc:>10.2f} {sub:>11.2f}")

        print("-" * 65)

        # 💰 RESUMO FINANCEIRO (INCLUSÃO DO FRETE)
        # 🟢 Buscamos os valores individuais para somar no visual
        v_produtos = self.ler_dados(cabecalho, ['valor_total_produtos'])
        v_frete = self.ler_dados(cabecalho, ['valor_frete'])
        v_total = self.ler_dados(cabecalho, ['valor_total_pedido'])

        forma = self.ler_dados(cabecalho, ['forma_pagamento'])
        parc = self.ler_dados(cabecalho, ['total_parcelas'])
        prazo = self.ler_dados(cabecalho, ['intervalo_dias'])

        # Exibição discriminada
        print(f" TOTAL PRODUTOS:    R$ {v_produtos:>12.2f}")
        print(f" (+) VALOR FRETE:   R$ {v_frete:>12.2f}")
        print(f" TOTAL GERAL:       R$ {v_total:>12.2f}")
        print("-" * 65)

        # 💳 Condições de Pagamento
        print(f" FORMA PAGAMENTO:   {forma}")
        print(f" CONDIÇÃO:          {parc} parcela(s) com intervalo de {prazo} dias")

        # 🚦 Status do Fluxo
        st_c = self.ler_dados(cabecalho, ['status_credito'])
        st_e = self.ler_dados(cabecalho, ['situacao_estoque'])
        print(f" STATUS CRÉDITO:    {st_c}")
        print(f" STATUS ESTOQUE:    {st_e}")
        print("█" * 65 + "\n")

    def excluir_pedido(self):
        id_ped = input("\n🗑️ ID para excluir: ").strip()
        if self.repo.deletar_com_estorno(id_ped):
            print("✅ Excluído e estoque estornado!")
        else:
            print("❌ Pedido não encontrado ou erro ao excluir.")