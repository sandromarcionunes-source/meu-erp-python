import pytest
from database.database_manager import SQLiteDatabaseManager
from repositories.compra_repository import CompraRepository
from models.compra import Compra, CompraItem
from datetime import datetime


# --- AUXILIAR: A "FÁBRICA" QUE EVITA VOCÊ DIGITAR TUDO ---
def criar_compra_valida():
    # 1. Cabeçalho com campos exigidos pelo seu SQL (NOT NULL)
    compra = Compra(
        fornecedor_id=1,
        fornecedor_nome_snap="Fornecedor Teste",
        tipo_compra="REVENDA",
        data_emissao=datetime.now().strftime("%d/%m/%Y %H:%M")  # Resolve o erro do NOT NULL
    )

    # 2. Item com campos exigidos (quantidade, preco_custo, subtotal)
    # O seu modelo CompraItem já calcula o subtotal no __init__
    item = CompraItem(
        produto_id=10,
        produto_nome_snap="Produto Teste",
        quantidade=2.0,
        valor_unitario=50.0
    )

    compra.adicionar_item(item)

    # 3. Campos opcionais que o seu Repository salva
    compra.forma_pagamento = "PIX"
    compra.observacao = "Teste automatizado"

    return compra


# --- O TESTE PROPRIAMENTE DITO ---
def test_deve_salvar_pedido_e_itens_no_banco():
    # Setup - Usando :memory: para ser instantâneo e limpo
    db = SQLiteDatabaseManager(":memory:")
    db.connection.execute("PRAGMA foreign_keys = OFF;")
    repo = CompraRepository(db)

    # Ação - Usamos a nossa fábrica (Zero esforço de digitação aqui!)
    pedido = criar_compra_valida()
    id_gerado = repo.salvar(pedido)

    # Validação
    assert id_gerado is not None, "O ID deveria ter sido gerado pelo banco"

    # Verifica se o valor total foi calculado certo (2 * 50 = 100)
    venda_db = db.fetch_one("SELECT * FROM compras WHERE id = ?", (id_gerado,))
    assert venda_db['valor_total'] == 100.0
    assert venda_db['status'] == 'DIGITADO'

    # Verifica se o item caiu na tabela certa (compra_itens)
    item_db = db.fetch_one("SELECT * FROM compra_itens WHERE compra_id = ?", (id_gerado,))
    assert item_db is not None
    assert item_db['subtotal'] == 100.0