from datetime import datetime
from models.produto import Produto

REGRAS_ITEM = {
    '00': {'desc': 'MERCADORIA PARA REVENDA', 'ncm': True, 'venda': True, 'estoque': True},
    '01': {'desc': 'MATÉRIA-PRIMA', 'ncm': True, 'venda': False, 'estoque': True},
    '04': {'desc': 'PRODUTO ACABADO', 'ncm': True, 'venda': True, 'estoque': True},
    '07': {'desc': 'USO E CONSUMO', 'ncm': True, 'venda': False, 'estoque': True},
    '08': {'desc': 'ATIVO IMOBILIZADO', 'ncm': True, 'venda': False, 'estoque': True},
    '09': {'desc': 'SERVIÇO', 'ncm': False, 'venda': True, 'estoque': False},
}


class ProdutoService:
    def __init__(self, repository):
        self.repo = repository

    def menu(self):
        while True:
            print("\n" + "=" * 60)
            print("📦 GESTÃO INTEGRAL DE PRODUTOS")
            print("=" * 60)
            print("1. Cadastrar Novo Item")
            print("2. Listar Resumo (Estoque)")
            print("3. Consulta Detalhada (Pesos/Estoque/Fisica)")
            print("4. Alterar / Revisar Cadastro")
            print("0. Voltar")
            op = input("\nEscolha uma opção: ").strip()
            if op == "1":
                self.cadastrar()
            elif op == "2":
                self.listar()
            elif op == "3":
                self.consultar_detalhado()
            elif op == "4":
                self.alterar()
            elif op == "0":
                break

    def cadastrar(self):
        print("\n" + "─" * 20 + " NOVO CADASTRO " + "─" * 20)
        for k, v in REGRAS_ITEM.items():
            print(f"{k} - {v['desc']}")

        tipo = input("\nEscolha o Tipo [00]: ").strip() or "00"
        regra = REGRAS_ITEM.get(tipo, REGRAS_ITEM['00'])

        nome = input("Nome/Descrição: ").strip()
        unidade = input("Unidade [UN]: ").strip().upper() or "UN"
        cat = input("Categoria: ").strip() or None
        mar = input("Marca: ").strip() or None
        mod = input("Modelo/Versão: ").strip() or None

        try:
            ncm = input("NCM: ").strip() if regra['ncm'] else ""
            cest = input("CEST: ").strip()
            ori = int(input("Origem (0-Nacional) [0]: ") or 0)

            # --- CAMPOS DE PESO ADICIONADOS ---
            p_liq = float(input("Peso Líquido (KG) [0.0]: ").replace(',', '.') or 0)
            p_bru = float(input("Peso Bruto (KG) [0.0]: ").replace(',', '.') or 0)

            custo = float(input("Custo R$: ").replace(',', '.') or 0)
            venda = float(input("Venda R$: ").replace(',', '.') or 0) if regra['venda'] else 0
            est_ini = float(input("Estoque Inicial: ").replace(',', '.') or 0) if regra['estoque'] else 0
            est_min = float(input("Estoque Mínimo: ").replace(',', '.') or 0)
            obs = input("Observações: ").strip()

            p = Produto(
                tipo_item=tipo, nome=nome, unidade=unidade, categoria=cat, marca=mar, modelo_versao=mod,
                ncm=ncm, cest=cest, origem=ori, peso_liquido=p_liq, peso_bruto=p_bru,
                preco_custo=custo, preco_venda=venda, estoque_atual=est_ini,
                estoque_reservado=0.0, estoque_minimo=est_min,
                observacoes=obs, ativo=1, data_cadastramento=datetime.now().strftime("%d/%m/%Y %H:%M")
            )

            sku = self.repo.salvar(p)
            print(f"\n✅ Sucesso! SKU: {sku} cadastrado com pesos e estoque.")
        except ValueError:
            print("\n❌ Erro: Verifique os valores numéricos.")

    def listar(self):
        itens = self.repo.buscar_todos()
        print("\n" + "═" * 105)
        print(f"{'SKU':<6} | {'DESCRIÇÃO':<40} | {'VENDA':>10} | {'ATUAL':>10} | {'RESERV.':>10}")
        print("─" * 105)
        for i in itens:
            desc = f"{i.nome} {i.marca or ''}".strip()
            print(
                f"{i.codigo_interno:<6} | {desc[:40]:<40} | R${i.preco_venda:>8.2f} | {i.estoque_atual:>10.2f} | {i.estoque_reservado:>10.2f}")

    def consultar_detalhado(self):
        termo = input("\n🔎 SKU ou Nome: ").strip()
        produtos = self.repo.buscar_por_id_ou_descricao(termo)
        if not produtos: return print("⚠️ Não encontrado.")

        for p in produtos:
            disponivel = p.estoque_atual - p.estoque_reservado
            print("\n" + "═" * 60)
            print(f"📦 SKU: {p.codigo_interno} | {p.nome}")
            print(f"🔹 Marca: {p.marca or 'N/A'} | Modelo: {p.modelo_versao or 'N/A'}")
            print(f"🔹 NCM: {p.ncm} | CEST: {p.cest} | Origem: {p.origem}")
            print(f"🔹 Unidade: {p.unidade} | Categoria: {p.categoria or 'N/A'}")
            print("─" * 60)
            # EXIBIÇÃO DOS PESOS
            print(f"⚖️  PESO LÍQUIDO: {p.peso_liquido:>10.3f} KG")
            print(f"⚖️  PESO BRUTO:   {p.peso_bruto:>10.3f} KG")
            print("─" * 60)
            print(f"📈 ESTOQUE ATUAL:    {p.estoque_atual:>10.2f}")
            print(f"📉 ESTOQUE RESERVADO: {p.estoque_reservado:>10.2f}")
            print(f"✅ DISPONÍVEL VENDA:  {disponivel:>10.2f}")
            print(f"🔔 ESTOQUE MÍNIMO:    {p.estoque_minimo:>10.2f}")
            if disponivel <= p.estoque_minimo: print("⚠️  ALERTA: ESTOQUE BAIXO!")
            print("═" * 60)
        input("\n[ENTER] para voltar...")

    def alterar(self):
        sku = input("\n🔎 SKU para revisar: ").strip().upper()
        p = self.repo.buscar_por_codigo(sku)
        if not p: return print("❌ SKU não encontrado!")

        print(f"\nEditando: {p.nome}")
        try:
            p.nome = input(f"Nome [{p.nome}]: ").strip() or p.nome
            p.categoria = input(f"Categoria [{p.categoria}]: ").strip() or p.categoria

            # EDIÇÃO DE PESOS NA ALTERAÇÃO
            p.peso_liquido = float(input(f"Peso Líq [{p.peso_liquido}]: ").replace(',', '.') or p.peso_liquido)
            p.peso_bruto = float(input(f"Peso Bruto [{p.peso_bruto}]: ").replace(',', '.') or p.peso_bruto)

            p.preco_custo = float(input(f"Custo [{p.preco_custo}]: ").replace(',', '.') or p.preco_custo)
            p.preco_venda = float(input(f"Venda [{p.preco_venda}]: ").replace(',', '.') or p.preco_venda)
            p.estoque_atual = float(input(f"Estoque [{p.estoque_atual}]: ").replace(',', '.') or p.estoque_atual)
            p.ativo = int(input(f"Ativo (1/0) [{p.ativo}]: ") or p.ativo)

            self.repo.atualizar(p)
            print("\n✅ Cadastro atualizado com sucesso!")
        except ValueError:
            print("\n❌ Erro nos valores.")