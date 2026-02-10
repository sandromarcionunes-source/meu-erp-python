from models.entidade import Entidade
from models.socio import Socio
from models.entidade_enderecos import Endereco
from models.entidade_contatos import Contato
from typing import Any


class EntidadeRepository:  # <--- Nome exato exigido pelo seu main.py
    def __init__(self, db: Any):
        self.db = db

    def salvar(self, entidade: Entidade) -> int:
        """Salva a entidade principal e dispara o salvamento de sócios se houver"""
        query = """
            INSERT INTO 
            entidades (
            tipo_pessoa, 
            nome_fantasia, 
            razao_social, 
            documento, 
            inscricao_estadual, 
            inscricao_municipal,
            email_comercial, 
            email_nfe, 
            regime_tributario, 
            indicador_ie, 
            limite_credito, 
            observacoes, 
            eh_cliente, 
            eh_fornecedor, 
            eh_transportadora, 
            eh_seguradora, 
            data_cadastramento
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )
        """
        params = (
            entidade.tipo_pessoa,
            entidade.nome_fantasia,
            entidade.razao_social,
            entidade.documento,
            entidade.inscricao_estadual,
            entidade.inscricao_municipal,
            entidade.email_comercial,
            entidade.email_nfe,
            entidade.regime_tributario,
            entidade.indicador_ie,
            entidade.limite_credito,
            entidade.observacoes,
            1 if entidade.eh_cliente else 0,
            1 if entidade.eh_fornecedor else 0,
            1 if entidade.eh_transportadora else 0,
            1 if entidade.eh_seguradora else 0,
            entidade.data_cadastramento
        )

        entidade_id = self.db.execute(query, params)

        # Se for PJ e tiver sócios, salva os vínculos
        if entidade.tipo_pessoa == 'PJ' and entidade.socios:
            self.salvar_socios_vinculados(entidade_id, entidade.socios)

        if entidade.enderecos:
            self.salvar_enderecos_vinculados(entidade_id, entidade.enderecos)

        if entidade.contatos:
            self.salvar_contatos_vinculados(entidade_id, entidade.contatos)

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

    def salvar_enderecos_vinculados(self, entidade_id: int, lista_enderecos: list[Endereco]) -> None:
        """Salva os endereços na tabela entidade_enderecos"""
        query = """
            INSERT INTO 
            entidade_enderecos (
            entidade_id, 
            tipo, 
            cep, 
            endereco, 
            numero, 
            complemento, 
            bairro, 
            cidade, 
            uf, 
            cidade_ibge
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for e in lista_enderecos:
            self.db.execute(query, (
                entidade_id,
                e.tipo,
                e.cep,
                e.endereco,
                e.numero,
                e.complemento,
                e.bairro,
                e.cidade,
                e.uf,
                e.cidade_ibge
            ))

    def salvar_contatos_vinculados(self, entidade_id: int, lista_contatos: list[Contato]) -> None:
        """Salva os contatos na tabela entidade_contatos"""
        query = """
            INSERT INTO 
            entidade_contatos (
            entidade_id, 
            tipo, 
            numero, 
            nome_contato 
            ) 
            VALUES (?, ?, ?, ?)
        """
        for c in lista_contatos:
            self.db.execute(query, (
                entidade_id,
                c.tipo,
                c.numero,  # Aqui usamos o atributo 'valor' do seu Model Contato
                c.nome_contato
            ))


    def buscar_por_id(self, entidade_id: int) -> Entidade | None:
        row = self.db.fetch_one("SELECT * FROM entidades WHERE id = ?", (entidade_id,))
        if not row: return None

        entidade = Entidade(
            id=row['id'],
            tipo_pessoa=row['tipo_pessoa'],
            nome_fantasia=row['nome_fantasia'],
            documento=row['documento'],
            razao_social=row['razao_social'],
            inscricao_estadual=row['inscricao_estadual'],
            inscricao_municipal=row['inscricao_municipal'],
            email_comercial=row['email_comercial'],
            email_nfe=row['email_nfe'],
            regime_tributario=row['regime_tributario'],
            indicador_ie=row['indicador_ie'],
            limite_credito=row['limite_credito'],
            observacoes=row['observacoes'],
            eh_cliente=bool(row['eh_cliente']),
            eh_fornecedor=bool(row['eh_fornecedor']),
            eh_transportadora=bool(row['eh_transportadora']),
            eh_seguradora=bool(row['eh_seguradora']),
            data_cadastramento=row['data_cadastramento']
        )

        # 1. BUSCAR SÓCIOS
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

        # 🟡 2. BUSCAR ENDEREÇOS (Corrigido sem o .get)
        query_ends = "SELECT * FROM entidade_enderecos WHERE entidade_id = ?"
        rows_e = self.db.fetch_all(query_ends, (entidade_id,))
        for re in rows_e:
            entidade.enderecos.append(Endereco(
                id=re['id'],
                tipo=re['tipo'],
                cep=re['cep'],
                endereco=re['endereco'],
                numero=re['numero'],
                bairro=re['bairro'],
                cidade=re['cidade'],
                uf=re['uf'],
                complemento=re['complemento'], # <-- Acesso correto
                cidade_ibge=re['cidade_ibge']   # <-- Acesso correto
            ))

        # 🟡 3. BUSCAR CONTATOS (Corrigido sem o .get)
        query_conts = "SELECT * FROM entidade_contatos WHERE entidade_id = ?"
        rows_c = self.db.fetch_all(query_conts, (entidade_id,))
        for rc in rows_c:
            entidade.contatos.append(Contato(
                id=rc['id'],
                tipo=rc['tipo'],
                numero=rc['numero'],
                nome_contato=rc['nome_contato']
            ))

        if entidade.tipo_pessoa == 'PF':
            query_p = """
                SELECT s.*, e.nome_fantasia as nome_empresa 
                FROM socios s 
                JOIN entidades e ON s.entidade_pai_id = e.id 
                WHERE s.socio_entidade_id = ?
            """
            entidade.participacoes_societarias = self.db.fetch_all(query_p, (entidade_id,))

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


    def buscar_clientes(self):
        """Busca IDs tratando casos onde o booleano virou texto na revisão"""
        query = """
            SELECT id FROM entidades 
            WHERE eh_cliente = 1 
               OR eh_cliente = '1' 
               OR eh_cliente = 'S' 
               OR eh_cliente = 'TRUE'
            ORDER BY nome_fantasia
        """
        rows = self.db.fetch_all(query)
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

        # 🟡 NOVO: Atualiza um endereço específico pelo ID dele

    def atualizar_endereco_id(self, endereco_id: int, logradouro: str, numero: str,
                              complemento: str, bairro: str, cidade: str,
                              uf: str, cep: str) -> None:
        # 1. Montamos a Query (A ordem das '?' dita tudo)
        query = """
            UPDATE entidade_enderecos 
            SET 
                cep = ?,          -- 1ª ?
                endereco = ?,     -- 2ª ?
                numero = ?,       -- 3ª ?
                complemento = ?,  -- 4ª ?
                bairro = ?,       -- 5ª ?
                cidade = ?,       -- 6ª ?
                uf = ?            -- 7ª ?
            WHERE id = ?          -- 8ª ?
        """

        # 2. Montamos a tupla seguindo EXATAMENTE a ordem das interrogações acima
        params = (
            cep,  # 1
            logradouro,  # 2
            numero,  # 3
            complemento,  # 4
            bairro,  # 5
            cidade,  # 6
            uf,  # 7
            endereco_id  # 8 (Onde o ID é o filtro final)
        )

        self.db.execute(query, params)

    # 🟡 NOVO: Atualiza um contato específico pelo ID dele
    def atualizar_contato_id(self, contato_id: int, novo_numero: str) -> None:
        query = "UPDATE entidade_contatos SET numero = ? WHERE id = ?"
        self.db.execute(query, (novo_numero, contato_id))