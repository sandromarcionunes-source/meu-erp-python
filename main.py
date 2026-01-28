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
from services.compra_service import CompraService
from services.produto_service import ProdutoService
from services.pedido_service import PedidoService
from services.database_service import DatabaseService
from services.entidade_service import EntidadeService
from services.config_service import ConfigService
from menus.menu_principal import MenuPrincipal


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

    # 3. Inicializa os Serviços
    service_entidade = EntidadeService(repo_entidades)
    service_produto = ProdutoService(repo_produto)
    service_pedido = PedidoService(repo_pedido,repo_entidades,repo_produto,repo_pagamento,repo_config)
    service_compra = CompraService(repo_compra, repo_entidades, repo_produto, repo_config)
    service_configuracao = ConfigService(repo_config)
    service_banco_dados = DatabaseService(db)

    # 4. Configura o Menu Principal
    # Mapeamos as opções do menu para as funções 'exibir_menu' de cada serviço
    modulos = {
        "1": {"nome": "Entidades", "funcao": service_entidade.exibir_menu},
        "2": {"nome": "Produtos", "funcao": service_produto.menu},
        "3": {"nome": "Pedidos", "funcao": service_pedido.exibir_menu},
        "4": {"nome": "Compras", "funcao": service_compra.exibir_menu},
        # REMOVIDOS os parênteses de exibir_menu, pois queremos passar a função, não o resultado dela
        "5": {"nome": "Configuracoes diversas", "funcao": service_configuracao.exibir_menu},
        "6": {"nome": "Banco Dados", "funcao": service_banco_dados.exibir_menu},
    }

    menu = MenuPrincipal(modulos)

    # 5. "Loop" Principal do Sistema
    try:
        menu.exibir()
    except KeyboardInterrupt:
        print("\n\nSaindo do sistema... Até logo! 👋")
    except Exception as e:
        print(f"\n❌ Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()