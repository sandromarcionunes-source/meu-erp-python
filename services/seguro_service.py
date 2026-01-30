class SeguroService:
    def __init__(self, repository, entidade_repo):
        self.repo = repository
        self.entidade_repo = entidade_repo

    def exibir_menu(self):
        while True:
            print("\n--- GESTÃO DE SEGUROS ---")
            print("1. Cadastrar Nova Apólice")
            print("2. Listar Seguros Ativos")
            print("0. Voltar")

            op = input("Escolha: ")
            if op == "1":
                self.novo_seguro()
            elif op == "2":
                self.listar()
            elif op == "0":
                break

    def novo_seguro(self):
        print("\n--- CADASTRO DE APÓLICE ---")
        # Aqui você listaria as entidades que são 'SEGURADORAS'
        seg_id = input("ID da Seguradora (Fornecedor): ")
        apolice = input("Número da Apólice: ")
        valor = float(input("Valor do Prêmio (R$): ").replace(',', '.'))
        inicio = input("Início da Vigência (AAAA-MM-DD): ")
        fim = input("Fim da Vigência (AAAA-MM-DD): ")

        novo = Seguro(seg_id, apolice, valor, inicio, fim)
        self.repo.salvar(novo)
        print("✅ Apólice registrada com sucesso!")

    def listar(self):
        seguros = self.repo.listar_ativos()
        for s in seguros:
            print(f"ID: {s['id']} | Apólice: {s['numero_apolice']} | R$ {s['valor_premio']}")