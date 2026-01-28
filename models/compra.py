class CompraItem:
    def __init__(self, produto_id, produto_nome_snap, quantidade, valor_unitario):
        self.produto_id = produto_id
        self.produto_nome_snap = produto_nome_snap  # <--- ADICIONE ESTA LINHA
        self.quantidade = quantidade
        self.valor_unitario = valor_unitario
        self.subtotal = quantidade * valor_unitario
        self.valor_total = self.subtotal

class Compra:
    def __init__(self, fornecedor_id, fornecedor_nome_snap, tipo_compra, data_emissao=None):
        self.fornecedor_id = fornecedor_id
        self.fornecedor_nome_snap = fornecedor_nome_snap
        self.tipo_compra = tipo_compra
        self.data_emissao = data_emissao
        self.status = "DIGITADO"
        self.itens = []
        self.valor_total = 0.0
        self.forma_pagamento = ""
        self.qtde_parcelas = 1
        self.intervalo_dias = 0
        self.observacao = ""

    def adicionar_item(self, item: CompraItem):
        self.itens.append(item)
        self.calcular_total()

    def calcular_total(self):
        self.valor_total = sum(i.subtotal for i in self.itens)