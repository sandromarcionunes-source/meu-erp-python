# services/cliente_service.py
from models.cliente import Cliente
from datetime import datetime

class ClienteService:
    def __init__(self, repository):
        self.repo = repository

    def exibir_menu(self):
        """Este é o método que o main.py estava procurando!"""
        while True:
            print("\n" + "-" * 20)
            print("  SUB-MENU: CLIENTES")
            print("-" * 20)
            print("1. Cadastrar Novo Cliente")
            print("2. Consultar por CPF")
            print("3. Alterar dados cliente cadastrado")
            print("0. Voltar ao Menu Principal")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                self.cadastrar_cliente()
            elif opcao == "2":
                self.consultar_por_cpf()
            elif opcao == "3":
                self.alterar_cliente_iterativo()
            elif opcao == "0":
                break  # Sai do loop e volta para o MenuPrincipal
            else:
                print("Opção inválida!")

    def cadastrar_cliente(self):
        print("\n" + "=" * 40)
        print("      NOVO CADASTRO DE CLIENTE")
        print("=" * 40)

        # 1. Definição do Tipo
        print("Tipo de Pessoa:")
        print("1 - Física (PF)")
        print("2 - Jurídica (PJ)")
        opcao_tipo = input("Escolha: ")

        # Inicializamos os campos específicos como None
        tipo_pessoa = 'pf' if opcao_tipo == "1" else 'pj'
        nome = None
        razao_social = None
        cpf = None
        cnpj = None

        # 2. Coleta de dados específicos
        if tipo_pessoa == 'pf':
            nome = input("Nome Completo: ")
            cpf = input("CPF (somente números): ")
        else:
            razao_social = input("Razão Social: ")
            cnpj = input("CNPJ (somente números): ")

        cep = input("CEP: ")
        email = input("Email: ")
        telefone = input("Telefone:")
        endereco = input("Endereço: ")
        numero = input("Número: ")
        complemento = input("Complemento: ")
        bairro = input("Bairro: ")
        cidade = input("Cidade: ")
        uf = input("UF: ")
        limite_credito = float(input("Limite de Crédito: ") or 0)

        # Data automática
        data_cadastramento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 3. Criar o objeto Cliente (Model) usando os dados acima
        novo_cliente = Cliente(
            tipo_pessoa = tipo_pessoa,
            nome=nome,
            razao_social=razao_social,
            cpf=cpf,
            cnpj=cnpj,
            cep=cep,
            email=email,
            telefone=telefone,
            endereco=endereco,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            uf=uf,
            data_cadastramento=data_cadastramento,
            limite_credito=limite_credito
        )

        # 4. Enviar para o Repositório salvar
        try:
            self.repo.salvar(novo_cliente)
            print(f"\n✅ Cliente {nome} cadastrado com sucesso!")
        except Exception as e:
            print(f"\n❌ Erro ao salvar: {e}")


    def alterar_cliente_iterativo(self):
        id_cliente = input("\nDigite o ID do cliente: ")
        cliente = self.repo.buscar_por_id(id_cliente)

        if not cliente:
            print("❌ Cliente não encontrado.")
            return

        # Lista de campos que podem ser alterados
        campos = [
            "nome", "razao_social", "cpf", "cnpj", "cep", "email",
            "telefone", "endereco", "numero", "complemento",
            "bairro", "cidade", "uf", "limite_credito"
        ]

        print(f"\n--- ALTERANDO: {cliente.nome or cliente.razao_social} ---")

        # Exibe o menu iterando a lista (o enumerate começa do 1)
        for i, campo in enumerate(campos, 1):
            # O replace serve para deixar o nome mais bonito (ex: limite_credito -> Limite Credito)
            print(f"{i}. {campo.replace('_', ' ').title()}")

        try:
            escolha = int(input("\nEscolha o número do campo que deseja alterar: "))

            if 1 <= escolha <= len(campos):
                campo_selecionado = campos[escolha - 1]
                novo_valor = input(f"Digite o novo valor para {campo_selecionado.upper()}: ")

                # Envia para o repositório
                self.repo.atualizar_campo_dinamico(id_cliente, campo_selecionado, novo_valor)
                print(f"✅ {campo_selecionado.upper()} atualizado com sucesso!")
            else:
                print("⚠️ Opção fora do intervalo.")

        except ValueError:
            print("❌ Por favor, digite um número válido.")

    def consultar_por_cpf(self):
        print("\n🔍 CONSULTA DE CLIENTE POR CPF")
        cpf_busca = input("Digite o CPF (somente números): ")

        cliente = self.repo.buscar_por_cpf(cpf_busca)

        if cliente:
            print("\n" + "─" * 40)
            print(f"✅ CLIENTE ENCONTRADO:")
            print(f"ID:       {cliente['id']}")
            print(f"Nome:     {cliente['nome']}")
            print(f"CPF:      {cliente['cpf']}")
            print(f"Cidade:   {cliente['cidade']}/{cliente['uf']}")
            print("─" * 40)
        else:
            print(f"\n❌ Nenhum cliente cadastrado com o CPF: {cpf_busca}")