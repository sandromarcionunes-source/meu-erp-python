class Produto:
    def __init__(self, **kwargs):
        # O kwargs.get('nome_da_coluna_no_banco')
        self.id = kwargs.get('id')
        self.codigo_interno = kwargs.get('codigo_interno')
        self.tipo_item = kwargs.get('tipo_item')
        self.nome = kwargs.get('nome')
        self.unidade = kwargs.get('unidade') # Ajustado para bater com o banco
        self.ncm = kwargs.get('ncm')
        self.peso_liquido = kwargs.get('peso_liquido', 0.0)
        self.peso_bruto = kwargs.get('peso_bruto', 0.0)
        self.preco_custo = kwargs.get('preco_custo', 0.0) # Ajustado
        self.preco_venda = kwargs.get('preco_venda', 0.0)
        self.estoque_atual = kwargs.get('estoque_atual', 0.0)
        self.estoque_reservado = kwargs.get('estoque_reservado', 0.0)
        self.estoque_minimo = kwargs.get('estoque_minimo', 0.0)
        self.observacoes = kwargs.get('observacoes', "")
        self.data_cadastramento = kwargs.get('data_cadastramento')
        self.ativo = kwargs.get('ativo', 1)