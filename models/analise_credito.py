class AnaliseCreditoResult:
    def __init__(self, aprovado: bool, motivo: str, limite_restante: float = 0.0):
        self.aprovado = aprovado
        self.motivo = motivo
        self.limite_restante = limite_restante