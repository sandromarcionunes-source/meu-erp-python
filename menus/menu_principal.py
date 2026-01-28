class MenuPrincipal:
    def __init__(self, modulos):
        self.modulos = modulos  # Dicionário para guardar os serviços

    def registrar_modulo(self, tecla, nome, servico_funcao):
        """O gênio 'conecta' novos módulos aqui"""
        self.modulos[tecla] = {"nome": nome, "funcao": servico_funcao}

    def exibir(self):
        while True:
            print("\n" + "═" * 50)
            print(f"{'🏢 EMPRESA SANXI - SISTEMA ERP PRO':^50}")
            print("═" * 50)

            # Lista os módulos cadastrados no main.py
            for chave, info in self.modulos.items():
                print(f" {chave}. 🔹 Módulo de {info['nome']}")

            print(" 0. 🚪 Sair do Sistema")
            print("═" * 50)

            opcao = input("👉 Escolha uma opção: ").strip()

            if opcao == "0":
                print("\n✅ Sistema encerrado. Até logo!")
                break

            # PROTEÇÃO: Busca o módulo sem travar se a chave não existir
            modulo_selecionado = self.modulos.get(opcao)

            if modulo_selecionado:
                try:
                    # Executa o menu do serviço (ex: service_cliente.exibir_menu)
                    modulo_selecionado["funcao"]()
                except Exception as e:
                    print(f"\n❌ Erro ao processar módulo {modulo_selecionado['nome']}: {e}")
            else:
                if opcao:  # Se não for apenas um 'Enter' vazio
                    print(f"\n⚠️ Opção '{opcao}' inválida! Tente 1, 2 ou 3.")