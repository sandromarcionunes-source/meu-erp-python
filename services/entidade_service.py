from models.entidade import Entidade
from models.socio import Socio
from models.entidade_enderecos import Endereco
from models.entidade_contatos import Contato
from datetime import datetime
from typing import List

class EntidadeService:
    def __init__(self, repo):
        self.repo = repo

    def selecionar_opcao(self, titulo: str, opcoes: dict) -> str:
        """Retorna o VALOR da opção (ex: 'SIMPLES')"""
        while True:
            print(f"\n--- {titulo} ---")
            for k, v in opcoes.items():
                print(f"{k}. {v}")
            esc = input("Selecione uma opção: ").strip()
            if esc in opcoes:
                return opcoes[esc]
            print("⚠️ Opção inválida! Tente novamente.")

    def selecionar_opcao_chave(self, titulo: str, opcoes: dict) -> str:
        """Retorna a CHAVE da opção (ex: '1', '2' ou '9')"""
        while True:
            print(f"\n--- {titulo} ---")
            for k, v in opcoes.items():
                print(f"{k}. {v}")
            esc = input("Selecione uma opção: ").strip()
            if esc in opcoes:
                return esc  # Retorna a chave (o número digitado)
            print("⚠️ Opção inválida! Tente novamente.")



    def exibir_menu(self):
        while True:
            print("\n" + "═" * 45 + f"\n{'👥 GESTÃO DE ENTIDADES':^45}\n" + "═" * 45)
            print("1. 📝 Cadastrar Nova Entidade")
            print("2. 📋 Listar Clientes (Resumo)")
            print("3. 🔍 Consulta Detalhada (Ficha)")
            print("4. 🔎 Revisão Geral (Mestre/Ends/Conts)")
            print("5. 🤝 GESTÃO DE SÓCIOS (I/A/E)")
            print("6. 🤝 Alterar todos os dados de Entidades(Somente para Administrador)")
            print("0. ⬅️  Voltar")
            op = input("\nEscolha: ")
            if op == "1":
                self.cadastrar_entidade()
            elif op == "2":
                self.listar_clientes_resumido()
            elif op == "3":
                self.consultar_detalhes()
            elif op == "4":
                self.revisao_geral_completa()
            elif op == "5":
                self.gestao_socios()
            elif op == "6":
                self.editar_entidade_completa()
            elif op == "0":
                break

    def gestao_socios(self):
        """Módulo para Incluir, Alterar e Excluir Sócios (Opção 5) - VERSÃO INTEGRAL"""
        termo = input("\n🔎 Digite o ID ou CPF/CNPJ da Empresa (PJ): ")
        ent = self.repo.buscar_por_id_ou_documento(termo)

        if not ent:
            return print("❌ Empresa não encontrada.")
        if ent.tipo_pessoa != 'PJ':
            return print("❌ Apenas entidades PJ possuem quadro societário.")

        print("\n" + "─" * 70 + f"\n{'QUADRO SOCIETÁRIO: ' + ent.nome_fantasia:^70}\n" + "─" * 70)

        if not ent.socios:
            print(f"{'⚠️ Nenhum sócio vinculado.':^70}")
        else:
            print(f"{'Nº':<3} | {'SÓCIO':<25} | {'PART.':>6} | {'CARGO':<15} | {'ENTRADA'}")
            print("-" * 70)
            for i, s in enumerate(ent.socios):
                dt_ex = s.data_entrada if hasattr(s, 'data_entrada') and s.data_entrada else "N/A"
                print(f"{i + 1:<3} | {s.nome_snapshot[:25]:<25} | {s.participacao:>5}% | {s.cargo:<15} | {dt_ex}")

        print("\n" + "─" * 70)
        print("[A] Incluir Novo  [E] Editar Existente  [R] Remover  [S] Sair")
        acao = input("Ação: ").upper().strip()

        # --- [A] INCLUIR NOVO SÓCIO ---
        if acao == 'A':
            doc_s = input("CPF/CNPJ do Novo Sócio: ").strip()
            s_db = self.repo.buscar_por_cpf(doc_s)

            if not s_db:
                print("Sócio não cadastrado. Criando cadastro básico...")
                nome_s = input("Nome do Sócio: ").strip().upper()
                s_id = self.repo.salvar(Entidade(
                    tipo_pessoa='PF',
                    nome_fantasia=nome_s,
                    documento=doc_s,
                    data_cadastramento=datetime.now().strftime("%Y-%m-%d %H:%M")
                ))
            else:
                s_id = s_db.id

            try:
                part = float(input("Porcentagem (%): ").replace(',', '.'))
                cargo = input("Cargo: ").strip().upper() or "SÓCIO"

                # Data de Entrada conforme Livro de Regras
                data_hoje = datetime.now().strftime("%d/%m/%Y")
                data_entrada = input(f"Data de Entrada [{data_hoje}]: ").strip() or data_hoje

                self.repo.db.execute("""
                    INSERT INTO socios (entidade_pai_id, socio_entidade_id, percentual_participacao, data_entrada, cargo)
                    VALUES (?, ?, ?, ?, ?)
                """, (ent.id, s_id, part, data_entrada, cargo))

                print(f"✅ Sócio vinculado com sucesso em {data_entrada}!")
            except ValueError:
                print("❌ Erro: Porcentagem inválida.")

        # --- [E] EDITAR SÓCIO EXISTENTE ---
        elif acao == 'E' and ent.socios:
            try:
                idx = int(input("Número do sócio para editar: ")) - 1
                if 0 <= idx < len(ent.socios):
                    s_alvo = ent.socios[idx]
                    print(f"\nEditando: {s_alvo.nome_snapshot}")

                    n_part = input(f"Nova % [{s_alvo.participacao}]: ").strip()
                    n_cargo = input(f"Novo Cargo [{s_alvo.cargo}]: ").strip()
                    n_data = input(f"Nova Data [{s_alvo.data_entrada}]: ").strip()

                    if n_part:
                        self.repo.atualizar_campo_dinamico("socios", "percentual_participacao",
                                                           float(n_part.replace(',', '.')), s_alvo.id)
                    if n_cargo:
                        self.repo.atualizar_campo_dinamico("socios", "cargo", n_cargo.upper(), s_alvo.id)
                    if n_data:
                        self.repo.atualizar_campo_dinamico("socios", "data_entrada", n_data, s_alvo.id)

                    print("✅ Sócio atualizado!")
                else:
                    print("❌ Número inválido.")
            except ValueError:
                print("❌ Digite um número válido.")

        # --- [R] REMOVER SÓCIO (O QUE ESTAVA FALTANDO) ---
        elif acao == 'R' and ent.socios:
            try:
                idx = int(input("Número do sócio para REMOVER: ")) - 1
                if 0 <= idx < len(ent.socios):
                    s_alvo = ent.socios[idx]
                    confirma = input(f"⚠️ Tem certeza que deseja remover {s_alvo.nome_snapshot}? (S/N): ").upper()
                    if confirma == 'S':
                        # Deleta o vínculo da tabela de sócios
                        self.repo.db.execute("DELETE FROM socios WHERE id = ?", (s_alvo.id,))
                        print(f"🗑️ Sócio {s_alvo.nome_snapshot} removido do quadro.")
                else:
                    print("❌ Número inválido.")
            except ValueError:
                print("❌ Digite um número válido.")

        elif acao == 'S':
            return

    def consultar_detalhes(self):
        """OPÇÃO 3: Exibição completa e organizada de todos os dados."""
        # Aplicando sua mudança de 'Documento' para 'CPF/CNPJ'
        termo = input("\n🔎 Digite o ID ou CPF/CNPJ para consulta: ")
        ent = self.repo.buscar_por_id_ou_documento(termo)
        if not ent:
            return print("❌ Registro não localizado.")

        print("\n" + "═" * 80)
        print(f"{'FICHA CADASTRAL DETALHADA':^80}")
        print("═" * 80)

        # Bloco 1: Identificação Principal
        print(f"👤 NOME FANTASIA: {ent.nome_fantasia}")
        print(f"🏢 RAZÃO SOCIAL:  {ent.razao_social}")
        print(f"📄 CPF/CNPJ:      {ent.documento} ({ent.tipo_pessoa})")
        print(f"📅 CADASTRO EM:   {ent.data_cadastramento}")
        print("-" * 80)

        # Bloco 2: Dados Fiscais e Tributários
        print(
            f"📊 REGIME: {ent.regime_tributario or 'N/A':<15} | IE: {ent.inscricao_estadual or 'ISENTO':<15} | IM: {ent.inscricao_municipal or 'N/A'}")
        print(f"✉️  EMAIL COM.: {ent.email_comercial or 'N/A':<30} | EMAIL NFE: {ent.email_nfe or 'N/A'}")
        print(f"💰 LIMITE CRÉDITO: R$ {ent.limite_credito:,.2f} | 📅 VALIDADE: {ent.limite_validade}")
        print(f"📝 OBSERVAÇÕES: {ent.observacoes or 'Nenhum registro.'}")
        print("-" * 80)

        # Bloco 3: Quadro Societário (Se for PJ ou tiver vínculos)
        if ent.socios:
            titulo = "SÓCIOS / PROPRIETÁRIOS" if ent.tipo_pessoa == 'PJ' else "PARTICIPAÇÕES EM EMPRESAS"
            print(f"🔗 {titulo}:")
            for s in ent.socios:
                print(f"   • {s.nome_snapshot:<35} | Participação: {s.participacao:>5.1f}% | Cargo: {s.cargo}")
            print("-" * 80)

        # Bloco 4: Endereços (Recuperando a visualização completa com Complemento)
        if ent.enderecos:
            print("🏠 ENDEREÇOS:")
            for e in ent.enderecos:
                comp = f" ({e.complemento})" if e.complemento else ""
                print(f"   • [{e.tipo}] {e.endereco}, {e.numero}{comp} - {e.bairro} - {e.cidade}/{e.uf} - CEP: {e.cep}")
        else:
            print("🏠 ENDEREÇOS: Nenhum endereço cadastrado.")
        print("-" * 80)

        # Bloco 5: Contatos
        if ent.contatos:
            print("📞 CONTATOS:")
            for c in ent.contatos:
                print(f"   • {c.tipo:<10}: {c.numero:<15} | Ref: {c.nome_contato or 'Geral'}")
        else:
            print("📞 CONTATOS: Nenhum contato cadastrado.")

        print("═" * 80)
        input("\n[Pressione Enter para voltar ao menu]")

    def listar_clientes_resumido(self):
        """OPÇÃO 2: Listagem organizada com larguras fixas e correção de formato."""
        try:
            clientes = self.repo.buscar_clientes()
            if not clientes:
                print("\n⚠️ Nenhum cliente cadastrado no sistema.")
                input("\n[Pressione Enter para voltar]")
                return

            # Definição de Larguras (Total ajustado para 100 caracteres)
            L_ID = 5
            L_CLI = 30
            L_DOC = 18
            L_SOC = 30
            L_PER = 8

            print("\n" + "═" * 105)
            print(f"{'RELATÓRIO DE VÍNCULOS E QUADRO SOCIETÁRIO':^105}")
            print("═" * 105)

            # Cabeçalho
            header = (
                f"{'ID':<{L_ID}} | "
                f"{'CLIENTE / EMPRESA':<{L_CLI}} | "
                f"{'DOCUMENTO':<{L_DOC}} | "
                f"{'SÓCIO/VÍNCULO':<{L_SOC}} | "
                f"{'%':>{L_PER}}"
            )
            print(header)
            print("─" * 105)

            for c in clientes:
                # CORREÇÃO AQUI: Formatamos o ID separado da largura
                id_formatado = f"{c.id:03d}"
                doc_formatado = str(c.documento) if c.documento else "N/A"

                if not c.socios:
                    print(
                        f"{id_formatado:<{L_ID}} | "
                        f"{c.nome_fantasia[:L_CLI]:<{L_CLI}} | "
                        f"{doc_formatado[:L_DOC]:<{L_DOC}} | "
                        f"{'--':<{L_SOC}} | "
                        f"{'--':>{L_PER}}"
                    )
                else:
                    for i, s in enumerate(c.socios):
                        nome_socio = s.nome_snapshot if s.nome_snapshot else "N/A"
                        # Tratando a porcentagem para evitar erro se for None
                        perc_valor = s.participacao if s.participacao is not None else 0.0
                        perc_socio = f"{perc_valor:.1f}%"

                        if i == 0:
                            print(
                                f"{id_formatado:<{L_ID}} | "
                                f"{c.nome_fantasia[:L_CLI]:<{L_CLI}} | "
                                f"{doc_formatado[:L_DOC]:<{L_DOC}} | "
                                f"{nome_socio[:L_SOC]:<{L_SOC}} | "
                                f"{perc_socio:>{L_PER}}"
                            )
                        else:
                            print(
                                f"{' ':<{L_ID}} | "
                                f"{' ':<{L_CLI}} | "
                                f"{' ':<{L_DOC}} | "
                                f"{nome_socio[:L_SOC]:<{L_SOC}} | "
                                f"{perc_socio:>{L_PER}}"
                            )
                print("-" * 105)

            print(f"\n💡 DICA: Use a Opção 3 para ficha detalhada ou '..' para sair.")
            res = input("\n[Enter para voltar]: ").strip()
            if res == "..":
                # Em vez de sys.exit, vamos apenas retornar para o menu
                return

        except Exception as e:
            print(f"\n❌ Erro ao gerar relatório: {e}")
            input("Pressione Enter para continuar...")

    def cadastrar_entidade(self):
        print("\n" + "─" * 55 + f"\n{'🆕 NOVO CADASTRO':^55}\n" + "─" * 55)

        # 1. Validação de Tipo (PF/PJ)
        while True:
            tipo_input = input("Tipo (1-PF / 2-PJ): ").strip()
            if tipo_input == '1':
                tipo = 'PF'
                break
            elif tipo_input == '2':
                tipo = 'PJ'
                break
            else:
                print('⚠️ Opção inválida!')

        doc = input("Informe o CPF/CNPJ: ").strip()
        if self.repo.buscar_por_cpf(doc):
            return print(f"❌ CPF/CNPJ já cadastrado!")

        nome = input("Nome Fantasia: ").strip()
        razao = input("Razão Social: ").strip()

        # 2. Dados Fiscais (Mapeando códigos numéricos conforme o Schema)
        ie = input("Inscrição Estadual (ISENTO se não houver): ").strip()
        im = input("Inscrição Municipal: ").strip()

        # IMPORTANTE: Pegamos a CHAVE (1, 2 ou 9) para salvar no banco
        ind_ie = self.selecionar_opcao_chave("INDICADOR DE IE", {
            "1": "CONTRIBUINTE",
            "2": "CONTRIBUINTE ISENTO",
            "9": "NAO_CONTRIBUINTE"
        })

        regime = self.selecionar_opcao("REGIME", {
            "1": "MEI",
            "2": "SIMPLES",
            "3": "PRESUMIDO",
            "4": "REAL"
        })

        # 3. Comunicação e Financeiro
        email_c = input("E-mail Comercial: ").strip()
        email_n = input("E-mail p/ NFe: ").strip()
        limite = input("Limite de Crédito: ").replace(',', '.') or "0"

        hoje_br = datetime.now().strftime("%d/%m/%Y")
        print(f"📅 Validade do Limite [Padrão: {hoje_br}]")
        val_input = input("Informe a data (DD/MM/AAAA) ou [ENTER]: ").strip()
        validade_final = self.converter_data_br_para_iso(val_input if val_input else hoje_br)

        obs = input("Observações: ").strip()

        # 4. Bandeiras de Perfil
        print("\n--- Perfil da Entidade ---")
        e_for = input("É Fornecedor? (S/N): ").upper() == 'S'
        e_tra = input("É Transportadora? (S/N): ").upper() == 'S'
        e_seg = input("É Seguradora? (S/N): ").upper() == 'S'

        # 5. Criação do Objeto (Bate 100% com o seu __init__)
        ent = Entidade(
            tipo_pessoa=tipo,
            nome_fantasia=nome,
            documento=doc,
            razao_social=razao,
            inscricao_estadual=ie,
            inscricao_municipal=im,
            email_comercial=email_c,
            email_nfe=email_n,
            regime_tributario=regime,
            indicador_ie=ind_ie,  # Aqui vai "1", "2" ou "9"
            limite_credito=float(limite),
            limite_validade=validade_final,
            observacoes=obs,
            eh_cliente=True,  # Definido como cliente neste fluxo
            eh_fornecedor=e_for,
            eh_transportadora=e_tra,
            eh_seguradora=e_seg,
            data_cadastramento=datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        # 6. Listas Vinculadas
        ent.enderecos = self.fluxo_endereco()
        ent.contatos = self.fluxo_contato()

        # 7. Persistência
        self.repo.salvar(ent)
        print("\n✅ CADASTRO REALIZADO COM SUCESSO!")

    def revisao_geral_completa(self):
        """MÉTODO RESTAURADO: Revisão Mestre + Endereços + Contatos"""
        termo = input("\n🔎 Digite o ID ou CPF/CNPJ para Revisão Total: ")
        ent = self.repo.buscar_por_id_ou_documento(termo)
        if not ent:
            return print("❌ Registro não localizado para revisão.")

        print("\n" + "═" * 60)
        print(f"{'MODO DE REVISÃO TOTAL: ' + ent.nome_fantasia:^60}")
        print("═" * 60)

        # 1. DADOS MESTRES (ENTIDADE)
        print("\n[1/3] DADOS CADASTRAIS (Deixe vazio para manter o atual):")
        campos = [
            ("Nome Fantasia", "nome_fantasia", ent.nome_fantasia),
            ("Razão Social", "razao_social", ent.razao_social),
            ("E-mail Comercial", "email_comercial", ent.email_comercial),
            ("E-mail NFe", "email_nfe", ent.email_nfe),
            ("Regime Tributário", "regime_tributario", ent.regime_tributario),
            ("Limite de Crédito", "limite_credito", ent.limite_credito),
            ("Observações", "observacoes", ent.observacoes)
        ]
        for rotulo, col, atual in campos:
            novo = input(f"🔹 {rotulo} [{atual}]: ").strip()
            if novo:
                self.repo.atualizar_campo_dinamico("entidades", col, novo.upper(), ent.id)

        # 2. REVISÃO/INCLUSÃO DE ENDEREÇOS
        print("\n[2/3] ENDEREÇOS:")
        if ent.enderecos:
            for e in ent.enderecos:
                print(f"--- Editando Endereço: {e.tipo} ---")
                e_campos = [
                    ("CEP", "cep", e.cep),
                    ("Rua", "endereco", e.endereco),
                    ("Nº", "numero", e.numero),
                    ("Complemento", "complemento", e.complemento),
                    ("Bairro", "bairro", e.bairro),
                    ("Cidade", "cidade", e.cidade),
                    ("UF", "uf", e.uf)
                ]
                for rot, col, val in e_campos:
                    n = input(f"   🏠 {rot} [{val}]: ").strip()
                    if n:
                        self.repo.atualizar_campo_dinamico("entidade_enderecos", col, n.upper(), e.id)

        if input("\n➕ Deseja incluir um NOVO endereço nesta revisão? (S/N): ").upper() == 'S':
            novos_ends = self.fluxo_endereco()
            for ne in novos_ends:
                self.repo.db.execute("""
                    INSERT INTO entidade_enderecos (entidade_id, tipo, cep, endereco, numero, complemento, bairro, cidade, uf)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (ent.id, ne.tipo, ne.cep, ne.endereco, ne.numero, ne.complemento, ne.bairro, ne.cidade, ne.uf))
                print(f"   ✔️ Novo endereço ({ne.tipo}) adicionado.")

        # 3. REVISÃO/INCLUSÃO DE CONTATOS
        print("\n[3/3] CONTATOS:")
        if ent.contatos:
            for c in ent.contatos:
                print(f"--- Editando Contato: {c.tipo} ---")
                n_contato = input(f"   📞 Número [{c.numero}]: ").strip()
                if n_contato:
                    self.repo.atualizar_campo_dinamico("entidade_contatos", "numero", n_contato, c.id)
                n_nome = input(f"   👤 Nome Contato [{c.nome_contato}]: ").strip()
                if n_nome:
                    self.repo.atualizar_campo_dinamico("entidade_contatos", "nome_contato", n_nome.upper(), c.id)

        if input("\n➕ Deseja incluir um NOVO contato nesta revisão? (S/N): ").upper() == 'S':
            novos_conts = self.fluxo_contato()
            for nc in novos_conts:
                self.repo.db.execute("""
                    INSERT INTO entidade_contatos (entidade_id, tipo, numero, nome_contato)
                    VALUES (?, ?, ?, ?)
                """, (ent.id, nc.tipo, nc.numero, nc.nome_contato))
                print(f"   ✔️ Novo contato ({nc.tipo}) adicionado.")

        print("\n✅ REVISÃO FINALIZADA E DADOS ATUALIZADOS!")
        input("[Enter para sair]")

    def fluxo_endereco(self):
        lista = []
        while input("\n🏠 Cadastrar endereço? (S/N): ").upper() == 'S':
            t = self.selecionar_opcao("TIPO", {"1": "PRINCIPAL", "2": "COBRANÇA", "3": "ENTREGA"})
            lista.append(Endereco(tipo=t, cep=input("   CEP: "), endereco=input("   Rua: "), numero=input("   Nº: "),
                                  complemento=input("   Compl: "), bairro=input("   Bairro: "),
                                  cidade=input("   Cidade: "), uf=input("   UF: ").upper()))
        return lista

    def fluxo_contato(self) -> List[Contato]:
        """
        MÉTODO INTEGRAL: Realiza a captura de múltiplos contatos.
        Cobre 100% das colunas da tabela 'entidade_contatos'.
        """
        lista: List[Contato] = []

        while True:
            confirmacao = input("\n📞 Deseja cadastrar um contato? (S/N): ").upper().strip()
            if confirmacao != 'S':
                break

            # 1. TIPO (Conforme Schema: 'CELULAR', 'FIXO', 'WHATSAPP')
            # Usando o dicionário para mapear a escolha do usuário
            opcoes_tipo = {"1": "WHATSAPP", "2": "CELULAR", "3": "FIXO"}
            tipo_selecionado = self.selecionar_opcao("TIPO DE CONTATO", opcoes_tipo)

            # 2. NÚMERO (NOT NULL no Schema)
            while True:
                numero = input("   Nº do Telefone/WhatsApp: ").strip()
                if numero:
                    break
                print("   ⚠️ O número é obrigatório para o cadastro de contatos.")

            # 3. NOME DO CONTATO (Coluna 'nome_contato' do Schema)
            # Ex: 'Setor de Compras', 'João Gerente'
            nome = input("   Nome da Pessoa ou Setor: ").strip().upper()

            # 4. INSTANCIAÇÃO E ADIÇÃO À LISTA
            # Criamos o objeto Contato passando todos os parâmetros
            novo_contato = Contato(
                tipo=tipo_selecionado,
                numero=numero,
                nome_contato=nome
            )

            lista.append(novo_contato)
            print(f"   ✔️ Contato '{nome}' adicionado com sucesso.")

        return lista

    def editar_entidade_completa(self):
        """
        ALTERAÇÃO TOTAL E ABSOLUTA: Mapeamento fiel ao Schema Completo.
        Não suprime nenhum campo das tabelas Entidades, Endereços, Contatos e Sócios.
        """
        termo = input("\n🔎 Digite o ID ou CPF/CNPJ para ALTERAÇÃO TOTAL: ")
        ent = self.repo.buscar_por_id_ou_documento(termo)

        if not ent:
            return print("❌ Registro não localizado para alteração.")

        print("\n" + "═" * 80)
        print(f"{'MODO EDIÇÃO MESTRE: ' + ent.nome_fantasia:^80}")
        print(f"{'Pressione [ENTER] para manter o valor atual':^80}")
        print("═" * 80)

        # --- 1. TABELA: entidades (TODOS OS CAMPOS) ---
        campos_mestre = [
            ("Tipo (PF/PJ)", "tipo_pessoa", ent.tipo_pessoa),
            ("Nome Fantasia", "nome_fantasia", ent.nome_fantasia),
            ("Razão Social", "razao_social", ent.razao_social),
            ("Documento (CPF/CNPJ)", "documento", ent.documento),
            ("Inscrição Estadual", "inscricao_estadual", ent.inscricao_estadual),
            ("Inscrição Municipal", "inscricao_municipal", ent.inscricao_municipal),
            ("E-mail Comercial", "email_comercial", ent.email_comercial),
            ("E-mail NFe", "email_nfe", ent.email_nfe),
            ("Regime Tributário", "regime_tributario", ent.regime_tributario),
            ("Indicador IE", "indicador_ie", ent.indicador_ie),
            ("Limite de Crédito", "limite_credito", ent.limite_credito),
            ("Observações", "observacoes", ent.observacoes),
        ]

        for rotulo, col, atual in campos_mestre:
            novo = input(f"🔹 {rotulo} [{atual}]: ").strip()
            if novo:
                valor = float(novo.replace(',', '.')) if col == "limite_credito" else novo.upper()
                self.repo.atualizar_campo_dinamico("entidades", col, valor, ent.id)

        # --- 2. FLAGS DE PERFIL (BOOLEANS) ---
        print("\n--- Perfil da Entidade ---")
        flags = [
            ("É Cliente?", "eh_cliente", ent.eh_cliente),
            ("É Fornecedor?", "eh_fornecedor", ent.eh_fornecedor),
            ("É Transportadora?", "eh_transportadora", ent.eh_transportadora),
            ("É Seguradora?", "eh_seguradora", ent.eh_seguradora)
        ]
        for rotulo, col, atual in flags:
            novo = input(f"🔹 {rotulo} (S/N) [{'S' if atual else 'N'}]: ").strip().upper()
            if novo in ['S', 'N']:
                self.repo.atualizar_campo_dinamico("entidades", col, 1 if novo == 'S' else 0, ent.id)

        # --- 3. TABELA: entidade_enderecos (TODOS OS CAMPOS) ---
        if ent.enderecos:
            print("\n" + "─" * 40 + "\n📍 EDITANDO ENDEREÇOS\n" + "─" * 40)
            for end in ent.enderecos:
                print(f"\nID Endereço: {end.id} [{end.tipo}]")
                campos_end = [
                    ("Tipo (PRINCIPAL/ENTREGA/COBRANCA)", "tipo", end.tipo),
                    ("CEP", "cep", end.cep),
                    ("Endereço", "endereco", end.endereco),
                    ("Número", "numero", end.numero),
                    ("Complemento", "complemento", end.complemento),
                    ("Bairro", "bairro", end.bairro),
                    ("Cidade", "cidade", end.cidade),
                    ("UF", "uf", end.uf),
                    ("Cidade IBGE", "cidade_ibge", end.cidade_ibge)
                ]
                for rot, col, val in campos_end:
                    n = input(f"   🏠 {rot} [{val}]: ").strip()
                    if n:
                        v = int(n) if col == "cidade_ibge" else n.upper()
                        self.repo.atualizar_campo_dinamico("entidade_enderecos", col, v, end.id)

        # --- 4. TABELA: entidade_contatos (TODOS OS CAMPOS) ---
        if ent.contatos:
            print("\n" + "─" * 40 + "\n📞 EDITANDO CONTATOS\n" + "─" * 40)
            for con in ent.contatos:
                print(f"\nID Contato: {con.id}")
                campos_con = [
                    ("Tipo (CELULAR/FIXO/WHATSAPP)", "tipo", con.tipo),
                    ("Referência/Nome", "nome_contato", con.nome_contato),
                    ("Número", "numero", con.numero)
                ]
                for rot, col, val in campos_con:
                    n = input(f"   📞 {rot} [{val}]: ").strip()
                    if n:
                        self.repo.atualizar_campo_dinamico("entidade_contatos", col, n.upper(), con.id)

        # --- 5. TABELA: socios (TODOS OS CAMPOS + SNAPSHOT) ---
        if ent.socios:
            print("\n" + "─" * 40 + "\n👥 EDITANDO QUADRO SOCIETÁRIO\n" + "─" * 40)
            for soc in ent.socios:
                print(f"\nID Vínculo: {soc.id}")
                campos_soc = [
                    ("Participação %", "percentual_participacao", soc.participacao),
                    ("Cargo", "cargo", soc.cargo),
                    ("Data Entrada (AAAA-MM-DD)", "data_entrada", soc.data_entrada),
                    ("Data Saída (AAAA-MM-DD)", "data_saida", soc.data_saida),
                    ("Nome Snapshot", "nome_snapshot", soc.nome_snapshot)
                ]
                for rot, col, val in campos_soc:
                    n = input(f"   👥 {rot} [{val}]: ").strip()
                    if n:
                        v = float(n.replace(',', '.')) if col == "percentual_participacao" else n.upper()
                        self.repo.atualizar_campo_dinamico("socios", col, v, soc.id)

        print("\n✅ ALTERAÇÃO MESTRE FINALIZADA COM SUCESSO!")
        input("[Enter para retornar]")

    def converter_data_br_para_iso(self, data_br: str) -> str:
        """Converte DD/MM/AAAA para AAAA-MM-DD"""
        try:
            if not data_br:
                return datetime.now().strftime("%Y-%m-%d")
            # Converte o padrão brasileiro para objeto datetime e depois para string ISO
            return datetime.strptime(data_br, "%d/%m/%y").strftime("%Y-%m-%d") if len(data_br) == 8 \
                else datetime.strptime(data_br, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            print("⚠️ Data inválida! Usando data de hoje como padrão.")
            return datetime.now().strftime("%Y-%m-%d")