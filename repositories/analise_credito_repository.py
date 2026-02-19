from datetime import datetime


class AnaliseCreditoRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def buscar_dados_financeiros_cliente(self, entidade_id):
        # Certifique-se que os nomes aqui batem com a sua tabela 'entidades'
        sql = "SELECT limite_credito, limite_validade, bloqueado FROM entidades WHERE id = ?"
        return self.db.fetch_one(sql, (entidade_id,))


    def buscar_configuracoes_globais(self):
        # Retorna as regras globais de bloqueio
        return self.db.fetch_one("SELECT * FROM config_credito WHERE id = 1")

    def registrar_log(self, entidade_id, resultado, motivo, valor_pedido=0, limite_na_epoca=0, pedido_id=None):
        sql = """INSERT INTO analise_credito_logs (
                    entidade_id, pedido_id, data_hora, valor_pedido, 
                    limite_na_epoca, resultado, motivo
                 ) VALUES (?, ?, ?, ?, ?, ?, ?)"""

        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Executa a gravação do log de auditoria
        self.db.execute(sql, (
            entidade_id, pedido_id, data_atual, valor_pedido,
            limite_na_epoca, resultado, motivo
        ))

    def atualizar_limite(self, entidade_id, valor, validade):
        sql = "UPDATE entidades SET limite_credito = ?, limite_validade = ? WHERE id = ?"
        return self.db.execute(sql, (valor, validade, entidade_id))

    def atualizar_bloqueio_manual(self, entidade_id, status):
        sql = "UPDATE entidades SET bloqueado = ? WHERE id = ?"
        return self.db.execute(sql, (status, entidade_id))

    def atualizar_config_global(self, status_trava):
        sql = "UPDATE config_credito SET bloquear_automatico = ? WHERE id = 1"
        return self.db.execute(sql, (status_trava,))

    def buscar_logs_auditoria(self, limite=15):
        sql = "SELECT * FROM analise_credito_logs ORDER BY id DESC LIMIT ?"
        return self.db.fetch_all(sql, (limite,))