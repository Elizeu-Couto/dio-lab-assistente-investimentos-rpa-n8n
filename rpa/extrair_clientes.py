"""Script de RPA para extração de clientes e disparo do Webhook no n8n.

Projeto: Assistente de Investimentos com RPA e IA Generativa (DIO)
"""

import requests
from bs4 import BeautifulSoup

URL_PAGINA = "https://digitalinnovationone.github.io/dio-lab-assistente-investimentos-rpa-n8n/"

# URL de produção do Webhook configurado no n8n
N8N_WEBHOOK = "COLE_AQUI_A_PRODUCTION_URL_DO_N8N"


def extrair_clientes(url: str) -> list[dict]:
    """Baixa a página HTML e extrai a lista de clientes da tabela #clientes."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar a página de clientes: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    linhas = soup.select("#clientes tbody tr")

    clientes = []
    for linha in linhas:
        colunas = linha.find_all("td")
        if len(colunas) >= 4:
            cliente = {
                "nome": colunas[0].get_text(strip=True),
                "email": colunas[1].get_text(strip=True),
                "saldo": colunas[2].get_text(strip=True),
                "perfil": colunas[3].get_text(strip=True),
            }
            clientes.append(cliente)

    return clientes


def enviar_para_n8n(webhook_url: str, clientes: list[dict]) -> None:
    """Envia a lista de clientes em formato JSON para o Webhook do n8n."""
    if not clientes:
        print("Nenhum cliente disponível para envio.")
        return

    payload = {"clientes": clientes}
    print(f"\nIniciando envio de {len(clientes)} clientes para o Webhook do n8n...")
    print(f"Destino: {webhook_url}")

    if webhook_url == "COLE_AQUI_A_PRODUCTION_URL_DO_N8N":
        print("[ALERTA] Substitua a variável N8N_WEBHOOK pela Production URL gerada no seu nó Webhook do n8n.")

    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Resposta do n8n: {response.text}")

        if response.status_code == 200:
            print("Sucesso: Dados recebidos e aceitos pelo workflow do n8n!")
        else:
            print(f"Atenção: O webhook retornou código HTTP {response.status_code}. Verifique a aba Executions no n8n.")

    except requests.exceptions.Timeout:
        print("Erro: A requisição ao Webhook do n8n atingiu o tempo limite de espera (Timeout).")
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição HTTP para o n8n: {e}")


def main():
    print(f"1) Baixando dados da página: {URL_PAGINA}")
    clientes = extrair_clientes(URL_PAGINA)

    print(f"\n2) Clientes encontrados ({len(clientes)} registros):")
    for cliente in clientes:
        print(cliente)

    print("\n3) Enviando dados para o n8n:")
    enviar_para_n8n(N8N_WEBHOOK, clientes)


if __name__ == "__main__":
    main()
