from models.entidade import Entidade
from models.socio import Socio
from datetime import datetime
import re


class EntidadeService:
    def __init__(self, entidade_repo):
        self.repo = entidade_repo

    def validar_data(self, data_str):
        """Valida se a data está no formato SQL AAAA-MM-DD"""
        if not data_str: return None
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", data_str))

    def exibir_menu(self) -> None:
        """Menu Completo de Gestão de Entidades"""
        while True:
            print("\n" + "═" * 45)
            print(f"{'👥 SISTEMA DE GESTÃO DE ENTIDADES':^45}")
            print("═" * 45)
            print("1. 📝 Cadastrar Nova Entidade (PF/PJ)")
            print("2. 📋 Listar Todos os Clientes")
            print("3. 🔍 Consultar um Cliente (Detalhado)")
            print("4. 🚪 Registrar Saída de Sócio")
            print("5. 🛠️  Alterar 1 Campo Específico")
            print("6. 🔎 Revisão Geral (Campo a Campo)")
            print("0. ⬅️  Voltar ao Menu Principal")

            opcao = input("\nEscolha uma opção: ")

            if opcao == "1":
                self.cadastrar_entidade()
            elif opcao == "2":
                self.exibir_clientes_com_socios()
                self.listar_todas()
            elif opcao == "3":
                self.consultar_detalhes()
            elif opcao == "4":
                self.registrar_saida_socio()
            elif opcao == "5":
                self.alterar_campo_unico()
            elif opcao == "6":
                self.revisao_geral()
            elif opcao == "0":
                break
            else:
                print("⚠️ Opção inválida!")

    def cadastrar_entidade(self):
        """Cadastro completo com fluxo obrigatório de sócios para PJ"""
        print("\n" + "─" * 55)
        print(f"{'🆕 NOVO CADASTRO DE CLIENTE':^55}")
        print("─" * 55)

        tipo = input("Tipo (PF/PJ): ").upper().strip()
        if tipo not in ['PF', 'PJ']:
            print("❌ Erro: Tipo inválido.");
            return

        documento = input("CPF/CNPJ (Somente números): ").strip()
        if self.repo.buscar_por_cpf(documento):
            print(f"⚠️ Erro: Documento {documento} já cadastrado!");
            return

        nome_fantasia = input("Nome Fantasia / Nome Completo: ").strip()
        razao_social = input("Razão Social (Enter se igual): ").strip() or nome_fantasia
        inscricao_estadual = input("Inscrição estadual: ").strip()
        inscricao_municipal = input("Inscrição municipal(Se não tiver, não preencher): ").strip()
        email = input("E-mail: ").strip()
        telefone = input("Telefone: ").strip()

        print("\n📍 Endereço:")
        cep = input("  CEP: ").strip()
        endereco = input("  Logradouro: ").strip()
        numero = input("  Número: ").strip()
        complemento = input("  Complemento: ").strip()
        bairro = input("  Bairro: ").strip()
        cidade = input("  Cidade: ").strip()
        uf = input("  UF: ").upper().strip()

        print("\n🎭 Papéis (S para Sim / Enter para Não):")
        eh_cli = input("  É Cliente? ").upper() == 'S'
        eh_for = input("  É Fornecedor? ").upper() == 'S'
        eh_tra = input("  É Transportadora? ").upper() == 'S'

        obs = input("\n📝 Observações: ").strip()

        entidade = Entidade(
            tipo_pessoa=tipo,
            nome_fantasia=nome_fantasia,
            razao_social=razao_social,
            documento=documento,
            inscricao_estadual=inscricao_estadual,
            inscricao_municipal=inscricao_municipal,
            email=email,
            telefone=telefone,
            cep=cep,
            endereco=endereco,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            uf=uf,
            eh_cliente=eh_cli or True,
            eh_fornecedor=eh_for,
            eh_transportadora=eh_tra,
            observacoes=obs,
            data_cadastramento=datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        if tipo == 'PJ':
            print("\n🛡️ EMPRESA PJ: O cadastro de sócios é OBRIGATÓRIO.")
            self.fluxo_obrigatorio_socios(entidade)

        try:
            self.repo.salvar(entidade)
            print(f"\n✅ SUCESSO: '{nome_fantasia}' cadastrado!")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

    def fluxo_obrigatorio_socios(self, entidade_pj: Entidade):
        """Busca sócio ou cadastra um novo 'na hora' como PF"""
        while True:
            print("\n🔗 VINCULANDO SÓCIO")
            doc_socio = input("🔍 CPF do Sócio (ou 'F' para finalizar): ").strip()

            if doc_socio.upper() == 'F':
                if not entidade_pj.socios:
                    print("⚠️ PJs devem ter ao menos um sócio vinculado!")
                    continue
                break

            socio_existente = self.repo.buscar_por_cpf(doc_socio)

            if socio_existente:
                print(f"✅ Sócio localizado: {socio_existente.nome_fantasia}")
                id_socio = socio_existente.id
                nome_socio = socio_existente.nome_fantasia
            else:
                print("✨ Sócio não cadastrado. Iniciando Cadastro Expresso PF...")
                nome_novo = input("   Nome Completo do Sócio: ").strip()
                nova_pf = Entidade(
                    tipo_pessoa='PF', nome_fantasia=nome_novo, documento=doc_socio,
                    eh_cliente=True, data_cadastramento=datetime.now().strftime("%Y-%m-%d")
                )
                id_socio = self.repo.salvar(nova_pf)
                nome_socio = nome_novo

            try:
                part = float(input(f"📊 % Participação de {nome_socio}: ").replace(',', '.'))
                hoje_sql = datetime.now().strftime("%Y-%m-%d")

                while True:
                    d_entrada = input(f"📅 Data Entrada (AAAA-MM-DD) [Enter para {hoje_sql}]: ").strip() or hoje_sql
                    if self.validar_data(d_entrada): break
                    print("❌ Formato inválido! Use AAAA-MM-DD.")

                while True:
                    d_saida = input("📅 Data Saída (AAAA-MM-DD) [Enter se ativo]: ").strip() or None
                    if not d_saida or self.validar_data(d_saida): break
                    print("❌ Formato inválido! Use AAAA-MM-DD.")

                cargo = input("💼 Cargo: ").strip() or "Sócio"

                entidade_pj.adicionar_socio(Socio(
                    socio_entidade_id=id_socio, participacao=part,
                    data_entrada=d_entrada, data_saida=d_saida,
                    cargo=cargo, nome_snapshot=nome_socio
                ))
                print(f"➕ Sócio {nome_socio} vinculado!")
            except ValueError:
                print("❌ Erro nos valores. Tente novamente.")

    def listar_todas(self):
        lista = self.repo.buscar_flexivel("")
        print(f"\n{'ID':<4} | {'NOME':<30} | {'DOC':<15} | {'TIPO'}")
        print("-" * 60)
        for e in lista:
            print(f"{e.id:<4} | {e.nome_fantasia[:30]:<30} | {e.documento:<15} | {e.tipo_pessoa}")
        input("\n[Enter] para voltar...")

    def consultar_detalhes(self):
        termo = input("\n🔎 ID ou Documento da Entidade: ")
        ent = self.repo.buscar_por_id_ou_documento(termo)
        if not ent:
            print("❌ Não encontrado.");
            return

        print("\n" + "═" * 65)
        print(f"👤 {ent.nome_fantasia.upper()} ({ent.tipo_pessoa})")
        print(f"📄 Doc: {ent.documento} | 📞 {ent.telefone}")

        # MOSTRAR SÓCIOS (Se for PJ)
        if ent.tipo_pessoa == 'PJ' and ent.socios:
            print("-" * 65)
            print(f"{'QUADRO SOCIETÁRIO (Quem manda aqui)':^65}")
            for s in ent.socios:
                status = "Ativo" if not s.data_saida else f"Saiu em {s.data_saida}"
                print(f"   • {s.nome_snapshot[:25]:<25} | {s.cargo} ({s.participacao}%) | {status}")

        # MOSTRAR ONDE É SÓCIO (Se for PF)
        if ent.tipo_pessoa == 'PF' and hasattr(ent, 'participacoes_societarias') and ent.participacoes_societarias:
            print("-" * 65)
            print(f"{'PARTICIPAÇÕES EM EMPRESAS (Onde esta PF investe)':^65}")
            for p in ent.participacoes_societarias:
                status = "Ativo" if not p['data_saida'] else f"Ex-sócio"
                print(f"   • Empresa: {p['nome_empresa']:<20} | Cargo: {p['cargo']} | {status}")

        print("═" * 65)
        input("\n[Enter] para voltar...")



    def registrar_saida_socio(self):
        id_empresa = input("\n🏢 ID da Empresa (PJ): ")
        empresa = self.repo.buscar_por_id(id_empresa)
        if not empresa or not empresa.socios:
            print("❌ Empresa sem sócios ativos.");
            return

        for s in empresa.socios:
            if not s.data_saida:
                print(f"ID Vínculo: {s.id} | Sócio: {s.nome_snapshot}")

        id_vinculo = input("\n👉 ID Vínculo do sócio que está saindo: ")
        while True:
            data_saida = input("📅 Data de Saída (AAAA-MM-DD): ").strip()
            if self.validar_data(data_saida): break
            print("❌ Formato inválido! Use AAAA-MM-DD.")

        self.repo.encerrar_sociedade(id_vinculo, data_saida)
        print("✅ Saída registrada com sucesso!")

    def alterar_campo_unico(self):
        termo = input("\n🛠️  ID ou Documento da Entidade: ")
        ent = self.repo.buscar_por_id_ou_documento(termo)
        if not ent:
            print("❌ Entidade não localizada.");
            return

        print("\nCampos: 1.Nome, 2.Email, 3.Telefone, 4.Endereco, 5.Obs")
        op = input("Qual deseja alterar? ")
        mapa = {"1": "nome_fantasia", "2": "email", "3": "telefone", "4": "endereco", "5": "observacoes"}

        if op in mapa:
            novo_valor = input(f"Novo valor para {mapa[op]}: ").strip()
            self.repo.atualizar_campo_dinamico(ent.id, mapa[op], novo_valor)
            print("✅ Campo atualizado!")

    def revisao_geral(self):
        """Restauração da função original de revisão campo a campo"""
        termo = input("\n🔎 ID ou Documento para Revisão Geral: ")
        ent = self.repo.buscar_por_id_ou_documento(termo)
        if not ent:
            print("❌ Entidade não localizada.");
            return

        print("\n--- 🔎 REVISÃO DE DADOS (Enter para manter atual) ---")

        # Lista de campos para revisão: (Nome amigável, Nome no banco, Valor atual)
        campos = [
            ("Nome Fantasia", "nome_fantasia", ent.nome_fantasia),
            ("Razão Social", "razao_social", ent.razao_social),
            ("Inscrição estadual", "inscricao_estadual", ent.inscricao_estadual),
            ("Inscrição municipal", "inscricao_municipal", ent.inscricao_municipal),
            ("E-mail", "email", ent.email),
            ("Telefone", "telefone", ent.telefone),
            ("CEP", "cep", ent.cep),
            ("Endereço", "endereco", ent.endereco),
            ("Número", "numero", ent.numero),
            ("Complemento", "complemento", ent.complemento),
            ("Bairro", "bairro", ent.bairro),
            ("Cidade", "cidade", ent.cidade),
            ("UF", "uf", ent.uf),
            ("Observações", "observacoes", ent.observacoes)
        ]

        for rotulo, coluna, valor_atual in campos:
            novo = input(f"{rotulo} [{valor_atual}]: ").strip()
            if novo:
                self.repo.atualizar_campo_dinamico(ent.id, coluna, novo)
                print(f"✅ {rotulo} alterado.")

        print("\n✅ Revisão geral concluída!")
        input("[Enter] para continuar...")


    def exibir_clientes_com_socios(self):
        # Agora buscar_clientes() retorna uma lista de OBJETOS Entidade
        clientes = self.repo.buscar_clientes()

        if not clientes:
            print("⚠️ Nenhum cliente encontrado no banco.")
            return

        print("\n" + "═" * 95)
        print(f"{'👥 RELAÇÃO GERAL DE CLIENTES E VÍNCULOS':^95}")
        print("═" * 95)
        print(f"{'ID':<4} | {'NOME / RAZÃO SOCIAL':<35} | {'DOCUMENTO':<15} | {'TIPO'}")
        print("─" * 95)

        for c in clientes:
            # Como 'c' é um objeto, usamos o ponto (.)
            print(f"{c.id:03}  | {c.nome_fantasia[:35]:<35} | {c.documento:<15} | {c.tipo_pessoa} ")

            # LADO A: Se for Empresa (PJ), mostra quem são os sócios dela
            if c.tipo_pessoa == 'PJ':
                if c.socios:
                    for s in c.socios:
                        print(f"     └─ [Quadro societário] {s.cargo}: {s.nome_snapshot}  Participação=> {s.participacao} %")
                else:
                    print("     └─ (Nenhum sócio vinculado)")

            # LADO B: Se for Pessoa (PF), mostra de quais empresas ela é sócia
            elif c.tipo_pessoa == 'PF':
                # Verificamos o atributo que criamos no buscar_por_id
                participacoes = getattr(c, 'participacoes_societarias', [])
                if participacoes:
                    for p in participacoes:
                        print(f"     └─ [É Sócio na Empresa] {p['nome_empresa']} ({p['cargo']}) | Participação: {p['percentual_participacao']}% ")
                else:
                    print("     └─ [Pessoa Física sem participações]")

            print("─" * 95)