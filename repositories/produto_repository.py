from models.produto import Produto

class ProdutoRepository:
    def __init__(self, db):
        self.db = db

    def salvar(self, p: Produto) -> str:
        query = """
            INSERT INTO produtos (
                tipo_item, nome, unidade, categoria, marca, modelo_versao,
                ncm, cest, origem, peso_liquido, peso_bruto,
                preco_custo, preco_venda, estoque_atual, estoque_reservado,
                estoque_minimo, observacoes, data_cadastramento, ativo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            p.tipo_item, p.nome, p.unidade, p.categoria, p.marca, p.modelo_versao,
            p.ncm, p.cest, p.origem, p.peso_liquido, p.peso_bruto,
            p.preco_custo, p.preco_venda, p.estoque_atual, p.estoque_reservado,
            p.estoque_minimo, p.observacoes, p.data_cadastramento, p.ativo
        )

        gerado_id = self.db.execute(query, params)
        sku = str(gerado_id).zfill(4)
        self.db.execute("UPDATE produtos SET codigo_interno = ? WHERE id = ?", (sku, gerado_id))
        return sku

    def atualizar(self, p: Produto) -> bool:
        query = """
            UPDATE produtos SET 
                tipo_item=?, nome=?, unidade=?, categoria=?, marca=?, modelo_versao=?,
                ncm=?, cest=?, origem=?, peso_liquido=?, peso_bruto=?, 
                preco_custo=?, preco_venda=?, estoque_atual=?, estoque_reservado=?,
                estoque_minimo=?, observacoes=?, ativo=?
            WHERE codigo_interno = ?
        """
        params = (
            p.tipo_item, p.nome, p.unidade, p.categoria, p.marca, p.modelo_versao,
            p.ncm, p.cest, p.origem, p.peso_liquido, p.peso_bruto,
            p.preco_custo, p.preco_venda, p.estoque_atual, p.estoque_reservado,
            p.estoque_minimo, p.observacoes, p.ativo, p.codigo_interno
        )
        self.db.execute(query, params)
        return True

    def buscar_por_codigo(self, sku: str):
        row = self.db.fetch_one("SELECT * FROM produtos WHERE codigo_interno = ? OR id = ?", (sku, sku))
        return Produto(**row) if row else None

    def buscar_todos(self):
        rows = self.db.fetch_all("SELECT * FROM produtos WHERE ativo = 1 ORDER BY nome ASC")
        return [Produto(**r) for r in rows]

    def buscar_por_id_ou_descricao(self, termo):
        query = """
            SELECT * FROM produtos 
            WHERE (id = ? 
            OR nome LIKE ? 
            OR marca LIKE ? 
            OR modelo_versao LIKE ?)
            AND ativo = 1
        """
        like_termo = f"%{termo}%"
        rows = self.db.fetch_all(query, (termo, like_termo, like_termo, like_termo))
        return [Produto(**r) for r in rows]