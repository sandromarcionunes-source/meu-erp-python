from models.entidade import Entidade
from models.socio import Socio
from typing import Any


class EntidadeRepository:  # <--- Nome exato exigido pelo seu main.py
    def __init__(self, db: Any):
        self.db = db

    def salvar(self, entidade: Entidade) -> int:
        """Salva a entidade principal e dispara o salvamento de sócios se houver"""
        query = """
            INSERT INTO entidades (
                tipo_pessoa, nome_fantasia, razao_social, documento, 
                email, telefone, cep, endereco, numero, complemento, 
                bairro, cidade, uf, limite_credito, eh_cliente, 
                eh_fornecedor, eh_transportadora, data_cadastramento, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            entidade.tipo_pessoa, entidade.nome_fantasia, entidade.razao_social,
            entidade.documento, entidade.email, entidade.telefone,
            entidade.cep, entidade.endereco, entidade.numero,
            entidade.complemento, entidade.bairro, entidade.cidade,
            entidade.uf, entidade.limite_credito,
            1 if entidade.eh_cliente else 0,
            1 if entidade.eh_fornecedor else 0,
            1 if entidade.eh_transportadora else 0,
            entidade.data_cadastramento, entidade.observacoes
        )

        entidade_id = self.db.execute(query, params)

        # Se for PJ e tiver sócios, salva os vínculos
        if entidade.tipo_pessoa == 'PJ' and entidade.socios:
            self.salvar_socios_vinculados(entidade_id, entidade.socios)

        return entidade_id

    def salvar_socios_vinculados(self, entidade_pai_id: int, lista_socios: list[Socio]) -> None:
        """Salva os vínculos na tabela de sócios"""
        query = """
            INSERT INTO socios (
                entidade_pai_id, socio_entidade_id, percentual_participacao, 
                data_entrada, data_saida, cargo
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        for s in lista_socios:
            self.db.execute(query, (
                entidade_pai_id,
                s.socio_entidade_id,
                s.participacao, # O Python envia 'participacao' para a coluna 'percentual_participacao'
                s.data_entrada,
                s.data_saida,
                s.cargo
            ))

    # def buscar_por_id(self, entidade_id: int) -> Entidade | None:
    #     """Recupera uma entidade completa com seus sócios e respectivos períodos"""
    #     row = self.db.fetch_one("SELECT * FROM entidades WHERE id = ?", (entidade_id,))
    #     if not row:
    #         return None
    #
    #     entidade = Entidade(
    #         id=row['id'],
    #         tipo_pessoa=row['tipo_pessoa'],
    #         nome_fantasia=row['nome_fantasia'],
    #         razao_social=row['razao_social'],
    #         documento=row['documento'],
    #         email=row['email'],
    #         telefone=row['telefone'],
    #         cep=row['cep'],
    #         endereco=row['endereco'],
    #         numero=row['numero'],
    #         complemento=row['complemento'],
    #         bairro=row['bairro'],
    #         cidade=row['cidade'],
    #         uf=row['uf'],
    #         limite_credito=row['limite_credito'],
    #         eh_cliente=bool(row['eh_cliente']),
    #         eh_fornecedor=bool(row['eh_fornecedor']),
    #         eh_transportadora=bool(row['eh_transportadora']),
    #         data_cadastramento=row['data_cadastramento'],
    #         observacoes=row['observacoes']
    #     )
    #
    #     # Busca sócios trazendo as datas gravadas
    #     query_socios = """
    #                 SELECT s.*, e.nome_fantasia as nome_socio
    #                 FROM socios s
    #                 JOIN entidades e ON s.socio_entidade_id = e.id
    #                 WHERE s.entidade_pai_id = ?
    #             """
    #     rows_s = self.db.fetch_all(query_socios, (entidade_id,))
    #
    #     for rs in rows_s:
    #         socio_obj = Socio(
    #             socio_entidade_id=rs['socio_entidade_id'],
    #             participacao=rs['percentual_participacao'],  # Nome da coluna no seu SQL
    #             data_entrada=rs['data_entrada'],
    #             data_saida=rs['data_saida'],
    #             cargo=rs['cargo'],
    #             nome_snapshot=rs['nome_socio'],  # O apelido que demos no JOIN
    #             id=rs['id']
    #         )
    #         entidade.socios.append(socio_obj)
    #
    #     return entidade

    def buscar_por_id(self, entidade_id: int) -> Entidade | None:
        row = self.db.fetch_one("SELECT * FROM entidades WHERE id = ?", (entidade_id,))
        if not row: return None

        entidade = Entidade(
            id=row['id'], tipo_pessoa=row['tipo_pessoa'],
            nome_fantasia=row['nome_fantasia'], razao_social=row['razao_social'],
            documento=row['documento'], email=row['email'], telefone=row['telefone'],
            eh_cliente=bool(row['eh_cliente']), eh_fornecedor=bool(row['eh_fornecedor']),
            eh_transportadora=bool(row['eh_transportadora']),
            data_cadastramento=row['data_cadastramento'], observacoes=row['observacoes']
        )

        # 1. Se for PJ: Busca quem são os SÓCIOS desta empresa
        query_socios = """
            SELECT s.*, e.nome_fantasia as nome_socio 
            FROM socios s 
            JOIN entidades e ON s.socio_entidade_id = e.id 
            WHERE s.entidade_pai_id = ?
        """
        rows_s = self.db.fetch_all(query_socios, (entidade_id,))
        for rs in rows_s:
            entidade.socios.append(Socio(
                socio_entidade_id=rs['socio_entidade_id'],
                participacao=rs['percentual_participacao'],
                data_entrada=rs['data_entrada'], data_saida=rs['data_saida'],
                cargo=rs['cargo'], nome_snapshot=rs['nome_socio'], id=rs['id']
            ))

        # 2. Se for PF: Busca de quais EMPRESAS esta pessoa é sócia
        if entidade.tipo_pessoa == 'PF':
            query_participacoes = """
                SELECT s.*, e.nome_fantasia as nome_empresa 
                FROM socios s 
                JOIN entidades e ON s.entidade_pai_id = e.id 
                WHERE s.socio_entidade_id = ?
            """
            rows_p = self.db.fetch_all(query_participacoes, (entidade_id,))
            # Criamos um atributo temporário para exibir no Service
            entidade.participacoes_societarias = rows_p

        return entidade




    def buscar_por_cpf(self, cpf: str) -> Entidade | None:
        """Busca por documento (Compatibilidade com Service)"""
        documento_limpo = str(cpf).replace(".", "").replace("-", "").replace("/", "").strip()
        row = self.db.fetch_one("SELECT id FROM entidades WHERE documento = ?", (documento_limpo,))
        if row:
            return self.buscar_por_id(row['id'])
        return None

    def buscar_flexivel(self, termo: str) -> list[Entidade]:
        """Busca por ID, CPF/CNPJ ou Nome"""
        termo = str(termo).strip()
        if not termo: return []

        if termo.isdigit():
            rows = self.db.fetch_all(
                "SELECT id FROM entidades WHERE id = ? OR documento = ?",
                (termo, termo)
            )
        else:
            rows = self.db.fetch_all(
                "SELECT id FROM entidades WHERE nome_fantasia LIKE ? OR razao_social LIKE ?",
                (f"%{termo}%", f"%{termo}%")
            )

        return [self.buscar_por_id(r['id']) for r in rows if r]

    def buscar_por_id_ou_documento(self, termo: str) -> Entidade | None:
        """Busca inteligente para campos rápidos"""
        termo_limpo = str(termo).replace(".", "").replace("-", "").replace("/", "").strip()
        if not termo_limpo: return None

        if termo_limpo.isdigit() and len(termo_limpo) <= 7:
            ent = self.buscar_por_id(int(termo_limpo))
            if ent: return ent

        row = self.db.fetch_one("SELECT id FROM entidades WHERE documento = ?", (termo_limpo,))
        if row:
            return self.buscar_por_id(row['id'])

        return None

    def atualizar_campo_dinamico(self, entidade_id: int, campo: str, valor: Any) -> None:
        """Atualiza um único campo"""
        query = f"UPDATE entidades SET {campo} = ? WHERE id = ?"
        self.db.execute(query, (valor, entidade_id))

    def encerrar_sociedade(self, socio_id: int, data_saida: str) -> None:
        """Grava a data de saída de um sócio"""
        query = "UPDATE socios SET data_saida = ? WHERE id = ?"
        self.db.execute(query, (data_saida, socio_id))

    # def buscar_clientes(self):
    #     """Busca apenas as entidades que são clientes"""
    #     sql = "SELECT * FROM entidades WHERE eh_cliente = 1 ORDER BY nome_fantasia"
    #     return self.db.fetch_all(sql)

    def buscar_clientes(self):
        """Busca as entidades e converte cada uma em objeto completo"""
        rows = self.db.fetch_all("SELECT id FROM entidades WHERE eh_cliente = 1 ORDER BY nome_fantasia")
        # Para cada ID encontrado, usamos o buscar_por_id que já tem toda a lógica de sócios/participações
        return [self.buscar_por_id(r['id']) for r in rows if r]


    def buscar_socios_por_entidade(self, entidade_id: int):
        """Busca os sócios cruzando com a tabela entidades para evitar erro de snapshot"""
        sql = """
            SELECT s.cargo, e.nome_fantasia as nome_snapshot
            FROM socios s
            JOIN entidades e ON e.id = s.socio_entidade_id
            WHERE s.entidade_pai_id = ?
        """
        return self.db.fetch_all(sql, (entidade_id,))