from models.entidade import Entidade
from models.socio import Socio
from models.entidade_enderecos import Endereco
from models.entidade_contatos import Contato
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
                # self.listar_todas()
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
            print("❌ Erro: Tipo inválido.")
            return

        documento = input("CPF/CNPJ (Somente números): ").strip()

        if self.repo.buscar_por_cpf(documento):
            print(f"⚠️ Erro: Documento {documento} já cadastrado!")
            return

        nome_fantasia = input("Nome Fantasia / Nome Completo: ").strip()
        razao_social = input("Razão Social (Enter se igual): ").strip() or nome_fantasia
        inscricao_estadual = input("Inscrição estadual: ").strip()
        inscricao_municipal = input("Inscrição municipal(Se não tiver, não preencher): ").strip()
        email_comercial = input("E-mail_comercial: ").strip()
        email_nfe = input("E-mail_nfe: ").strip()
        regime_tributario= input("Informe o regime tributário=> A)MEI B)SIMPLES C)Lucro Presumido D)Lucro Real :")
        indicador_ie = input("O cliente é contribuinte ICMS (Escolha o código) 1)Sim 2)Isento 9)Não conbribuinte: ")
        limite_credito = 0

        enderecos_coletados = self.fluxo_coleta_endereco()
        contatos_coletados = self.fluxo_coleta_contato()



        print("\n🎭 Papéis (S para Sim / Enter para Não):")
        eh_cli = input("  É Cliente? ").strip().upper() == 'S'
        eh_for = input("  É Fornecedor? ").strip().upper() == 'S'
        eh_tra = input("  É Transportadora? ").strip().upper() == 'S'
        eh_seg = input("  É Seguradora? ").strip().upper() == 'S'
        obs = input("\n📝 Observações: ").strip()

        entidade = Entidade(
            tipo_pessoa=tipo,
            nome_fantasia=nome_fantasia,
            razao_social=razao_social,
            documento=documento,
            inscricao_estadual=inscricao_estadual,
            inscricao_municipal=inscricao_municipal,
            email_comercial=email_comercial,
            email_nfe=email_nfe,
            regime_tributario=regime_tributario,
            indicador_ie=indicador_ie,
            limite_credito=limite_credito,
            observacoes=obs,
            eh_cliente=eh_cli,  # Agora ele vai respeitar o que você digitou!
            eh_fornecedor=eh_for,
            eh_transportadora=eh_tra,
            eh_seguradora=eh_seg,
            data_cadastramento=datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        # 🟡 <--- INCLUSÃO: Vincula as listas ao objeto para o Repository salvar
        entidade.enderecos = enderecos_coletados
        entidade.contatos = contatos_coletados


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

                # 🟡 NOVO: Coleta endereços e contatos para o SÓCIO também
                ends_socio = self.fluxo_coleta_endereco()
                conts_socio = self.fluxo_coleta_contato()


                nova_pf = Entidade(
                    tipo_pessoa='PF',
                    nome_fantasia=nome_novo,
                    documento=doc_socio,
                    eh_cliente=True,
                    data_cadastramento=datetime.now().strftime("%Y-%m-%d")
                )

                nova_pf.enderecos = ends_socio
                nova_pf.contatos = conts_socio

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
                    socio_entidade_id=id_socio,
                    participacao=part,
                    data_entrada=d_entrada,
                    data_saida=d_saida,
                    cargo=cargo,
                    nome_snapshot=nome_socio
                ))
                print(f"➕ Sócio {nome_socio} vinculado!")
            except ValueError:
                print("❌ Erro nos valores. Tente novamente.")

    def fluxo_coleta_endereco(self):
        lista = []
        if input("\n🏠 Cadastrar endereço? (S/N): ").upper() == 'S':
            tipo = input("   Tipo (PRINCIPAL/COBRANÇA): ").upper() or "PRINCIPAL"
            cep = input("   CEP: ").strip()
            rua = input("   Rua: ").strip()
            num = input("   Número: ").strip()
            comp = input("   Complemento: ").strip() or None
            bairro = input("   Bairro: ").strip()
            cid = input("   Cidade: ").strip()
            uf = input("   UF: ").upper().strip()
            ibge = input("   Código IBGE da Cidade (Opcional): ").strip() or None
            lista.append(Endereco(tipo=tipo, cep=cep, endereco=rua, numero=num, complemento=comp,
                                  bairro=bairro, cidade=cid, uf=uf, cidade_ibge=ibge))
        return lista

    # 🟡 <--- FUNÇÃO NOVA: Coleta de dados de Contato
    def fluxo_coleta_contato(self):
        lista = []
        if input("\n📞 Cadastrar contatos telefônicos? (S/N): ").upper() == 'S':
            while True:
                tipo = input("   Tipo (WHATSAPP/CELULAR/FIXO): ").upper() or "CELULAR"
                num = input("   Número: ").strip()
                nome = input("   Nome do contato: ").strip()
                lista.append(Contato(tipo=tipo, numero=num, nome_contato=nome))
                if input("   Adicionar outro? (S/N): ").upper() != 'S': break
        return lista


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
            print("❌ Registro não encontrado no banco de dados.")
            return

        print("\n" + "═" * 70)
        print(f"👤 {ent.nome_fantasia} ({ent.tipo_pessoa})")
        print("═" * 70)

        # --- BLOCO 1: INFORMAÇÕES BÁSICAS E CONTATO ---
        print(f"🆔 ID: {ent.id:<5} | 📄 Doc: {ent.documento}")
        print(f"🏢 Razão Social: {ent.razao_social}")

        # Usando o helper do Model para pegar o WhatsApp/Celular
        whats = ent.obter_whatsapp() or "Não informado"
        print(f"📧 E-mail: {ent.email_comercial or 'N/A'}")
        print(f"📞 Contato: {whats}")

        # --- BLOCO 2: ENDEREÇO PRINCIPAL ---
        # Chamamos o método na INSTÂNCIA 'ent'
        principal = ent.obter_endereco_principal()
        if principal:
            print(f"🏠 Endereço: {principal.endereco}, {principal.numero}")
            print(f"📍 Bairro: {principal.bairro} - {principal.cidade}/{principal.uf} (CEP: {principal.cep})")
        else:
            print("🏠 Endereço: Nenhum endereço principal cadastrado.")

        # --- BLOCO 3: DADOS TRIBUTÁRIOS ---
        print("-" * 70)
        print(f"📊 Regime: {ent.regime_tributario or 'N/A'} | IE: {ent.inscricao_estadual or 'ISENTO'}")
        print(f"💰 Limite de Crédito: R$ {ent.limite_credito:,.2f}")

        # --- BLOCO 4: QUADRO SOCIETÁRIO (Se PJ) ---
        if ent.tipo_pessoa == 'PJ':
            print("-" * 70)
            if ent.socios:
                print(f"{'👥 QUADRO SOCIETÁRIO':^70}")
                for s in ent.socios:
                    status = "✅ Ativo" if not s.data_saida else f"❌ Saiu em {s.data_saida}"
                    print(f"   • {s.nome_snapshot[:25]:<25} | {s.cargo:<15} | {s.participacao:>5}% | {status}")
            else:
                print("⚠️  Esta empresa não possui sócios vinculados.")

        # --- BLOCO 5: PARTICIPAÇÕES (Se PF) ---
        elif ent.tipo_pessoa == 'PF':
            participacoes = getattr(ent, 'participacoes_societarias', [])
            if participacoes:
                print("-" * 70)
                print(f"{'💼 PARTICIPAÇÕES EM EMPRESAS (INVESTIMENTOS)':^70}")
                for p in participacoes:
                    status = "✅ Ativo" if not p['data_saida'] else "❌ Ex-sócio"
                    print(f"   • Empresa: {p['nome_empresa'][:20]:<20} | Cargo: {p['cargo']:<15} | {status}")

        # --- BLOCO 6: OBSERVAÇÕES ---
        if ent.observacoes:
            print("-" * 70)
            print(f"📝 Observações: {ent.observacoes}")

        print("═" * 70)
        input("\n[Pressione Enter para voltar ao menu]")

    def registrar_saida_socio(self):
        id_empresa = input("\n🏢 ID da Empresa (PJ): ")
        empresa = self.repo.buscar_por_id(id_empresa)
        if not empresa or not empresa.socios:
            print("❌ Empresa sem sócios ativos.")
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
            print("❌ Entidade não localizada.")
            return

        print("\nCampos: 1.Nome, 2.Email_comercial, 3.Obs")
        op = input("Qual deseja alterar? ")
        mapa = {"1": "nome_fantasia", "2": "email_comercial", "3": "observacoes"}

        if op in mapa:
            novo_valor = input(f"Novo valor para {mapa[op]}: ").strip()
            self.repo.atualizar_campo_dinamico(ent.id, mapa[op], novo_valor)
            print("✅ Campo atualizado!")


    def revisao_geral(self):
        termo = input("\n🔎 ID ou Documento para Revisão Geral: ")
        ent = self.repo.buscar_por_id_ou_documento(termo)
        if not ent:
            print("❌ Entidade não localizada.")
            return

        print(f"\n--- 🔎 REVISÃO: {ent.nome_fantasia} (Enter para manter) ---")

        # 1. Campos Básicos (Sua lógica que já funciona)
        campos = [
            ("Nome Fantasia", "nome_fantasia", ent.nome_fantasia),
            ("Razão Social", "razao_social", ent.razao_social),
            ("E-mail Comercial", "email_comercial", ent.email_comercial),
            ("Limite Crédito", "limite_credito", ent.limite_credito),
            ("É Cliente", "eh_cliente", ent.eh_cliente),
            ("É Fornecedor", "eh_fornecedor", ent.eh_fornecedor),
            ("É Transportadora", "eh_transportadora", ent.eh_transportadora),
            ("É Seguradora", "eh_seguradora", ent.eh_seguradora)
        ]

        for rotulo, coluna, valor_atual in campos:
            novo = input(f"{rotulo} [{valor_atual}]: ").strip()
            if novo:
                valor_final = (1 if novo.upper() in ['S', '1', 'SIM'] else 0) if coluna.startswith('eh_') else novo
                self.repo.atualizar_campo_dinamico(ent.id, coluna, valor_final)

        # 🟡 2. REVISÃO DE ENDEREÇOS (Inclusão)
        self.revisar_vinculos_endereco(ent)

        # 🟡 3. REVISÃO DE CONTATOS (Inclusão)
        self.revisar_vinculos_contato(ent)

        print("\n✅ Revisão completa finalizada!")

    def revisar_vinculos_endereco(self, ent):
        print("\n🏠 --- REVISÃO DE ENDEREÇOS ---")
        if ent.enderecos:
            for end in ent.enderecos:
                print(f"📍 Endereço Atual: {end.tipo}")

                # Ordem lógica para futura API: CEP primeiro
                novo_cep = input(f"   CEP [{end.cep}]: ").strip()
                nova_uf = input(f"   UF [{end.uf}]: ").strip().upper()
                nova_cid = input(f"   Cidade [{end.cidade}]: ").strip()
                novo_bai = input(f"   Bairro [{end.bairro}]: ").strip()
                novo_rua = input(f"   Rua [{end.endereco}]: ").strip()
                novo_num = input(f"   Número [{end.numero}]: ").strip()
                novo_com = input(f"   Complemento [{end.complemento}]: ").strip()

                # Se houve qualquer mudança, atualizamos o objeto e o banco
                if any([novo_cep, nova_uf, nova_cid, novo_bai, novo_rua, novo_num, novo_com]):
                    end.cep = novo_cep or end.cep
                    end.uf = nova_uf or end.uf
                    end.cidade = nova_cid or end.cidade
                    end.bairro = novo_bai or end.bairro
                    end.endereco = novo_rua or end.endereco
                    end.numero = novo_num or end.numero
                    end.complemento = novo_com or end.complemento

                    # Chamada ao Repository respeitando a assinatura da função
                    self.repo.atualizar_endereco_id(
                        end.id,  # endereco_id
                        end.endereco,  # logradouro
                        end.numero,  # numero
                        end.complemento,  # complemento
                        end.bairro,  # bairro
                        end.cidade,  # cidade
                        end.uf,  # uf
                        end.cep  # cep
                    )
                    print("   ✅ Alterações gravadas com sucesso!")

    def revisar_vinculos_contato(self, ent):
        print("\n📞 --- REVISÃO DE CONTATOS ---")
        if ent.contatos:
            for cont in ent.contatos:
                novo_num = input(f"   {cont.tipo} - {cont.nome_contato} [{cont.numero}]: ").strip()
                if novo_num:
                    self.repo.atualizar_contato_id(cont.id, novo_num)
                    print("   ✅ Contato atualizado.")
        else:
            # 🟡 Se não existir, oferece para cadastrar agora!
            print("⚠️ Nenhum contato cadastrado para esta entidade.")
            if input("👉 Deseja cadastrar um contato agora? (S/N): ").upper() == 'S':
                novo_cont_lista = self.fluxo_coleta_contato()
                if novo_cont_lista:
                    self.repo.salvar_contatos_vinculados(ent.id, novo_cont_lista)
                    print("✅ Novo contato adicionado com sucesso!")


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