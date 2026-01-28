# repositories/cliente_repository.py
from database.db_interface import DatabaseInterface
from models.cliente import Cliente

class ClienteRepository:
    def __init__(self, db: DatabaseInterface):
        self.db = db

    def salvar(self, cliente: Cliente):
        query = """
            INSERT INTO clientes (tipo_pessoa, nome, razao_social, cpf, cnpj, cep, email, telefone, endereco, numero, complemento, bairro, cidade, uf, data_cadastramento, limite_credito)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (cliente.tipo_pessoa, cliente.nome, cliente.razao_social, cliente.cpf, cliente.cnpj, cliente.cep, cliente.email, cliente.telefone, cliente.endereco, cliente.numero, cliente.complemento,
                  cliente.bairro, cliente.cidade, cliente.uf, cliente.data_cadastramento, cliente.limite_credito)
        self.db.execute(query, params)

    def buscar_por_cpf(self, cpf: str):
        query = "SELECT * FROM clientes WHERE cpf = ?"
        cursor = self.db.execute(query, (cpf,))
        row = cursor.fetchone()

        if row:
            # Re-hidratação do objeto: transforma a linha do banco num objeto Cliente
            return Cliente(id=row[0], tipo_pessoa=row[1], nome=row[2], razao_social=row[3], cpf=row[4], cnpj=row[5], cep=row[6], email=row[7], telefone=row[8],  endereco=row[9], numero=row[10], complemento=row[11],
                           bairro=row[12], cidade=row[13], uf=row[14], data_cadastramento=row[15], limite_credito=row[16])
        return None

    def atualizar_campo_dinamico(self, cliente_id, campo, novo_valor):
        campos_validos = [
            "nome", "razao_social", "cpf", "cnpj", "cep", "email",
            "telefone", "endereco", "numero", "complemento",
            "bairro", "cidade", "uf", "data_cadastramento", "limite_credito"
        ]

        if campo not in campos_validos:
            raise ValueError("Campo inválido.")

        query = f"UPDATE clientes SET {campo} = ? WHERE id = ?"
        self.db.execute(query, (novo_valor, cliente_id))

    def buscar_por_id(self, id_cliente):
        """Busca um cliente específico pelo ID e retorna um objeto Cliente"""
        query = "SELECT * FROM clientes WHERE id = ?"

        # Executa a consulta
        resultado = self.db.fetch_all(query, (id_cliente,))

        if resultado:
            row = resultado[0]  # Pega o primeiro (e único) registro encontrado

            # Aqui transformamos a linha do banco de volta em um objeto Cliente
            # Importante: a ordem e os nomes devem bater com o seu Model!
            from models.cliente import Cliente  # Import local para evitar erro circular se necessário

            return Cliente(
                id=row['id'],
                tipo_pessoa=row['tipo_pessoa'],
                nome=row['nome'],
                razao_social=row['razao_social'],
                cpf=row['cpf'],
                cnpj=row['cnpj'],
                cep=row['cep'],
                email=row['email'],
                telefone=row['telefone'],
                endereco=row['endereco'],
                numero=row['numero'],
                complemento=row['complemento'],
                bairro=row['bairro'],
                cidade=row['cidade'],
                uf=row['uf'],
                data_cadastramento=row['data_cadastramento'],
                limite_credito=row['limite_credito']
            )

        return None  # Se não encontrar ninguém com esse ID

    def buscar_por_cpf(self, cpf):
        # Limpa pontos e traços caso o usuário digite com formatação
        cpf_limpo = cpf.replace(".", "").replace("-", "").strip()

        query = "SELECT * FROM clientes WHERE cpf = ?"
        resultado = self.db.fetch_all(query, (cpf_limpo,))

        if resultado:
            return resultado[0]  # Retorna o dicionário do cliente encontrado
        return None

    def buscar_flexivel(self, termo):
        """Busca por ID, CPF ou parte do Nome"""
        # Se o termo for apenas números, tenta ID ou CPF primeiro
        if termo.isdigit():
            query = "SELECT * FROM clientes WHERE id = ? OR cpf = ?"
            return self.db.fetch_all(query, (termo, termo))
        else:
            # Busca por parte do nome (o % permite encontrar em qualquer posição)
            query = "SELECT * FROM clientes WHERE nome LIKE ? OR razao_social LIKE ?"
            param = f"%{termo}%"
            return self.db.fetch_all(query, (param, param))