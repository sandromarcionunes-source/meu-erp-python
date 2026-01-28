class PedidoItem:
    def __init__(self, produto_id, produto_nome_snap, quantidade, preco_unitario, desconto=0):
        self.produto_id = produto_id
        self.produto_nome_snap = produto_nome_snap
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.desconto = desconto if desconto <= preco_unitario else 0
        self.subtotal = quantidade * (self.preco_unitario - self.desconto)

class Pedido:
    def __init__(self, entidade_id, data_emissao, forma_pagamento="", id=None):
        self.id = id
        self.entidade_id = entidade_id
        self.data_emissao = data_emissao
        self.forma_pagamento = forma_pagamento
        self.valor_frete = 0.0
        self.cliente_nome_snap = ""
        self.cliente_documento_snap = ""
        self.cliente_endereco_snap = ""
        self.cliente_email_snap = ""
        self.itens = []
        self.valor_total_produtos = 0.0
        self.valor_total_pedido = 0.0

    def adicionar_item(self, item: PedidoItem):
        self.itens.append(item)
        self.calcular_totais()

    def calcular_totais(self):
        self.valor_total_produtos = sum(item.subtotal for item in self.itens)
        self.valor_total_pedido = self.valor_total_produtos + self.valor_frete