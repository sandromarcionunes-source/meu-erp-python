

class ConfigService:
    def __init__(self, config_repo):
        self.repo = config_repo

    def exibir_menu(self):
        while True:
            print("\n" + "⚙️" + "═" * 40)
            print(f"{'PAINEL DE CONFIGURAÇÕES':^40}")
            print("═" * 41)
            print("1. 💳 Gerenciar Formas de Pagamento")
            print("2. 🔧 Parâmetros do Sistema (Chaves)")
            print("0. ⬅️  Voltar")

            op = input("\nEscolha: ")
            if op == "1":
                self.gestao_formas_pagamento()
            elif op == "2":
                self.gestao_parametros_sistema() # Chamada para a nova função
            elif op == "0":
                break

    # --- NOVO MÉTODO PARA PARÂMETROS ---
    def gestao_parametros_sistema(self):
        print("\n--- 🔧 AJUSTE DE PARÂMETROS ---")
        chave = input("Digite o nome da chave (ex: TIPO_RESERVA): ").strip().upper()

        valor_atual = self.repo.get_valor(chave)

        if valor_atual is not None:
            print(f"Valor atual de [{chave}]: {valor_atual}")
            novo_valor = input(f"Novo valor (ou Enter para manter): ").strip()

            if novo_valor:
                self.repo.atualizar_valor(chave, novo_valor)
                print(f"✅ [{chave}] atualizado para: {novo_valor}")
        else:
            print(f"❌ Chave '{chave}' não encontrada no sistema.")


    def gestao_formas_pagamento(self):
        while True:
            print("\n--- FORMAS DE PAGAMENTO CADASTRADAS ---")
            formas = self.repo.listar_formas_pagamento(apenas_ativas=False)
            for f in formas:
                status = "🟢" if f['ativo'] == 1 else "🔴"
                print(f"[{f['id']}] {f['nome']:<20} {status}")

            print("\n1. [+] Nova | 2. [/] Ativar/Desativar | 0. Voltar")
            op = input("Ação: ")

            if op == "1":
                nome = input("Nome da Forma (ex: PIX, BOLETO 30 DIAS): ")
                if nome: self.repo.salvar_forma_pagamento(nome)
            elif op == "2":
                id_f = input("ID da Forma: ").strip()
                if id_f.isdigit():  # Verifica se é número
                    f_sel = next((f for f in formas if str(f['id']) == id_f), None)
                    if f_sel:
                        novo_status = 0 if f_sel['ativo'] == 1 else 1
                        self.repo.alterar_status_forma(id_f, novo_status)
                        print("✅ Status alterado!")
                else:
                    print("❌ ID inválido.")
            elif op == "0":
                break

