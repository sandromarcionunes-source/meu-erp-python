class NotaFiscal:
    def __init__(self):
        # 🟢 Atributos de Identificação
        self.id = None
        self.pedido_id = None
        self.numero_nf = None
        self.serie = 1
        self.chave_acesso = ""
        self.data_emissao = ""

        # 🟢 Snapshots Emissor
        self.emissor_razao_snap = ""
        self.emissor_cnpj_snap = ""
        self.emissor_ie_snap = ""

        # 🟢 Snapshots Cliente
        self.cliente_nome_snap = ""
        self.cliente_doc_snap = ""
        self.cliente_end_snap = ""

        # 🟢 Totais Financeiros e Logísticos
        self.valor_produtos = 0.0
        self.valor_frete = 0.0
        self.valor_total_nota = 0.0
        self.peso_bruto_total = 0.0
        self.peso_liquido_total = 0.0

        self.status = "AUTORIZADA"
        self.protocolo = ""
        self.itens = [] # 🔴 Lista de instâncias de NotaFiscalItem

    def __str__(self):
        return f"NF-e nº {self.numero_nf} | Total: R${self.valor_total_nota:.2f}"

class NotaFiscalItem:
    def __init__(self):
        # 🟢 Estrutura do Item
        self.id = None
        self.nota_fiscal_id = None
        self.produto_id = None
        self.nome_produto_snap = ""
        self.ncm_snap = ""
        self.quantidade = 0.0
        self.valor_unitario = 0.0
        self.valor_total_item = 0.0
        self.peso_bruto_unit = 0.0
        self.peso_liquido_unit = 0.0