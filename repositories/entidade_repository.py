from models.entidade import Entidade
from models.socio import Socio
from models.entidade_enderecos import Endereco
from models.entidade_contatos import Contato
from typing import List, Any, Optional


class EntidadeRepository:
    def __init__(self, db: Any):
        self.db = db

    def salvar(self, entidade: Entidade) -> int:
        """
        GRAVAÇÃO COMPLETA EM CASCATA:
        1. Salva a Entidade
        2. Recupera o ID gerado
        3. Salva Endereços e Contatos vinculados
        """
        # Evita duplicidade
        existente = self.buscar_por_cpf(entidade.documento)
        if existente and not entidade.id:
            return existente.id

        # INSERT DA TABELA PAI (entidades) - 19 colunas + ID automático
        query_pai = """
            INSERT INTO entidades (
                tipo_pessoa, nome_fantasia, razao_social, documento, 
                inscricao_estadual, inscricao_municipal, email_comercial, 
                email_nfe, regime_tributario, indicador_ie, limite_credito, 
                limite_validade, bloqueado, eh_cliente, eh_fornecedor, 
                eh_transportadora, eh_seguradora, data_cadastramento, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params_pai = (
            entidade.tipo_pessoa, entidade.nome_fantasia, entidade.razao_social,
            entidade.documento, entidade.inscricao_estadual, entidade.inscricao_municipal,
            entidade.email_comercial, entidade.email_nfe, entidade.regime_tributario,
            entidade.indicador_ie, entidade.limite_credito, entidade.limite_validade,
            1 if entidade.bloqueado else 0,
            1 if entidade.eh_cliente else 0, 1 if entidade.eh_fornecedor else 0,
            1 if entidade.eh_transportadora else 0, 1 if entidade.eh_seguradora else 0,
            entidade.data_cadastramento, entidade.observacoes
        )

        # Executa e captura o ID gerado (lastrowid)
        entidade_id = self.db.execute(query_pai, params_pai)
        entidade.id = entidade_id

        # 🟢 SALVAR ENDEREÇOS (Cascata)
        if entidade.enderecos:
            for end in entidade.enderecos:
                sql_end = """
                    INSERT INTO entidade_enderecos (
                        entidade_id, tipo, cep, endereco, numero, 
                        complemento, bairro, cidade, uf, cidade_ibge
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.db.execute(sql_end, (
                    entidade_id, end.tipo, end.cep, end.endereco, end.numero,
                    end.complemento, end.bairro, end.cidade, end.uf, end.cidade_ibge
                ))

        # 🟢 SALVAR CONTATOS (Cascata)
        if entidade.contatos:
            for cont in entidade.contatos:
                sql_cont = """
                    INSERT INTO entidade_contatos (
                        entidade_id, tipo, nome_contato, numero
                    ) VALUES (?, ?, ?, ?)
                """
                self.db.execute(sql_cont, (
                    entidade_id, cont.tipo, cont.nome_contato, cont.numero
                ))

        return entidade_id

    def buscar_por_id(self, entidade_id: int) -> Optional[Entidade]:
        """Carregamento mestre com loops forçados para sub-tabelas."""
        row_raw = self.db.fetch_one("SELECT * FROM entidades WHERE id = ?", (entidade_id,))
        if not row_raw: return None

        r = {k.lower(): v for k, v in dict(row_raw).items()}

        ent = Entidade(
            tipo_pessoa=r.get('tipo_pessoa', ''),
            nome_fantasia=r.get('nome_fantasia', ''),
            documento=r.get('documento', ''),
            razao_social=r.get('razao_social'),
            inscricao_estadual=r.get('inscricao_estadual'),
            inscricao_municipal=r.get('inscricao_municipal'),
            email_comercial=r.get('email_comercial'),
            email_nfe=r.get('email_nfe'),
            regime_tributario=r.get('regime_tributario'),
            indicador_ie=r.get('indicador_ie', '9'),
            limite_credito=float(r.get('limite_credito') or 0),
            limite_validade=r.get('limite_validade'),
            bloqueado=bool(r.get('bloqueado', 0)),
            eh_cliente=bool(r.get('eh_cliente', 0)),
            eh_fornecedor=bool(r.get('eh_fornecedor', 0)),
            eh_transportadora=bool(r.get('eh_transportadora', 0)),
            eh_seguradora=bool(r.get('eh_seguradora', 0)),
            data_cadastramento=r.get('data_cadastramento'),
            observacoes=r.get('observacoes'),
            id=r.get('id')
        )

        # 1. Endereços
        res_ends = self.db.fetch_all("SELECT * FROM entidade_enderecos WHERE entidade_id = ?", (entidade_id,))
        for re_raw in res_ends:
            re = {k.lower(): v for k, v in dict(re_raw).items()}
            ent.enderecos.append(Endereco(
                tipo=re.get('tipo'), cep=re.get('cep'), endereco=re.get('endereco'),
                numero=re.get('numero'), complemento=re.get('complemento'),
                bairro=re.get('bairro'), cidade=re.get('cidade'), uf=re.get('uf'),
                cidade_ibge=re.get('cidade_ibge'), id=re.get('id')
            ))

        # 2. Contatos
        res_conts = self.db.fetch_all("SELECT * FROM entidade_contatos WHERE entidade_id = ?", (entidade_id,))
        for rc_raw in res_conts:
            rc = {k.lower(): v for k, v in dict(rc_raw).items()}
            ent.contatos.append(Contato(
                tipo=rc.get('tipo'), numero=rc.get('numero'),
                nome_contato=rc.get('nome_contato'), id=rc.get('id')
            ))

        return ent

    def buscar_por_id_ou_documento(self, termo: str) -> Optional[Entidade]:
        """Busca o ID e delega para o buscar_por_id preencher as listas."""
        t = str(termo).replace(".", "").replace("-", "").replace("/", "").strip()
        if t.isdigit() and len(t) < 8:
            return self.buscar_por_id(int(t))
        row = self.db.fetch_one("SELECT id FROM entidades WHERE documento = ?", (t,))
        if row:
            rid = dict(row).get('id') or dict(row).get('ID')
            return self.buscar_por_id(rid)
        return None

    def buscar_por_cpf(self, cpf: str) -> Optional[Entidade]:
        return self.buscar_por_id_ou_documento(cpf)

    def buscar_clientes(self) -> List[Entidade]:
        rows = self.db.fetch_all("SELECT id FROM entidades WHERE eh_cliente = 1 ORDER BY nome_fantasia")
        return [self.buscar_por_id(dict(r).get('id') or dict(r).get('ID')) for r in rows]

    def atualizar_campo_dinamico(self, tabela: str, campo: str, valor: Any, id_reg: int):
        self.db.execute(f"UPDATE {tabela} SET {campo} = ? WHERE id = ?", (valor, id_reg))