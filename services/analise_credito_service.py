from datetime import datetime
from models.analise_credito import AnaliseCreditoResult
from models.constants import StatusCredito

class AnaliseCreditoService:
    def __init__(self, analise_repo, pedido_repo=None):
        self.repo = analise_repo
        self.pedido_repo = pedido_repo  # ✅ NOVO: Repositório para somar pedidos abertos

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
            # 1. Busca dados do banco
            row_cliente = self.repo.buscar_dados_financeiros_cliente(entidade_id)
            row_config = self.repo.buscar_configuracoes_globais()

            if not row_cliente:
                return AnaliseCreditoResult(False, "❌ Cliente não localizado.")

            # 🟢 CORREÇÃO: Conversão para Dicionário Real (Evita erro de Row)
            dados = {k.lower(): v for k, v in dict(row_cliente).items()}
            config = {k.lower(): v for k, v in dict(row_config).items()} if row_config else {}

            # Extração segura usando seu Schema
            limite_total = float(dados.get('limite_credito', 0) or 0)
            limite_data = dados.get('limite_validade')
            bloqueado_manual = dados.get('bloqueado', 0)
            bloqueio_ativo = config.get('bloquear_automatico', 1)

            veredito = None

            # --- REGRA A: BLOQUEIO MANUAL ---
            if str(bloqueado_manual) in ['1', 'S', 'True', 'True']:
                veredito = AnaliseCreditoResult(False, "🚫 Bloqueio manual ativo no cadastro.")

            # --- REGRA B: VIGÊNCIA ---
            if not veredito:
                vigente, msg_data = self._checar_data(limite_data)
                if not vigente:
                    veredito = AnaliseCreditoResult(False, msg_data)

            # --- 🟢 REGRA C: CÁLCULO DE EXPOSIÇÃO (CORRIGIDO) ---
            if not veredito:
                # Conforme regra de 01/03/2026: APROVADO + FATURADO
                status_consumo = (StatusCredito.APROVADO, StatusCredito.FATURADO)
                placeholders = ', '.join(['?'] * len(status_consumo))

                # 🟡 CORREÇÃO CRÍTICA: Nome da coluna alterado para 'valor_total_pedido'
                sql_exposicao = f"""
                        SELECT SUM(valor_total_pedido) FROM pedidos 
                        WHERE entidade_id = ? AND status_credito IN ({placeholders})
                    """
                res_exp = self.repo.db.fetch_one(sql_exposicao, [entidade_id] + list(status_consumo))

                # Tratamento do retorno do SUM
                exposicao_atual = 0.0
                if res_exp:
                    val = list(dict(res_exp).values())[0]
                    exposicao_atual = float(val or 0)

                # 🟡 AJUSTE: Se for edição de pedido, remove o valor antigo da conta
                if pedido_id:
                    sql_pedido = "SELECT valor_total_pedido FROM pedidos WHERE id = ?"
                    res_ped = self.repo.db.fetch_one(sql_pedido, (pedido_id,))
                    if res_ped:
                        val_ped = list(dict(res_ped).values())[0]
                        exposicao_atual -= float(val_ped or 0)

                limite_disponivel = limite_total - exposicao_atual

                if valor_pedido_atual > limite_disponivel:
                    veredito = AnaliseCreditoResult(False,
                                                    f"❌ Limite insuficiente. Disponível: R$ {limite_disponivel:.2f} (Exposição: R$ {exposicao_atual:.2f}).")
                else:
                    veredito = AnaliseCreditoResult(True,
                                                    f"✅ Crédito aprovado. Saldo: R$ {limite_disponivel - valor_pedido_atual:.2f}")

            # TRATAMENTO DO BLOQUEIO GLOBAL
            if not veredito.aprovado and bloqueio_ativo == 0:
                veredito = AnaliseCreditoResult(True, f"⚠️ Alerta: {veredito.motivo} (Trava Global Desativada)")

            # LOG DE AUDITORIA
            self.repo.registrar_log(
                entidade_id=entidade_id,
                pedido_id=pedido_id,
                resultado="APROVADO" if veredito.aprovado else "BLOQUEADO",
                motivo=veredito.motivo,
                valor_pedido=valor_pedido_atual,
                limite_na_epoca=limite_total
            )

            return veredito

        except Exception as e:
            # Em caso de erro catastrófico, bloqueia por segurança
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