import sys
import os

# from database.database_manager import SQLiteDatabaseManager

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.db_factory import DatabaseFactory
from repositories.produto_repository import ProdutoRepository
from repositories.pedido_repository import PedidoRepository
from repositories.entidade_repository import EntidadeRepository
from repositories.forma_pagamento_repository import FormaPagamentoRepository
from repositories.config_repository import ConfigRepository
from repositories.compra_repository import CompraRepository
from repositories.emissor_repository import EmissorRepository
from repositories.seguro_repository import SeguroRepository
from repositories.analise_credito_repository import AnaliseCreditoRepository
from repositories.nota_fiscal_vendas_repository import NotaFiscalRepository

from services.compra_service import CompraService
from services.produto_service import ProdutoService
from services.pedido_service import PedidoService
from services.database_service import DatabaseService
from services.entidade_service import EntidadeService
from services.config_service import ConfigService
from services.emissor_service import EmissorService
from services.seguro_service import SeguroService
from services.analise_credito_service import AnaliseCreditoService
from services.nota_fiscal_service import NotaFiscalService
from menus.menu_principal import MenuPrincipal

def rodar_sistema():
    while True:
        try:
            # Aqui chama o menu que você já tem
            MenuPrincipal()
        except KeyboardInterrupt:
            # Se o usuário apertar Ctrl+C em qualquer lugar do sistema...
            print("\n\n🔄 Operação cancelada pelo usuário. Retornando ao Menu Principal...")
            continue # Ele ignora o erro e volta para o início do loop


def main():
    # 1. Inicializa o Banco de Dados
    # O Factory já cuida de criar as tabelas automaticamente
    db = DatabaseFactory.get_database("sqlite")
    print(f"✅ Banco conectado com sucesso!")

    # 2. Inicializa os Repositórios
    # Eles são a ponte direta com as tabelas do banco

    repo_produto = ProdutoRepository(db)
    repo_pedido = PedidoRepository(db)
    repo_pagamento = FormaPagamentoRepository(db)
    repo_entidades = EntidadeRepository(db)
    repo_config = ConfigRepository(db)
    repo_compra = CompraRepository(db)
    repo_emissor = EmissorRepository(db)
    repo_seguro = SeguroRepository(db)
    analise_repo = AnaliseCreditoRepository(db)
    repo_nf_vendas = NotaFiscalRepository(db)

    # 3. Inicializa os Serviços
    service_analise = AnaliseCreditoService(analise_repo)
    service_entidade = EntidadeService(repo_entidades)
    service_produto = ProdutoService(repo_produto)
    service_pedido = PedidoService(
        repo_pedido,
        repo_entidades,
        repo_produto,
        repo_pagamento,
        service_analise,
        repo_config)
    service_compra = CompraService(repo_compra, repo_entidades, repo_produto, repo_config)
    service_seguro = SeguroService(repo_seguro, repo_entidades)
    service_configuracao = ConfigService(repo_config)
    service_banco_dados = DatabaseService(db)
    service_emissor = EmissorService(repo_emissor)
    service_nota_fiscal_vendas = NotaFiscalService(
        repo_nf_vendas,  # 1. NF
        repo_emissor,  # 2. Emissor (Sua empresa - DadosEmissor)
        repo_pedido,  # 3. Pedido
        repo_produto  # 4. Produto
    )

    # 4. Configura o Menu Principal
    # Mapeamos as opções do menu para as funções 'exibir_menu' de cada serviço
    modulos = {
        "1": {"nome": "Entidades", "funcao": service_entidade.exibir_menu},
        "2": {"nome": "Produtos", "funcao": service_produto.menu},
        "3": {"nome": "Pedidos", "funcao": service_pedido.exibir_menu},
        "4": {"nome": "Compras", "funcao": service_compra.exibir_menu},
        "5": {"nome": "Emissor", "funcao": service_emissor.exibir_menu},
        "6": {"nome": "Seguro", "funcao": service_seguro.exibir_menu},
        "7": {"nome": "Configuracoes diversas", "funcao": service_configuracao.exibir_menu},
        "8": {"nome": "Banco Dados", "funcao": service_banco_dados.exibir_menu},
        "9": {"nome": "Analise de credito", "funcao": service_analise.exibir_menu},
        "10": {"nome": "Nota fiscal Vendas", "funcao": service_nota_fiscal_vendas.exibir_menu},
    }

    menu = MenuPrincipal(modulos)

    # 5. "Loop" Principal com Escotilha de Escape (Ajustado)
    print("\n💡 DICA: Pressione Ctrl + C para cancelar qualquer ação e voltar ao Menu Principal.")


    menu.exibir()


if __name__ == "__main__":
    main()