from models.entidade import Entidade
from models.socio import Socio
from models.entidade_enderecos import Endereco
from models.entidade_contatos import Contato
from typing import List, Any, Optional


class EntidadeRepository:
    def __init__(self, db: Any):
        self.db = db

    def salvar(self, entidade: Entidade) -> int:
        # Verifica se já existe pelo documento (CPF/CNPJ)
        existente = self.buscar_por_cpf(entidade.documento)
        if existente and not entidade.id:
            return existente.id

        # INSERT completo com as 17 colunas do seu Schema
        query = """
            INSERT INTO entidades (
                tipo_pessoa, nome_fantasia, razao_social, documento, 
                inscricao_estadual, inscricao_municipal, email_comercial, 
                email_nfe, regime_tributario, indicador_ie, limite_credito, limite_validade,
                observacoes, eh_cliente, eh_fornecedor, eh_transportadora, 
                eh_seguradora, data_cadastramento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            entidade.tipo_pessoa, entidade.nome_fantasia, entidade.razao_social,
            entidade.documento, entidade.inscricao_estadual, entidade.inscricao_municipal,
            entidade.email_comercial, entidade.email_nfe, entidade.regime_tributario,
            entidade.indicador_ie, entidade.limite_credito, entidade.limite_validade, entidade.observacoes,
            1 if entidade.eh_cliente else 0, 1 if entidade.eh_fornecedor else 0,
            1 if entidade.eh_transportadora else 0, 1 if entidade.eh_seguradora else 0,
            entidade.data_cadastramento
        )
        entidade_id = self.db.execute(query, params)

        # Salva os Sócios (Quadro Societário)
        for s in entidade.socios:
            self.db.execute("""
                INSERT INTO socios (entidade_pai_id, socio_entidade_id, percentual_participacao, data_entrada, cargo, nome_snapshot)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (entidade_id, s.socio_entidade_id, s.participacao, s.data_entrada, s.cargo, s.nome_snapshot))

        # Salva os Endereços
        for e in entidade.enderecos:
            self.db.execute("""
                INSERT INTO entidade_enderecos (entidade_id, tipo, cep, endereco, numero, complemento, bairro, cidade, uf, cidade_ibge)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (entidade_id, e.tipo, e.cep, e.endereco, e.numero, e.complemento, e.bairro, e.cidade, e.uf, e.cidade_ibge))

        # Salva os Contatos
        for c in entidade.contatos:
            self.db.execute(
                "INSERT INTO entidade_contatos (entidade_id, tipo, numero, nome_contato) VALUES (?, ?, ?, ?)",
                (entidade_id, c.tipo, c.numero, c.nome_contato))

        return entidade_id

    def buscar_por_id(self, entidade_id: int) -> Entidade | None:
        row = self.db.fetch_one("SELECT * FROM entidades WHERE id = ?", (entidade_id,))
        if not row: return None

        # Mapeamento exato para o Construtor da Classe Entidade
        ent = Entidade(
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
            limite_validade=row['limite_validade'],
            observacoes=row['observacoes'],
            eh_cliente=bool(row['eh_cliente']),
            eh_fornecedor=bool(row['eh_fornecedor']),
            eh_transportadora=bool(row['eh_transportadora']),
            eh_seguradora=bool(row['eh_seguradora']),
            id=row['id'],
            data_cadastramento=row['data_cadastramento']
        )

        # Carregar Sócios
        sql_socios = "SELECT s.*, e.nome_fantasia as nome_ent FROM socios s JOIN entidades e ON s.socio_entidade_id = e.id WHERE s.entidade_pai_id = ?"
        for rs in self.db.fetch_all(sql_socios, (entidade_id,)):
            ent.socios.append(Socio(
                id=rs['id'],
                socio_entidade_id=rs['socio_entidade_id'],
                participacao=rs['percentual_participacao'],
                data_entrada=rs['data_entrada'],
                cargo=rs['cargo'],
                nome_snapshot=rs['nome_ent']
            ))

        # Carregar Endereços - CORREÇÃO: Acesso direto por chave ['cidade_ibge']
        for re in self.db.fetch_all("SELECT * FROM entidade_enderecos WHERE entidade_id = ?", (entidade_id,)):
            ent.enderecos.append(Endereco(
                tipo=re['tipo'],
                cep=re['cep'],
                endereco=re['endereco'],
                numero=re['numero'],
                complemento=re['complemento'],
                bairro=re['bairro'],
                cidade=re['cidade'],
                uf=re['uf'],
                cidade_ibge=re['cidade_ibge'], # Removido o .get()
                id=re['id']
            ))

        # Carregar Contatos
        for rc in self.db.fetch_all("SELECT * FROM entidade_contatos WHERE entidade_id = ?", (entidade_id,)):
            ent.contatos.append(Contato(
                tipo=rc['tipo'],
                numero=rc['numero'],
                nome_contato=rc['nome_contato'],
                id=rc['id']
            ))

        return ent

    # ... buscar_por_cpf e outros métodos permanecem iguais
    def buscar_por_cpf(self, cpf: str) -> Entidade | None:
        doc = str(cpf).replace(".", "").replace("-", "").replace("/", "").strip()
        row = self.db.fetch_one("SELECT id FROM entidades WHERE documento = ?", (doc,))
        return self.buscar_por_id(row['id']) if row else None

    def buscar_por_id_ou_documento(self, termo: str) -> Entidade | None:
        t = str(termo).replace(".", "").replace("-", "").replace("/", "").strip()
        row = self.db.fetch_one("SELECT id FROM entidades WHERE documento = ? OR id = ?", (t, t))
        return self.buscar_por_id(row['id']) if row else None

    def buscar_clientes(self):
        rows = self.db.fetch_all("SELECT id FROM entidades WHERE eh_cliente = 1 ORDER BY nome_fantasia")
        return [self.buscar_por_id(r['id']) for r in rows]

    def atualizar_campo_dinamico(self, tabela, campo, valor, id_registro):
        self.db.execute(f"UPDATE {tabela} SET {campo} = ? WHERE id = ?", (valor, id_registro))

    def excluir_socio(self, socio_vinc_id):
        self.db.execute("DELETE FROM socios WHERE id = ?", (socio_vinc_id,))

    def buscar_por_id_dados_puros(self, id_entidade):
        sql = "SELECT * FROM entidades WHERE id = ?"
        return self.db.fetch_one(sql, (id_entidade,))

    def buscar_flexivel(self, termo):
        """
        FUNÇÃO ORIGINAL RECUPERADA:
        Usa o fetch_all do DatabaseManager para buscar por ID, Documento ou Nome.
        """
        sql = """
            SELECT * FROM entidades 
            WHERE (id = ? OR documento = ? OR nome_fantasia LIKE ? OR razao_social LIKE ?)
        """
        # Preparação dos parâmetros para busca exata (ID/Doc) e parcial (Nomes)
        params = (termo, termo, f"%{termo}%", f"%{termo}%")

        try:
            # Esta é a chamada que o seu sistema já conhece e confia
            return self.db.fetch_all(sql, params)
        except Exception as e:
            print(f"❌ Erro na busca flexível original: {e}")
            return []