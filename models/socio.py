class Socio:
    def __init__(
        self,
        socio_entidade_id: int,
        participacao: float,
        data_entrada: str,      # 🆕 Obrigatório
        data_saida: str | None = None, # 🆕 Opcional
        cargo: str = "Sócio",
        nome_snapshot: str = "",
        id: int | None = None
    ):
        self.id = id
        self.socio_entidade_id = socio_entidade_id
        self.participacao = participacao
        self.data_entrada = data_entrada
        self.data_saida = data_saida
        self.cargo = cargo
        self.nome_snapshot = nome_snapshot