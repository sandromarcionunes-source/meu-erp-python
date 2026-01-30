from models.dados_emissor import DadosEmissor
from typing import Any


class EmissorRepository:
    def __init__(self, db: Any):
        self.db = db

    def salvar(self, emissor: DadosEmissor) -> None:
        """Salva ou atualiza os dados do emissor (sempre ID 1)"""
        query = """
            INSERT OR REPLACE INTO dados_emissor (
                id, razao_social, nome_fantasia, cnpj, inscricao_estadual, 
                email, telefone, cep, endereco, numero, bairro, cidade, 
                uf, ibge_municipio, regime_tributario
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            emissor.razao_social, emissor.nome_fantasia, emissor.cnpj,
            emissor.inscricao_estadual, emissor.email, emissor.telefone,
            emissor.cep, emissor.endereco, emissor.numero, emissor.bairro,
            emissor.cidade, emissor.uf, emissor.ibge_municipio,
            emissor.regime_tributario
        )
        self.db.execute(query, params)

    def buscar(self) -> DadosEmissor | None:
        """Recupera os dados do emissor único e converte em objeto DadosEmissor"""
        row = self.db.fetch_one("SELECT * FROM dados_emissor WHERE id = 1")

        if not row:
            return None

        return DadosEmissor(
            id=row['id'],
            razao_social=row['razao_social'],
            nome_fantasia=row['nome_fantasia'],
            cnpj=row['cnpj'],
            inscricao_estadual=row['inscricao_estadual'],
            email=row['email'],
            telefone=row['telefone'],
            cep=row['cep'],
            endereco=row['endereco'],
            numero=row['numero'],
            bairro=row['bairro'],
            cidade=row['cidade'],
            uf=row['uf'],
            ibge_municipio=row['ibge_municipio'],
            regime_tributario=row['regime_tributario']
        )