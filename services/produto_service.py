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

    def selecionar_opcao(self, titulo: str, opcoes: dict) -> str:
        while True:
            print(f"\n--- {titulo} ---")
            for k, v in opcoes.items():
                print(f"{k}. {v}")
            esc = input("Selecione uma opção: ").strip()
            if esc in opcoes:
                return opcoes[esc]
            print("⚠️ Opção inválida!")

    def selecionar_opcao_chave(self, titulo: str, opcoes: dict) -> str:
        while True:
            print(f"\n--- {titulo} ---")
            for k, v in opcoes.items():
                print(f"{k}. {v}")
            esc = input("Selecione uma opção: ").strip()
            if esc in opcoes:
                return esc
            print("⚠️ Opção inválida!")




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
        print("\n" + "═" * 110)
        # Adicionamos o cabeçalho 'DISP.'
        print(f"{'SKU':<6} | {'DESCRIÇÃO':<40} | {'VENDA':>10} | {'ATUAL':>10} | {'RESV.':>10} | {'DISP.':>10}")
        print("─" * 110)

        for i in itens:
            desc = f"{i.nome} {i.marca or ''}".strip()

            # 🟢 A CONTA DIRETA: Pegamos os valores que já existem e subtraímos aqui
            disponivel = i.estoque_atual - i.estoque_reservado

            print(f"{i.codigo_interno:<6} | {desc[:40]:<40} | R${i.preco_venda:>8.2f} | "
                  f"{i.estoque_atual:>10.2f} | {i.estoque_reservado:>10.2f} | {disponivel:>10.2f}")


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
        print("\n" + "═" * 55 + f"\n{'📝 ALTERAÇÃO COM MARCAÇÃO VISUAL':^55}\n" + "═" * 55)
        sku = input("🔎 SKU para revisar (Ex: 0001): ").strip().upper()
        p = self.repo.buscar_por_codigo(sku)

        if not p:
            return print("❌ SKU não encontrado no sistema!")

        # 1. Backup para comparação
        original = {
            "Nome": p.nome,
            "Categoria": p.categoria,
            "Marca": p.marca,
            "Modelo": p.modelo_versao,  # 🛠️ Ajustado
            "NCM": p.ncm,
            "CEST": p.cest,
            "Origem": str(p.origem),
            "Peso Líq": p.peso_liquido,
            "Peso Bruto": p.peso_bruto,
            "Custo": p.preco_custo,
            "Venda": p.preco_venda,
            "Estoque": p.estoque_atual,
            "Ativo": p.ativo
        }

        print(f"\n📦 Editando SKU: {p.codigo_interno} - {p.nome}")
        try:
            p.nome = input(f"🏷️ Nome [{p.nome}]: ").strip().upper() or p.nome
            p.categoria = input(f"📂 Categoria [{p.categoria}]: ").strip().upper() or p.categoria
            p.marca = input(f"🔖 Marca [{p.marca}]: ").strip().upper() or p.marca
            p.modelo_versao = input(f"🚘 Modelo [{p.modelo_versao}]: ").strip().upper() or p.modelo_versao

            p.ncm = input(f"📜 NCM [{p.ncm}]: ").strip() or p.ncm
            p.cest = input(f"📑 CEST [{p.cest}]: ").strip() or p.cest

            opcoes_origem = {"0": "Nacional", "1": "Imp. Dir.", "2": "Adq. Int.", "3": "Nac >40%", "4": "Proc. Básico",
                             "5": "Nac <=40%", "6": "Imp. Dir s/ sim.", "7": "Adq. Int s/ sim.", "8": "Nac >70%"}
            print(f"🌍 Origem atual: {p.origem}")
            nova_ori = self.selecionar_opcao_chave("ALTERAR ORIGEM", opcoes_origem)
            p.origem = int(nova_ori) if nova_ori else p.origem

            p.peso_liquido = float(str(input(f"⚖️ Peso Líq [{p.peso_liquido}]: ")).replace(',', '.') or p.peso_liquido)
            p.peso_bruto = float(str(input(f"🏋️ Peso Bruto [{p.peso_bruto}]: ")).replace(',', '.') or p.peso_bruto)
            p.preco_custo = float(str(input(f"💵 Custo [{p.preco_custo}]: ")).replace(',', '.') or p.preco_custo)
            p.preco_venda = float(str(input(f"💰 Venda [{p.preco_venda}]: ")).replace(',', '.') or p.preco_venda)
            p.estoque_atual = float(str(input(f"📦 Estoque [{p.estoque_atual}]: ")).replace(',', '.') or p.estoque_atual)
            p.ativo = int(input(f"✅ Ativo (1/0) [{p.ativo}]: ") or p.ativo)

            # 2. Mapa de novos valores
            atualizado = {
                "Nome": p.nome,
                "Categoria": p.categoria,
                "Marca": p.marca,
                "Modelo": p.modelo_versao,
                "NCM": p.ncm,
                "CEST": p.cest,
                "Origem": p.origem,
                "Peso Líq": p.peso_liquido,
                "Peso Bruto": p.peso_bruto,
                "Custo": p.preco_custo,
                "Venda": p.preco_venda,
                "Estoque": p.estoque_atual,
                "Ativo": p.ativo
            }

            # 3. Exibição da Marcação Visual de Alterações
            print("\n" + "─" * 55)
            print(f"{'🔍 RESUMO DAS ALTERAÇÕES':^55}")
            print("─" * 55)
            print(f"{'CAMPO':<15} | {'DE (ANTERIOR)':<17} | {'PARA (NOVO)':<17}")
            print("─" * 55)

            alterou = False
            for campo in original:
                if str(original[campo]) != str(atualizado[campo]):
                    print(f"⚠️ {campo:<13} | {str(original[campo]):<17} | {str(atualizado[campo]):<17} 🔄")
                    alterou = True

            if not alterou:
                print(f"{'Nenhuma alteração realizada.':^55}")
                print("─" * 55)
                return

            confirmar = input("\n💾 Confirma as alterações acima? (S/N): ").upper().strip()
            if confirmar == 'S':
                self.repo.atualizar(p)
                print("\n✅ CADASTRO ATUALIZADO COM SUCESSO!")
            else:
                print("\n❌ OPERAÇÃO CANCELADA PELO CEO.")

        except ValueError:
            print("\n❌ ERRO: Verifique os valores numéricos. Alteração cancelada.")
