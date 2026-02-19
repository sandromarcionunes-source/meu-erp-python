from models.produto import Produto
from typing import List, Any, Optional


class ProdutoRepository:
    def __init__(self, db: Any):
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
        # Sincronizado com o campo codigo_interno do Schema
        self.db.execute("UPDATE produtos SET codigo_interno = ? WHERE id = ?", (sku, gerado_id))
        return sku

    def buscar_por_codigo(self, sku_input: str) -> Optional[Produto]:
        """Busca inteligente: aceita '1' ou '0001'"""
        sku_formatado = str(sku_input).strip().zfill(4)
        row = self.db.fetch_one("SELECT * FROM produtos WHERE codigo_interno = ?", (sku_formatado,))

        if not row:
            row = self.db.fetch_one("SELECT * FROM produtos WHERE codigo_interno = ?", (sku_input.strip(),))

        return Produto(**row) if row else None

    def buscar_por_id(self, produto_id: int) -> Optional[Produto]:
        row = self.db.fetch_one("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        return Produto(**row) if row else None

    def buscar_todos(self) -> List[Produto]:
        """O método que estava faltando e causou o erro"""
        rows = self.db.fetch_all("SELECT * FROM produtos WHERE ativo = 1 ORDER BY nome ASC")
        return [Produto(**r) for r in rows]

    def buscar_por_id_ou_descricao(self, termo: str) -> List[Produto]:
        query = """
            SELECT * FROM produtos 
            WHERE (id = ? OR nome LIKE ? OR marca LIKE ? OR codigo_interno = ?)
            AND ativo = 1
        """
        like_termo = f"%{termo}%"
        rows = self.db.fetch_all(query, (termo, like_termo, like_termo, termo))
        return [Produto(**r) for r in rows]

    def atualizar(self, p: Produto) -> bool:
        query = """
            UPDATE produtos SET 
                tipo_item=?, nome=?, unidade=?, categoria=?, marca=?, modelo_versao=?,
                ncm=?, cest=?, origem=?, peso_liquido=?, peso_bruto=?, 
                preco_custo=?, preco_venda=?, estoque_atual=?, estoque_reservado=?,
                estoque_minimo=?, observacoes=?, ativo=?
            WHERE id = ?
        """
        params = (
            p.tipo_item, p.nome, p.unidade, p.categoria, p.marca, p.modelo_versao,
            p.ncm, p.cest, p.origem, p.peso_liquido, p.peso_bruto,
            p.preco_custo, p.preco_venda, p.estoque_atual, p.estoque_reservado,
            p.estoque_minimo, p.observacoes, p.ativo, p.id
        )
        self.db.execute(query, params)
        return True