class Produto:
    def __init__(
            self,
            nome: str,
            tipo_item: str = "00",
            unidade: str = "UN",
            categoria: str = None,
            codigo_interno: str = None,
            preco_custo: float = 0.0,
            preco_venda: float = 0.0,
            estoque_atual: float = 0.0,
            estoque_reservado: float = 0.0,
            estoque_minimo: float = 0.0,
            peso_liquido: float = 0.0,
            peso_bruto: float = 0.0,
            ativo: int = 1,
            marca: str = "",
            modelo_versao: str = "", # Sincronizado com Schema
            ncm: str = "",
            cest: str = "",
            origem: str = "0",
            observacoes: str = "",
            data_cadastramento: str = None,
            id: int | None = None
    ):
        self.id = id
        self.codigo_interno = codigo_interno # 👈 Substituído sku por codigo_interno
        self.tipo_item = tipo_item
        self.nome = nome.upper()
        self.unidade = unidade.upper()
        self.categoria = categoria.upper() if categoria else None
        self.marca = marca.upper() if marca else None
        self.modelo_versao = modelo_versao.upper() if modelo_versao else None
        self.ncm = ncm
        self.cest = cest
        self.origem = origem
        self.preco_custo = float(preco_custo)
        self.preco_venda = float(preco_venda)
        self.estoque_atual = float(estoque_atual)
        self.estoque_reservado = float(estoque_reservado)
        self.estoque_minimo = float(estoque_minimo)
        self.peso_liquido = float(peso_liquido)
        self.peso_bruto = float(peso_bruto)
        self.observacoes = observacoes
        self.data_cadastramento = data_cadastramento
        self.ativo = ativo