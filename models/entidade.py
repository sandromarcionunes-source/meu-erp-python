from models.socio import Socio
from models.entidade_contatos import Contato
from models.entidade_enderecos import Endereco

class Entidade:
    def __init__(
            self,
            tipo_pessoa: str,
            nome_fantasia: str,
            documento: str,
            razao_social: str | None = None,
            inscricao_estadual: str | None = None,
            inscricao_municipal: str | None = None,
            email_comercial: str | None = None,
            email_nfe: str | None = None,
            regime_tributario: str | None = None,
            indicador_ie: str = "9",
            limite_credito: float = 0.0,
            limite_validade: str | None = None,
            bloqueado: bool = False, # 🛠️ Adicionado aqui
            observacoes: str | None = None,
            eh_cliente: bool = False,
            eh_fornecedor: bool = False,
            eh_transportadora: bool = False,
            eh_seguradora: bool = False,
            id: int | None = None,
            data_cadastramento: str | None = None
    ):
        self.id = id
        self.tipo_pessoa = tipo_pessoa.upper()
        self.nome_fantasia = nome_fantasia.upper()
        self.documento = documento
        self.razao_social = (razao_social or nome_fantasia).upper()
        self.inscricao_estadual = inscricao_estadual or ""
        self.inscricao_municipal = inscricao_municipal or ""
        self.email_comercial = email_comercial.upper() if email_comercial else None
        self.email_nfe = email_nfe.upper() if email_nfe else None
        self.regime_tributario = str(regime_tributario).upper() if regime_tributario else None
        self.indicador_ie = str(indicador_ie)
        self.limite_credito = float(limite_credito or 0)
        self.limite_validade = limite_validade
        self.bloqueado = bool(bloqueado) # 🛠️ Adicionado aqui
        self.observacoes = observacoes.upper() if observacoes else None
        self.eh_cliente = bool(eh_cliente)
        self.eh_fornecedor = bool(eh_fornecedor)
        self.eh_transportadora = bool(eh_transportadora)
        self.eh_seguradora = bool(eh_seguradora)
        self.data_cadastramento = data_cadastramento
        self.enderecos: list[Endereco] = []
        self.contatos: list[Contato] = []
        self.socios: list[Socio] = []

    def adicionar_endereco(self, endereco: Endereco) -> None:
        """Adiciona um endereço à lista."""
        self.enderecos.append(endereco)

    def adicionar_contato(self, contato: Contato) -> None:
        """Adiciona um contato à lista."""
        self.contatos.append(contato)

    def adicionar_socio(self, socio: Socio) -> None:
        """Adiciona um sócio apenas se for PJ (Regra de Negócio)."""
        if self.tipo_pessoa == 'PJ':
            self.socios.append(socio)
        else:
            # Em vez de travar o programa com erro, podemos apenas ignorar ou avisar
            print(f"⚠️ Aviso: Não é possível adicionar sócio à Pessoa Física ({self.nome_fantasia}).")

    # --- HELPERS ---

    def obter_endereco_principal(self) -> Endereco | None:
        """Busca o endereço PRINCIPAL (ajustado para bater com o menu numérico)."""
        for end in self.enderecos:
            if str(end.tipo).upper() == 'PRINCIPAL':
                return end
        return self.enderecos[0] if self.enderecos else None

    def obter_whatsapp(self) -> str | None:
        """Busca contatos de comunicação rápida."""
        for cont in self.contatos:
            if str(cont.tipo).upper() in ['WHATSAPP', 'CELULAR']:
                return cont.numero
        return None

    def __repr__(self) -> str:
        return (f"Entidade(id={self.id}, nome='{self.nome_fantasia}', "
                f"doc='{self.documento}', tipo='{self.tipo_pessoa}')")