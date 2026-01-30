from models.seguro import Seguro

class SeguroRepository:
    def __init__(self, db):
        self.db = db

    def salvar(self, seguro: Seguro):
        query = """
            INSERT INTO seguros (entidade_seguradora_id, numero_apolice, valor_premio, 
                                 vigencia_inicio, vigencia_fim, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.db.execute(query, (
            seguro.seguradora_id, seguro.numero_apolice, seguro.valor_premio,
            seguro.vigencia_inicio, seguro.vigencia_fim, seguro.status
        ))

    def listar_ativos(self):
        return self.db.fetch_all("SELECT * FROM seguros WHERE status = 'ATIVO'")