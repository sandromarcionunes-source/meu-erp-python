class StatusCredito:
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    BLOQUEADO = "BLOQUEADO"
    FATURADO = "FATURADO"
    CONTABILIZADO = "CONTABILIZADO"

class SituacaoEstoque:
    NAO_MOVIMENTADO = "NAO_MOVIMENTADO"
    RESERVADO = "RESERVADO"  # 🚩 Destino após estorno
    BAIXADO = "BAIXADO"
    ESTORNADO = "ESTORNADO"  # 🚩 Apenas para logs internos

class SituacaoLogistica:
    PENDENTE = "PENDENTE"  # 🚩 Destino após estorno
    EM_SEPARACAO = "EM_SEPARACAO"
    FATURADO = "FATURADO"
    ENVIADO = "ENVIADO"
    ENTREGUE = "ENTREGUE"
    RETIDO_FINANCEIRO = "RETIDO_FINANCEIRO"