from models.produto import Produto


class ProdutoRepository:
    def __init__(self, db):
        self.db = db

    def salvar(self, p):
        # 1. Inserimos o produto (sem o codigo_interno, pois ele será o ID)
        # Note: Contei 14 colunas e 14 interrogações agora.
        sql = """
        INSERT INTO produtos (
            tipo_item, nome, unidade, ncm, 
            peso_liquido, peso_bruto, preco_custo, preco_venda, 
            estoque_atual, estoque_reservado, estoque_minimo, 
            observacoes, data_cadastramento, ativo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            p.tipo_item, p.nome, p.unidade, p.ncm,
            p.peso_liquido, p.peso_bruto, p.preco_custo, p.preco_venda,
            p.estoque_atual, p.estoque_reservado, p.estoque_minimo,
            p.observacoes, p.data_cadastramento, p.ativo
        )

        # Executa a inserção e pega o ID gerado
        ultimo_id = self.db.execute(sql, params)

        # 2. Sincroniza o codigo_interno com o ID que o banco acabou de gerar
        sql_update = "UPDATE produtos SET codigo_interno = ? WHERE id = ?"
        self.db.execute(sql_update, (str(ultimo_id), ultimo_id))

        return ultimo_id

    def atualizar(self, p):
        sql = """
        UPDATE produtos SET 
            nome = ?, unidade = ?, ncm = ?, peso_liquido = ?, peso_bruto = ?, 
            preco_custo = ?, preco_venda = ?, estoque_minimo = ?, 
            observacoes = ?, ativo = ?
        WHERE id = ?
        """
        params = (
            p.nome, p.unidade, p.ncm, p.peso_liquido, p.peso_bruto,
            p.preco_custo, p.preco_venda, p.estoque_minimo,
            p.observacoes, p.ativo, p.id
        )
        return self.db.execute(sql, params)

    def buscar_todos(self):
        sql = "SELECT * FROM produtos WHERE ativo = 1 ORDER BY id ASC"
        rows = self.db.fetch_all(sql)
        return [Produto(**row) for row in rows]

    def buscar_por_codigo(self, codigo):
        # Busca flexível: aceita tanto o ID numérico quanto o texto do SKU
        sql = "SELECT * FROM produtos WHERE codigo_interno = ? OR id = ?"
        row = self.db.fetch_one(sql, (str(codigo), codigo))
        return Produto(**row) if row else None

    def buscar_por_id_ou_descricao(self, termo):
        query = """
            SELECT * FROM produtos 
            WHERE (id = ? OR nome LIKE ?) AND ativo = 1
            ORDER BY nome ASC
        """
        rows = self.db.fetch_all(query, (termo, f"%{termo}%"))

        # ESTA É A LINHA MÁGICA: converte o resultado do banco em objetos que o Pedido entende
        return [Produto(**row) for row in rows]

    def buscar_por_id(self, id_produto):
        """Busca um produto único pelo ID para o módulo de Pedidos"""
        query = "SELECT * FROM produtos WHERE id = ?"
        return self.db.fetch_one(query, (id_produto,))