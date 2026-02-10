from models.dados_emissor import DadosEmissor
from datetime import datetime


class EmissorService:
    def __init__(self, emissor_repo):
        self.repo = emissor_repo

    def exibir_menu(self) -> None:
        """Menu de Configuração do Emitente (Sua Empresa)"""
        while True:
            print("\n" + "═" * 45)
            print(f"{'⚙️ CONFIGURAÇÕES DO EMISSOR':^45}")
            print("═" * 45)
            print("1. 📝 Configurar/Alterar Dados da Empresa")
            print("2. 🔍 Visualizar Dados Atuais")
            print("0. ⬅️  Voltar ao Menu Principal")

            opcao = input("\nEscolha uma opção: ")

            if opcao == "1":
                self.configurar_dados()
            elif opcao == "2":
                self.visualizar_dados()
            elif opcao == "0":
                break
            else:
                print("⚠️ Opção inválida!")

    def configurar_dados(self):
        """Fluxo de entrada de dados para o emissor (ID Fixo 1)"""
        print("\n" + "─" * 55)
        print(f"{'📝 CADASTRO DOS DADOS FISCAIS':^55}")
        print("─" * 55)

        # Busca dados atuais para sugerir no input (estilo revisão)
        atual = self.repo.buscar()

        razao = input(f"Razão Social [{atual.razao_social if atual else ''}]: ").strip() or (
            atual.razao_social if atual else "")
        fantasia = input(f"Nome Fantasia [{atual.nome_fantasia if atual else ''}]: ").strip() or (
            atual.nome_fantasia if atual else "")
        cnpj = input(f"CNPJ (Somente números) [{atual.cnpj if atual else ''}]: ").strip() or (
            atual.cnpj if atual else "")
        ie = input(f"Inscrição Estadual [{atual.inscricao_estadual if atual else ''}]: ").strip() or (
            atual.inscricao_estadual if atual else "")

        print("\n📍 Endereço Fiscal:")
        email = input(f"E-mail: [{atual.email if atual else ''}]: ").strip() or (atual.email if atual else "")
        tel = input(f"Telefone: [{atual.telefone if atual else ''}]: ").strip() or (atual.telefone if atual else "")
        cep = input(f"CEP: [{atual.cep if atual else ''}]: ").strip() or (atual.cep if atual else "")
        end = input(f"Logradouro: [{atual.endereco if atual else ''}]: ").strip() or (atual.endereco if atual else "")
        num = input(f"Número: [{atual.numero if atual else ''}]: ").strip() or (atual.numero if atual else "")
        bairro = input(f"Bairro: [{atual.bairro if atual else ''}]: ").strip() or (atual.bairro if atual else "")
        cid = input(f"Cidade: [{atual.cidade if atual else ''}]: ").strip() or (atual.cidade if atual else "")
        uf = input(f"UF: [{atual.uf if atual else ''}]: ").upper().strip() or (atual.uf if atual else "")

        print("\n⚖️ Dados Tributários:")
        ibge = input(f"Cód. IBGE Município [{atual.ibge_municipio if atual else ''}]: ").strip() or (
            atual.ibge_municipio if atual else "")
        regime = input(f"Regime (1)MEI 2)SIMPLES 3)Lucro Presumido 4)Lucro Real) [{atual.regime_tributario if atual else ''}]: ").strip() or (
            atual.regime_tributario if atual else "")

        emissor = DadosEmissor(
            razao_social=razao, nome_fantasia=fantasia, cnpj=cnpj,
            inscricao_estadual=ie, email=email, telefone=tel, cep=cep,
            endereco=end, numero=num, bairro=bairro, cidade=cid, uf=uf,
            ibge_municipio=int(ibge), regime_tributario=int(regime)
        )

        try:
            self.repo.salvar(emissor)
            print(f"\n✅ SUCESSO: Dados da empresa '{razao}' atualizados!")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

    def visualizar_dados(self):
        ent = self.repo.buscar()
        if not ent:
            print("⚠️ Emissor não configurado.")
            return

        print("\n" + "═" * 65)
        print(f"🏢 {ent.razao_social.upper()}")
        print(f"📄 CNPJ: {ent.cnpj} | IE: {ent.inscricao_estadual}")
        print(f"📍 {ent.endereco}, {ent.numero} - {ent.cidade}/{ent.uf}")
        print(f"⚖️ Regime: {'Simples Nacional' if ent.regime_tributario == 1 else 'Regime Normal'}")
        print("═" * 65)
        input("\n[Enter] para voltar...")