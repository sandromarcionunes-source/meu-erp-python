class StatusPedido:
    # Fluxo de Crédito
    ORCAMENTO = "ORCAMENTO"
    AGUARDANDO_ANALISE = "AGUARDANDO_ANALISE"
    BLOQUEADO_CREDITO = "BLOQUEADO_CREDITO"
    APROVADO_AUTO = "APROVADO_AUTO"
    LIBERADO_MANUAL = "LIBERADO_MANUAL"

    # Fluxo Operacional
    EM_SEPARACAO = "EM_SEPARACAO"
    CONFERIDO = "CONFERIDO"
    AGUARDANDO_FATURAMENTO = "AGUARDANDO_FATURAMENTO"

    # Encerramento
    FATURADO = "FATURADO"
    CANCELADO = "CANCELADO"

    @classmethod
    def pode_faturar(cls, status):
        """Define quais status permitem gerar nota fiscal"""
        return status in [cls.APROVADO_AUTO, cls.LIBERADO_MANUAL, cls.CONFERIDO]

    @classmethod
    def reserva_estoque(cls, status):
        """Define se o status deve bloquear mercadoria"""
        return status not in [cls.ORCAMENTO, cls.CANCELADO]