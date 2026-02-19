from datetime import datetime
from models.pedido import Pedido, PedidoItem
from models.constants import StatusPedido


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
            for p in prods: print(f"   [ID: {p.id}] {p.nome} | R${p.preco_venda:.2f}")

            id_p = input("👉 ID Produto: ").strip()
            p_sel = self.prod_repo.buscar_por_id(id_p)
            if p_sel:
                qtd = float(input(f"   Quantidade: ").replace(',', '.') or 1)
                preco_in = input(f"   Preço Unit. [R$ {p_sel.preco_venda:.2f}]: ").strip().replace(',', '.')
                preco = float(preco_in) if preco_in else p_sel.preco_venda
                desc = float(input("   Desconto Unit. R$: ").replace(',', '.') or 0)

                pedido.adicionar_item(PedidoItem(p_sel.id, p_sel.nome, qtd, preco, desc))
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

        pedido.calcular_totais()

        # ⚖️ ANÁLISE DE CRÉDITO
        print("\n⚖️  Analisando crédito...")

        # 🛠️ CONSERTO 2: Passamos o ID_CLI para o avaliador, não o objeto 'ent'
        # O motor de análise vai usar esse ID para buscar os dados frescos no banco.
        analise = self.analisador.avaliar(id_cli, pedido.valor_total_pedido)

        # Define status com base no veredito
        pedido.status = StatusPedido.APROVADO_AUTO if analise.aprovado else StatusPedido.BLOQUEADO_CREDITO
        print(f"🚦 STATUS: {pedido.status} | {analise.motivo}")

        if input("\n🚀 Confirmar Gravação? (S/N): ").upper() == 'S':
            id_f = self.repo.salvar(pedido)
            if id_f:
                print(f"✅ Pedido #{id_f} gravado!")
            else:
                print("❌ Erro ao gravar no banco de dados.")

    def listar_pedidos(self):
        pedidos = self.repo.listar_todos()
        print("\n" + "─" * 60)
        for p in pedidos:
            pid = self.ler_dados(p, ['id'])
            cli = self.ler_dados(p, ['cliente_nome_snap'])
            tot = self.ler_dados(p, ['valor_total_pedido'])
            st = self.ler_dados(p, ['status'])
            print(f"ID: {pid} | {cli[:20]:<20} | R$ {tot:>8.2f} | {st}")

    def excluir_pedido(self):
        id_ped = input("\n🗑️ ID para excluir: ").strip()
        if self.repo.deletar_com_estorno(id_ped):
            print("✅ Excluído e estoque estornado!")
        else:
            print("❌ Pedido não encontrado ou erro ao excluir.")