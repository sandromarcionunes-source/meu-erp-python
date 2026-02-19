from datetime import datetime
from models.analise_credito import AnaliseCreditoResult

class AnaliseCreditoService:
    def __init__(self, analise_repo):
        self.repo = analise_repo

    def exibir_menu(self):
        while True:
            print("\n" + "═" * 60)
            print(f"{'🛡️  GESTÃO DE CRÉDITO':^60}")
            print("═" * 60)
            print("1. 📝 Alterar Limite")
            print("2. 🚫 Bloqueio Manual")
            print("3. ⚙️  Configuração Global")
            print("4. 📋 Logs de Auditoria")
            print("0. ⬅️  Sair")
            op = input("\nEscolha: ")

            if op == "1":
                id_cli = input("👉 ID Cliente: ").strip()
                valor = float(input("💰 Novo Limite R$: ").replace(',', '.'))
                data = input("📅 Validade (AAAA-MM-DD): ").strip()
                self.repo.atualizar_limite(id_cli, valor, data)
                print("✅ Limite atualizado!")

            elif op == "2":
                id_cli = input("👉 ID Cliente: ").strip()
                status = input("🚫 Bloquear Cliente? (S/N): ").upper()
                self.repo.atualizar_bloqueio_manual(id_cli, 1 if status == 'S' else 0)
                print("✅ Status alterado!")

            elif op == "3":
                status = input("⚙️ Ativar Trava Global? (S/N): ").upper()
                self.repo.atualizar_config_global(1 if status == 'S' else 0)
                print("✅ Configuração salva!")

            elif op == "4":
                print("\n" + "─" * 20 + " ÚLTIMOS LOGS " + "─" * 20)
                logs = self.repo.buscar_logs_auditoria(limite=15)
                for l in logs:
                    # Usando acesso direto por chave do sqlite3.Row
                    print(f"[{l['data_hora']}] Cli: {l['entidade_id']} | {l['resultado']} | {l['motivo']}")
                input("\nEnter para continuar...")

            elif op == "0":
                break


    def avaliar(self, entidade_id, valor_pedido_atual, pedido_id=None):
        try:
            # 1. Busca dados puros do banco (sqlite3.Row)
            row_cliente = self.repo.buscar_dados_financeiros_cliente(entidade_id)
            row_config = self.repo.buscar_configuracoes_globais()

            if not row_cliente:
                return AnaliseCreditoResult(False, "❌ Cliente não localizado.")

            # 🛠️ CONVERSÃO PARA DICIONÁRIO (Resolve o erro do .get)
            dados = dict(row_cliente)
            config = dict(row_config) if row_config else {}

            # 2. Extração segura usando os nomes do seu novo Schema
            limite_valor = dados.get('limite_credito', 0) or 0
            limite_data = dados.get('limite_validade', None)
            bloqueado_manual = dados.get('bloqueado', 0)
            bloqueio_ativo = config.get('bloquear_automatico', 1)

            veredito = None

            # --- REGRA A: BLOQUEIO MANUAL NO CADASTRO ---
            if bloqueado_manual in [1, 'S', 'True', True]:
                veredito = AnaliseCreditoResult(False, "🚫 Bloqueio manual ativo no cadastro.")

            # --- REGRA B: VIGÊNCIA DO LIMITE ---
            if not veredito:
                vigente, msg_data = self._checar_data(limite_data)
                if not vigente:
                    veredito = AnaliseCreditoResult(False, msg_data)

            # --- REGRA C: VALOR DO LIMITE ---
            if not veredito:
                if valor_pedido_atual > limite_valor:
                    veredito = AnaliseCreditoResult(False, f"❌ Limite insuficiente (R$ {limite_valor:.2f}).")
                else:
                    veredito = AnaliseCreditoResult(True, "✅ Crédito aprovado automaticamente.")

            # ⚖️ TRATAMENTO DO BLOQUEIO GLOBAL
            if not veredito.aprovado and bloqueio_ativo == 0:
                veredito = AnaliseCreditoResult(True, f"⚠️ Alerta: {veredito.motivo} (Bloqueio Global Desativado)")

            # 📝 REGISTRO DE LOG (AUDITORIA)
            self.repo.registrar_log(
                entidade_id=entidade_id,
                pedido_id=pedido_id,
                resultado="APROVADO" if veredito.aprovado else "BLOQUEADO",
                motivo=veredito.motivo,
                valor_pedido=valor_pedido_atual,
                limite_na_epoca=limite_valor
            )

            return veredito

        except Exception as e:
            # Captura erros inesperados e retorna como bloqueio por segurança
            return AnaliseCreditoResult(False, f"⚠️ Erro no processamento de crédito: {str(e)}")

    def _checar_data(self, data_str):
        if not data_str:
            return False, "❌ Data de limite de crédito não definida."
        try:
            # Tenta converter independente do formato vindo do banco
            fmt = "%Y-%m-%d" if "-" in data_str else "%d/%m/%Y"
            data_lim = datetime.strptime(data_str, fmt).date()
            if data_lim < datetime.now().date():
                return False, f"❌ Limite expirado em {data_lim.strftime('%d/%m/%Y')}."
            return True, ""
        except:
            return False, "❌ Erro no formato da data de crédito."