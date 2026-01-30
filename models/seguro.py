class Seguro:
    def __init__(self, seguradora_id, numero_apolice, valor_premio,
                 vigencia_inicio, vigencia_fim, id=None, status='ATIVO'):
        self.id = id
        self.seguradora_id = seguradora_id
        self.numero_apolice = numero_apolice
        self.valor_premio = valor_premio
        self.vigencia_inicio = vigencia_inicio
        self.vigencia_fim = vigencia_fim
        self.status = status