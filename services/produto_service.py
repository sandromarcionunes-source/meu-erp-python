from datetime import datetime
from constants.item_types import REGRAS_ITEM
from models.produto import Produto


class ProdutoService:
    def __init__(self, repository):
        self.repo = repository

    def menu(self):
        while True:
            print("\n" + "=" * 40)
            print("📦 GESTÃO DE PRODUTOS (SKU AUTOMÁTICO)")
            print("=" * 40)
            print("1. Cadastrar Novo Item")
            print("2. Listar Todos")
            print("3. Revisar / Alterar por SKU")
            print("0. Voltar")
            op = input("Escolha: ")
            if op == "1":
                self.cadastrar()
            elif op == "2":
                self.listar()
            elif op == "3":
                self.alterar()
            elif op == "0":
                break

    def cadastrar(self):
        print("\n[ NOVO CADASTRO ]")
        for cod, info in REGRAS_ITEM.items():
            print(f"  {cod} - {info['desc']}")

        tipo = input("\nCódigo do tipo: ").strip()
        regra = REGRAS_ITEM.get(tipo)
        if not regra:
            print("❌ Erro: Tipo inválido!");
            return

        print("--- Dados do Item ---")
        nome = input("Nome/Descrição: ").strip()
        unidade = input("Unidade (UN/KG/PC/HR): ").strip().upper()

        try:
            ncm = input("NCM: ").strip() if regra['ncm'] else ""

            p_liq = 0.0
            p_bru = 0.0
            if tipo != "09":
                p_liq = float(input("Peso Líquido (kg): ") or 0)
                p_bru = float(input("Peso Bruto (kg): ") or 0)

            custo = float(input("Preço de Custo R$: ") or 0)
            venda = float(input("Preço de Venda R$: ") or 0) if regra['venda'] else 0
            est_ini = float(input("Estoque Inicial: ") or 0) if regra['estoque'] else 0
            est_min = float(input("Estoque Mínimo: ") or 0)
            obs = input("Observações: ").strip()

            # Criamos o objeto (codigo_interno vai vazio e o repositório preenche)
            novo_p = Produto(
                codigo_interno=None, tipo_item=tipo, nome=nome, unidade=unidade,
                ncm=ncm, peso_liquido=p_liq, peso_bruto=p_bru, preco_custo=custo,
                preco_venda=venda, estoque_atual=est_ini, estoque_reservado=0.0,
                estoque_minimo=est_min, observacoes=obs,
                data_cadastramento=datetime.now().strftime("%d/%m/%Y %H:%M"),
                ativo=1
            )

            gerado_id = self.repo.salvar(novo_p)
            print(f"\n✅ SUCESSO! Item cadastrado com SKU automático: {gerado_id}")

        except ValueError:
            print("❌ Erro: Valor numérico inválido!")

    def listar(self):
        itens = self.repo.buscar_todos()
        if not itens:
            print("\n⚠️ Nenhum item no sistema.");
            return

        print("\n" + "=" * 105)
        print(f"{'SKU/ID':<10} | {'NOME/DESCRIÇÃO':<35} | {'TIPO':<15} | {'ESTOQUE':<10} | {'RESERVA':<10}")
        print("-" * 105)
        for i in itens:
            t_desc = REGRAS_ITEM.get(i.tipo_item, {}).get('desc', 'N/A')
            print(f"{i.codigo_interno:<10} | {i.nome[:35]:<35} | {t_desc[:15]:<15} | {i.estoque_atual:<10.2f} | {i.estoque_reservado:<10.2f}")
        print("=" * 105)

    def alterar(self):
        print("\n🔍 REVISÃO DE CADASTRO")
        sku = input("Digite o SKU (ID) para revisar: ").strip().upper()
        p = self.repo.buscar_por_codigo(sku)

        if not p:
            print("❌ SKU não encontrado!");
            return

        regra = REGRAS_ITEM.get(p.tipo_item)
        print(f"\nEditando Item {p.codigo_interno}: {p.nome}")
        print("💡 [ENTER] mantém o atual | [DIGITE] para alterar\n")

        try:
            p.nome = input(f"Nome [{p.nome}]: ").strip() or p.nome
            p.unidade = input(f"Unidade [{p.unidade}]: ").strip().upper() or p.unidade

            if regra['ncm']:
                p.ncm = input(f"NCM [{p.ncm}]: ").strip() or p.ncm

            if p.tipo_item != "09":
                res_pl = input(f"Peso Líq [{p.peso_liquido}]: ").strip()
                p.peso_liquido = float(res_pl) if res_pl else p.peso_liquido
                res_pb = input(f"Peso Bruto [{p.peso_bruto}]: ").strip()
                p.peso_bruto = float(res_pb) if res_pb else p.peso_bruto

            res_custo = input(f"Custo R$ [{p.preco_custo}]: ").strip()
            p.preco_custo = float(res_custo) if res_custo else p.preco_custo

            if regra['venda']:
                res_venda = input(f"Venda R$ [{p.preco_venda}]: ").strip()
                p.preco_venda = float(res_venda) if res_venda else p.preco_venda

            res_min = input(f"Est. Mínimo [{p.estoque_minimo}]: ").strip()
            p.estoque_minimo = float(res_min) if res_min else p.estoque_minimo

            p.observacoes = input(f"Obs [{p.observacoes}]: ").strip() or p.observacoes

            self.repo.atualizar(p)
            print(f"\n✅ SKU {p.codigo_interno} atualizado com sucesso!")
        except ValueError:
            print("❌ Erro: Valor numérico inválido.")