class DatabaseService:
    def __init__(self, db_manager):
        self.db = db_manager

    def exibir_menu(self):
        while True:
            print("\n" + "-" * 20)
            print("  MANUTENÇÃO DO BANCO")
            print("-" * 20)
            print("1. Criar/Verificar Tabelas")
            print("2. Listar Tabelas Existentes no ficheiro")
            print("3. Listar registros efetuados")
            print("4. Listar campos da tabela")
            print("0. Voltar")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                self.criar_tabelas()
            elif opcao == "2":
                self.consultar_tabelas()
            elif opcao == '3':
                self.consultar_dados_tabela()
            elif opcao == '4':
                self.inspecionar_estrutura()
            elif opcao == "0":
                break
            else:
                print('Opção incorreta, digite novamente')

    def criar_tabelas(self):
        print("Verificando estrutura do banco...")
        try:
            self.db.create_tables()
            print("✅ Tabelas processadas com sucesso!")
        except Exception as e:
            print(f"❌ Erro: {e}")

    def consultar_tabelas(self):
        print("\n🔍 Tabelas encontradas no banco de dados:")
        tabelas = self.db.listar_tabelas_reais()

        if not tabelas:
            print("⚠️ Nenhuma tabela encontrada!")
        else:
            for i, tabela in enumerate(tabelas, 1):
                # O fetchall retorna objetos Row, acessamos pelo índice ou nome
                print(f"   {i}. {tabela['name']}")

        input("\nPrima Enter para continuar...")

    def consultar_dados_tabela(self):
        tabela = input("\nQual tabela deseja consultar? ").strip()

        try:
            dados = self.db.fetch_all(f"SELECT * FROM {tabela}")

            if not dados:
                print(f"\n⚠️ A tabela '{tabela}' está vazia ou não existe.")
                return

            print(f"\n--- DADOS DA TABELA: {tabela.upper()} ---")

            # 1. Pega os nomes das colunas com segurança
            primeira_linha = dict(dados[0])
            colunas = primeira_linha.keys()
            header = " | ".join(colunas)
            print(header)
            print("-" * len(header))

            # 2. Imprime as linhas convertendo cada uma na hora
            for linha in dados:
                # Criamos a variável 'valores' GARANTIDAMENTE dentro do contexto do loop
                linha_dict = dict(linha)
                texto_linha = " | ".join(str(valor) for valor in linha_dict.values())
                print(texto_linha)

            input("\nPressione Enter para continuar...")

        except Exception as e:
            print(f"❌ Erro ao consultar: {e}")

    def inspecionar_estrutura(self):
        tabela = input("\nDigite o nome da tabela (ex: clientes): ").strip()

        try:
            # 1. Chama o motor para pegar os dados
            colunas = self.db.obter_detalhes_tabela(tabela)

            if not colunas:
                print(f"⚠️ Tabela '{tabela}' não encontrada.")
                return

            # 2. Desenha o cabeçalho
            print(f"\n--- ESTRUTURA DA TABELA: {tabela.upper()} ---")
            print(f"{'NOME':<15} | {'TIPO':<10} | {'PK':<3}")
            print("-" * 35)

            # 3. Percorre a lista que o SQLite devolveu
            for col in colunas:
                # O SQLite devolve 'name' (nome), 'type' (TEXT, etc) e 'pk' (1 se for chave primária)
                print(f"{col['name']:<15} | {col['type']:<10} | {'Sim' if col['pk'] else 'Não'}")

            input("\nPressione Enter para continuar...")

        except Exception as e:
            print(f"❌ Erro ao inspecionar: {e}")