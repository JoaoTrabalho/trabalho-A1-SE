# Para compatibilidade do código com a versão mais atual do Python
import collections
import collections.abc

collections.Mapping = collections.abc.Mapping

from experta import *


# Valida entrada abstrata
def valid(entrada):
    if entrada == "sim" or entrada == "nao":
        return entrada
    elif entrada == "s":
        return "sim"
    elif entrada == "n":
        return "nao"


# 1. Fato base
class StatusRede(Fact):
    """Armazena as informações e sintomas da rede do usuário"""

    pass


# 2. Motor de Inferência
class DiagnosticoRede(KnowledgeEngine):

    @DefFacts()
    def inicio(self):
        # Ponto de partida
        yield StatusRede(problema="sem_internet")

    # 1: REGRAS DE PERGUNTAS

    # Pergunta 1: Só pergunta do cabo se o problema for "sem_internet" e ainda não soubermos do cabo
    @Rule(StatusRede(problema="sem_internet"), NOT(StatusRede(cabo_conectado=W())))
    def perguntar_cabo(self):
        resp = (
            input("1. O cabo de rede (ou Wi-Fi) está conectado? (sim/nao): ")
            .strip()
            .lower()
        )
        self.declare(StatusRede(cabo_conectado=valid(resp)))

    # Pergunta 2: Só pergunta do IP se soubermos que o cabo está conectado, mas não soubermos do IP
    @Rule(StatusRede(cabo_conectado="sim"), NOT(StatusRede(ip_valido=W())))
    def perguntar_ip(self):
        resp = (
            input("2. O IP da máquina é válido (diferente de 169.254.x.x)? (sim/nao): ")
            .strip()
            .lower()
        )
        self.declare(StatusRede(ip_valido=valid(resp)))

    # Pergunta 3: Só pergunta do ping do roteador se o IP for válido
    @Rule(StatusRede(ip_valido="sim"), NOT(StatusRede(ping_roteador=W())))
    def perguntar_ping_rot(self):
        resp = (
            input("3. O comando de ping para o roteador funciona? (sim/nao): ")
            .strip()
            .lower()
        )
        self.declare(StatusRede(ping_roteador=valid(resp)))

    # Pergunta 4: Só pergunta do ping externo se o ping do roteador funcionou
    @Rule(StatusRede(ping_roteador="sim"), NOT(StatusRede(ping_google=W())))
    def perguntar_ping_ext(self):
        resp = (
            input("4. O comando de ping para o Google (8.8.8.8) funciona? (sim/nao): ")
            .strip()
            .lower()
        )
        self.declare(StatusRede(ping_google=valid(resp)))

    # 2: DIAGNÓSTICO

    @Rule(StatusRede(cabo_conectado="nao"))
    def falha_fisica(self):
        print(
            "\n[DIAGNÓSTICO FINAL]: O problema é físico. Conecte o cabo de rede ou ative o adaptador Wi-Fi."
        )

    @Rule(StatusRede(cabo_conectado="sim"), StatusRede(ip_valido="nao"))
    def falha_dhcp(self):
        print(
            "\n[DIAGNÓSTICO FINAL]: Falha de DHCP. Seu computador não recebeu um IP válido do roteador. Tente reiniciar o roteador."
        )

    @Rule(StatusRede(ip_valido="sim"), StatusRede(ping_roteador="nao"))
    def falha_gateway(self):
        print(
            "\n[DIAGNÓSTICO FINAL]: Sem comunicação com o Gateway. Você está na rede, mas não alcança o roteador. Verifique as configurações de firewall ou IP estático."
        )

    @Rule(StatusRede(ping_roteador="sim"), StatusRede(ping_google="nao"))
    def falha_dns_ou_provedor(self):
        print(
            "\n[DIAGNÓSTICO FINAL]: O roteador está acessível, mas não há saída para a internet. Pode ser falha no servidor DNS ou problema no provedor (ISP)."
        )

    @Rule(StatusRede(ping_google="sim"))
    def rede_ok(self):
        print(
            "\n[DIAGNÓSTICO FINAL]: A rede base está funcionando perfeitamente. O problema deve ser no seu navegador ou o site específico está fora do ar."
        )


# 3. Execução do Sistema
if __name__ == "__main__":
    print("=== Sistema Especialista: Diagnóstico de Rede ===")
    print("Responda às perguntas com 'sim' ou 'nao'.\n")

    motor = DiagnosticoRede()
    motor.reset()  # Prepara a engine
    motor.run()
