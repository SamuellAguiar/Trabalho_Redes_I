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
        'x-rapidapi-key': "e4fa60be34msh7261430d1be2e6bp1c99e7jsncfa5de942140",  # Insira sua chave de API
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

# Obtém a resposta do usuário
def obter_resposta_usuario():
    resposta = input("Digite a resposta: ")
    return resposta, "Humano"

# Salva os dados do histórico e ranking em arquivos
def salvar_dados(nome_usuario, historico, ranking):
    #Carrega o histórico dos usuários ou cria um novo dicionário
    try:
        with open("historico.json", "r") as f_rank:
            historico_json = json.load(f_rank)
    except FileNotFoundError:
        historico_json = {}
        
    # Atualiza o histórico_json com o novo histórico do usuário 
    historico_json[nome_usuario] = historico[nome_usuario]
    
    #Salva o historico dos usuários
    with open("historico.json", "w") as f_hist:
        json.dump(historico_json, f_hist, indent=4)
    
    #Carrega o ranking dos usuários ou cria um novo dicionário
    try:
        with open("ranking.json", "r") as f_rank:
            ranking_json = json.load(f_rank)
    except FileNotFoundError:
        ranking_json = {}
    
    #Calcula o percentual de acertos do usuário
    total_perguntas = len(historico[nome_usuario])
    porcentagem_acertos = (ranking[nome_usuario] / total_perguntas) * 100
    
    # Atualiza o ranking_json com o novo usuário e seus dados    
    ranking_json[nome_usuario] = {
        "acertos": ranking[nome_usuario],
        "porcentagem": porcentagem_acertos,
    }
    
    # Salva o ranking_json completo
    with open("ranking.json", "w") as f_rank:
        json.dump(ranking_json, f_rank, indent=4)
    

# Carrega o ranking dos usuários
def carregar_ranking():
    ranking = {}
    if os.path.exists("ranking.json"):
        with open("ranking.json", "r") as f:
            try:
                ranking_json = json.load(f)
                for usuario, dados in ranking_json.items():
                    try:
                        ranking[usuario] = dados["porcentagem"]
                    except KeyError:
                        print(f"Usuário {usuario} não possui a chave 'porcentagem'.")
            except json.JSONDecodeError:
                print("Erro ao decodificar o arquivo JSON.")

    # Ordena o ranking por porcentagem de acertos, do maior para o menor
    ranking_ordenado = dict(sorted(ranking.items(), key=lambda item: item[1], reverse=True))
    return ranking_ordenado

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