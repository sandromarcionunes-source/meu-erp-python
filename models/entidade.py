from models.socio import Socio

class Entidade:
    def __init__(
        self,
        tipo_pessoa: str,
        nome_fantasia: str,
        documento: str,
        razao_social: str | None = None,
        email: str | None = None,
        telefone: str | None = None,
        cep: str | None = None,
        endereco: str | None = None,
        numero: str | None = None,
        complemento: str | None = None,
        bairro: str | None = None,
        cidade: str | None = None,
        uf: str | None = None,
        limite_credito: float = 0.0,
        observacoes: str | None = None,
        eh_cliente: bool = False,
        eh_fornecedor: bool = False,
        eh_transportadora: bool = False,
        id: int | None = None,
        data_cadastramento: str | None = None
    ):
        self.id = id
        self.tipo_pessoa = tipo_pessoa.upper()
        self.nome_fantasia = nome_fantasia
        self.documento = documento
        self.razao_social = razao_social or nome_fantasia
        self.email = email
        self.telefone = telefone
        self.cep = cep
        self.endereco = endereco
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.uf = uf
        self.limite_credito = float(limite_credito or 0)
        self.observacoes = observacoes
        self.eh_cliente = bool(eh_cliente)
        self.eh_fornecedor = bool(eh_fornecedor)
        self.eh_transportadora = bool(eh_transportadora)
        self.data_cadastramento = data_cadastramento
        self.socios: list[Socio] = []

    def adicionar_socio(self, socio: Socio) -> None:
        if self.tipo_pessoa == 'PJ':
            self.socios.append(socio)
        else:
            raise ValueError("Pessoa Física não pode ter sócios.")