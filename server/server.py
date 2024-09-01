import http.client
import json
import os
import socket
import time

# Realiza a requisão da resposta através da API do Copilot
def copilot(message):
    conn = http.client.HTTPSConnection("copilot5.p.rapidapi.com")

    # Cria o payload com a mensagem (prompt)
    payload = json.dumps({
        "message": message + "- Responda de forma curta, direta e sem informações adicionais. Não use emojis. Use palavras que são normalmente usadas no dia a dia.",
        "conversation_id": None,
        "tone": "BALANCED",
        "markdown": False,
        "photo_url": None
    })

    headers = {
        'x-rapidapi-key': "4cde18aa1bmshd34591a77eb65fdp199e81jsn0cb7634422b2",  # Insira sua chave de API
        'x-rapidapi-host': "copilot5.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    conn.request("POST", "/copilot", payload, headers)

    
    resposta = conn.getresponse()
    data = resposta.read()

    resposta_json = json.loads(data.decode("utf-8"))
    if "data" in resposta_json and "message" in resposta_json["data"]:
        return resposta_json["data"]["message"], "IA"
    else:
        print("Erro: A resposta não contém a chave 'message' ou 'data'.")

def obter_resposta_usuario():
    resposta = input("Digite a resposta: ")
    return resposta, "Humano"

def salvar_dados(nome_usuario, historico, ranking):
    with open("historico.txt", "a", encoding='utf-8') as f_hist, open("ranking.txt", "w", encoding='utf-8') as f_rank:
        for usuario, perguntas in historico.items():
            contagem_ia = 0
            contagem_humano = 0
            contagem_acertos = 0
            for pergunta, resposta, origem, acertou in perguntas:
                f_hist.write(f"Cliente: {usuario} | Pergunta: {pergunta} | Resposta: {resposta} | Origem: {origem} | Acertou? {acertou}\n")
                if origem == "IA":
                    contagem_ia += 1
                else:
                    contagem_humano += 1
                if acertou:
                    contagem_acertos += 1
            f_hist.write(f"{usuario} - Estatísticas: IA = {contagem_ia}, Humano = {contagem_humano}, Acertos = {contagem_acertos}\n")
        for usuario, acertos in ranking.items():
            total_perguntas = len(historico.get(usuario, []))
            percentual = (acertos / total_perguntas) * 100 if total_perguntas > 0 else 0
            f_rank.write(f"Cliente: {usuario} |{percentual:.2f}%\n")


def carregar_ranking():
    ranking = {}
    if os.path.exists("ranking.txt"):
        with open("ranking.txt", "r") as f:
            for linha in f:
                partes = linha.strip().split("|") 
                usuario = partes[0].split(":")[1].strip()  # Extrai o usuário
                percentual = float(partes[1].strip()[:-1])  # Extrai o percentual
                ranking[usuario] = percentual
    return ranking

# Configurações iniciais
modo_execucao = input("Selecione o modo de execução (automático ou controlado): ").lower()
while modo_execucao not in ("automático", "controlado"):
    print("Modo inválido. Digite 'automático' ou 'controlado'.")
    modo_execucao = input("Selecione o modo de execução (automático ou controlado): ").lower()

tempo_espera = input("Digite o tempo de espera padrão para a IA (em segundos): ")
tempo_espera = float(tempo_espera)

historico_perguntas = {}  # Dicionário para armazenar o histórico
ranking_usuarios = carregar_ranking()

HOST = "127.0.0.1"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Servidor iniciado em {HOST}:{PORT}. Aguardando conexão...")
    conn, addr = s.accept()
    with conn:
        nome_usuario = conn.recv(1024).decode('utf-8')
        print(f"{nome_usuario} conectado.")

        if nome_usuario not in historico_perguntas:
            historico_perguntas[nome_usuario] = []
        if nome_usuario not in ranking_usuarios:
            ranking_usuarios[nome_usuario] = 0

        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode("utf-8")
            print(f"{nome_usuario}: {message}")

            if modo_execucao == "automático":
                resposta, origem = copilot(message)
                time.sleep(tempo_espera)
            else:
                opcao = input("Usar resposta da IA (s/n)? ").lower()
                if opcao == "s":
                    resposta, origem = copilot(message)
                    time.sleep(tempo_espera)
                else:
                    resposta, origem = obter_resposta_usuario()

            conn.sendall(f"({origem}) {resposta}".encode("utf-8"))

            # Recebe a resposta do cliente sobre se acertou ou errou
            acertou = conn.recv(1024).decode('utf-8') == "acertou."

            # Armazena a pergunta, resposta, origem e se acertou no histórico
            historico_perguntas[nome_usuario].append((message, resposta, origem, acertou))

            # Atualiza o ranking se o usuário acertou
            if acertou:
                ranking_usuarios[nome_usuario] += 1

        salvar_dados(nome_usuario, historico_perguntas, ranking_usuarios)