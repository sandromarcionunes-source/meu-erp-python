from datetime import datetime
from random import randint


class NotaFiscalService:
    def __init__(self, nf_repo, emissor_repo, pedido_repo, produto_repo):
        self.nf_repo = nf_repo
        self.emissor_repo = emissor_repo
        self.pedido_repo = pedido_repo
        self.produto_repo = produto_repo

    def exibir_menu(self) -> None:
        while True:
            print("\n" + "═" * 50)
            print(f"{'📑 MÓDULO DE NOTA FISCAL (NFe)':^50}")
            print("═" * 50)
            print("1. 🚀 Faturar Pedido (Gerar Nova Nota)")
            print("2. 🔍 Consultar Nota por Número")
            print("3. 📋 Listar Todas as Notas Emitidas")
            print("0. ⬅️  Voltar ao Menu Principal")

            opcao = input("\nEscolha uma opção: ")

            if opcao == "1":
                self._fluxo_emissao_nota()
            elif opcao == "2":
                self._fluxo_consulta_nota()
            elif opcao == "3":
                self._fluxo_listagem_notas()
            elif opcao == "0":
                break

    def gerar_chave_acesso(self, cnpj: str) -> str:
        cnpj_aux = str(cnpj) if cnpj else ""
        cnpj_limpo = "".join([char for char in cnpj_aux if char.isdigit()]).zfill(14)
        data = datetime.now().strftime("%y%m")
        aleatorio = "".join([str(randint(0, 9)) for _ in range(22)])
        return f"35{data}{cnpj_limpo}55001{aleatorio}"

    def faturar_pedido_detalhado(self, pedido_id: int):
        """
        MÉTODO INTEGRAL E CORRIGIDO:
        Converte Pedido em NF-e com snapshots e baixa de estoque.
        """
        try:
            # 1. Coleta de Dados
            emissor = self.emissor_repo.buscar()
            pedido_raw = self.pedido_repo.buscar_por_id(pedido_id)
            itens_pedido_raw = self.pedido_repo.buscar_itens_por_pedido(pedido_id)

            # 2. Validações Iniciais
            if not emissor:
                print("❌ Erro: Dados do Emissor (sua empresa) não configurados.")
                return None
            if not pedido_raw:
                print(f"❌ Erro: Pedido ID {pedido_id} não encontrado no banco.")
                return None
            if not itens_pedido_raw:
                print(f"❌ Erro: Pedido ID {pedido_id} não possui itens cadastrados.")
                return None

            # 🟢 NORMALIZAÇÃO: Converter Pedido (Row/Objeto) para Dicionário Real
            p = dict(pedido_raw) if not isinstance(pedido_raw, dict) else pedido_raw
            # Caso as chaves venham em maiúsculo do banco, normalizamos para minúsculo
            p = {k.lower(): v for k, v in p.items()}

            print(f"⚙️  Processando faturamento do Pedido {pedido_id}...")

            lista_final_itens = []
            p_bruto_total = 0.0
            p_liquido_total = 0.0

            # 3. Processamento dos Itens (Snapshot de Produto e Pesos)
            for item_row in itens_pedido_raw:
                # 🟢 CONVERSÃO: Cada item da lista também deve virar dicionário
                item = dict(item_row) if not isinstance(item_row, dict) else item_row
                item = {k.lower(): v for k, v in item.items()}

                prod_id = item.get('produto_id')
                prod = self.produto_repo.buscar_por_id(prod_id)

                if not prod:
                    print(f"⚠️ Alerta: Produto ID {prod_id} não localizado. Usando dados básicos do pedido.")
                    nome_prod = "PRODUTO NÃO IDENTIFICADO"
                    ncm = "00000000"
                    pb_u, pl_u = 0.0, 0.0
                else:
                    # Snapshot do cadastro de produtos
                    nome_prod = f"{prod.nome} {getattr(prod, 'marca', '')}".strip().upper()
                    ncm = getattr(prod, 'ncm', '00000000') or '00000000'
                    pb_u = float(getattr(prod, 'peso_bruto', 0.0) or 0.0)
                    pl_u = float(getattr(prod, 'peso_liquido', 0.0) or 0.0)

                nf_item = {
                    'produto_id': prod_id,
                    'nome': nome_prod,
                    'ncm': ncm,
                    'qtd': float(item.get('quantidade', 0)),
                    'valor_u': float(item.get('preco_venda', 0)),
                    'valor_t': float(item.get('subtotal', 0)),
                    'p_bruto_u': pb_u,
                    'p_liq_u': pl_u
                }

                lista_final_itens.append(nf_item)

                # Cálculo de pesos logísticos
                p_bruto_total += (nf_item['p_bruto_u'] * nf_item['qtd'])
                p_liquido_total += (nf_item['p_liq_u'] * nf_item['qtd'])

            # 4. Montagem do Cabeçalho da Nota
            cabecalho = {
                'pedido_id': pedido_id,
                'numero_nf': self.nf_repo.obter_proximo_numero(),
                'serie': 1,
                'chave_acesso': self.gerar_chave_acesso(emissor.cnpj),
                'data_emissao': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'emissor_razao': emissor.razao_social.upper(),
                'emissor_cnpj': emissor.cnpj,
                'emissor_ie': emissor.inscricao_estadual,
                # Snapshots do Cliente vindos do Pedido
                'cli_nome': p.get('cliente_nome_snap', 'CLIENTE NÃO IDENTIFICADO'),
                'cli_doc': p.get('cliente_documento_snap', ''),
                'cli_end': p.get('cliente_endereco_snap', ''),
                'v_prod': float(p.get('valor_total_produtos', 0)),
                'v_frete': float(p.get('valor_frete', 0)),
                'v_total': float(p.get('valor_total_pedido', 0)),
                'p_bruto': p_bruto_total,
                'p_liquido': p_liquido_total,
                'protocolo': f"135{randint(100000000, 999999999)}"
            }

            # 5. Persistência Final (Repository em Cascata)
            id_nf = self.nf_repo.salvar_completa(cabecalho, lista_final_itens)

            if id_nf:
                print("\n" + "═" * 50)
                print(f"✅ NF-e {cabecalho['numero_nf']} EMITIDA COM SUCESSO!")
                print(f"🔑 CHAVE: {cabecalho['chave_acesso']}")
                print(f"📊 STATUS: FATURADO | TOTAL: R$ {cabecalho['v_total']:.2f}")
                print("═" * 50)
                return id_nf

            return None

        except Exception as e:
            print(f"❌ Erro Crítico ao processar módulo Nota Fiscal Vendas: {e}")
            return None

    def _fluxo_emissao_nota(self):
        id_p = input("🔢 ID do Pedido: ").strip()
        if id_p: self.faturar_pedido_detalhado(int(id_p))

    def _fluxo_consulta_nota(self):
        num = input("🔍 Nº da NF: ").strip()
        res = self.nf_repo.db.fetch_one("SELECT id FROM notas_fiscais WHERE numero_nf = ?", (num,))
        if res:
            self._visualizar_espelho_nota(res['id'])
        else:
            print("⚠️ Não encontrada.")

    def _fluxo_listagem_notas(self):
        notas = self.nf_repo.db.fetch_all("SELECT * FROM notas_fiscais ORDER BY id DESC")
        for n in notas:
            print(f"NF: {n['numero_nf']} | {n['cliente_nome_snap'][:20]} | R${n['valor_total_nota']:.2f}")

    def _visualizar_espelho_nota(self, id_nf):
        dados = self.nf_repo.buscar_nota_completa(id_nf)

        if not dados:
            print("❌ Erro: Nota Fiscal não encontrada.")
            return

        nf = dados['cabecalho']
        itens = dados['itens']

        print("\n" + "═" * 80)
        print(f"{'DOCUMENTO AUXILIAR DE NOTA FISCAL ELETRÔNICA':^80}")
        print("═" * 80)

        # Bloco Emissor e Número
        print(f" EMISSOR: {nf['emissor_razao_snap'][:40]:<40} | NÚMERO: {nf['numero_nf']}")
        print(f" CNPJ: {nf['emissor_cnpj_snap']:<43} | SÉRIE:  {nf['serie']}")
        print(f" IE: {nf['emissor_ie_snap']:<45} | EMISSÃO: {nf['data_emissao']}")
        print("-" * 80)

        # Bloco Chave de Acesso
        print(f" CHAVE DE ACESSO: {nf['chave_acesso']}")
        print(f" PROTOCOLO: {nf['protocolo']} - {nf['status']}")
        print("-" * 80)

        # Bloco Destinatário
        print(f" DESTINATÁRIO: {nf['cliente_nome_snap']}")
        print(f" CPF/CNPJ: {nf['cliente_doc_snap']:<40} | END: {nf['cliente_end_snap'][:25]}")
        print("═" * 80)

        # Cabeçalho dos Itens
        print(f"{'PRODUTO':<40} | {'QTD':>5} | {'UN':>8} | {'TOTAL':>12}")
        print("-" * 80)

        for item in itens:
            nome = item['nome_produto_snap'][:38]
            qtd = item['quantidade']
            valor_u = item['valor_unitario']
            valor_t = item['valor_total_item']
            print(f"{nome:<40} | {qtd:>5} | {valor_u:>8.2f} | {valor_t:>12.2f}")

        print("-" * 80)

        # Totais
        print(f"{'TOTAL PRODUTOS:':>65} R$ {nf['valor_produtos']:>10.2f}")
        print(f"{'FRETE:':>65} R$ {nf['valor_frete']:>10.2f}")
        print(f"{'TOTAL DA NOTA:':>65} R$ {nf['valor_total_nota']:>10.2f}")
        print("═" * 80)

        input("\n[Pressione Enter para voltar ao menu]")