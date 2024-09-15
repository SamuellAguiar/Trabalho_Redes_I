import http.client
import json
import os
import socket
import time

# Envia uma mensagem para a API do Copilot e retorna a resposta formatada
def copilot(message):
    conn = http.client.HTTPSConnection("copilot5.p.rapidapi.com")
    payload = json.dumps({
        "message": f"{message} - Responda de forma curta, direta e sem informações adicionais. Não use emojis. Não use ponto final no final da frase.",
        "conversation_id": None,
        "tone": "BALANCED",
        "markdown": False,
        "photo_url": None
    })

    headers = {
        'x-rapidapi-key': "c97156f4damsh195378e236f4ffep1f6d3ejsn7d5a7de48b61",  # Insira sua chave da API
        'x-rapidapi-host': "copilot5.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    conn.request("POST", "/copilot", payload, headers)
    resposta = conn.getresponse()
    data = resposta.read()

    # Decodifica e extrai a resposta da API
    resposta_json = json.loads(data.decode("utf-8"))
    if "data" in resposta_json and "message" in resposta_json["data"]:
        return resposta_json["data"]["message"], "IA"
    else:
        print("Erro: Resposta inválida da API.")
        return None, "Erro"

# Função para obter resposta do humano
def obter_resposta_usuario():
    resposta = input("Digite a resposta: ")
    return resposta, "Humano"

# Salva os dados do histórico e ranking em arquivos JSON
def salvar_dados(nome_usuario, historico, ranking):
    # Carrega o histórico dos usuários ou cria um novo dicionário se o arquivo não existir
    try:
        with open("historico.json", "r") as f_hist:
            historico_json = json.load(f_hist)
    except FileNotFoundError:
        historico_json = {}

    # Atualiza o histórico_json do usuário com formatação mais legível
    historico_json[nome_usuario] = [
        {
            "pergunta": item[0],
            "resposta": item[1],
            "origem": item[2],
            "acertou": item[3]
        }
        for item in historico[nome_usuario]
    ]

    with open("historico.json", "w", encoding='utf-8') as f_hist:
        json.dump(historico_json, f_hist, indent=4, ensure_ascii=False)

    # Carrega o ranking dos usuários ou cria um novo dicionário se o arquivo não existir
    try:
        with open("ranking.json", "r") as f_rank:
            ranking_json = json.load(f_rank)
    except FileNotFoundError:
        ranking_json = {}

    # Calcula o percentual de acertos do usuário
    total_perguntas = len(historico[nome_usuario])
    porcentagem_acertos = (ranking[nome_usuario] / total_perguntas) * 100

    # Atualiza o ranking com o novo usuário
    ranking_json[nome_usuario] = {
        "acertos": ranking[nome_usuario],
        "porcentagem": porcentagem_acertos,
    }

    # Ordena o ranking por porcentagem de acertos
    ranking_json_ordenado = dict(sorted(ranking_json.items(), key=lambda item: item[1]["porcentagem"], reverse=True))
    with open("ranking.json", "w", encoding='utf-8') as f_rank:
        json.dump(ranking_json_ordenado, f_rank, indent=4, ensure_ascii=False)

# Carrega o ranking dos usuários
def carregar_ranking():
    ranking = {}
    if os.path.exists("ranking.json"):
        with open("ranking.json", "r") as f:
            try:
                ranking_json = json.load(f)
                for usuario, dados in ranking_json.items():
                    ranking[usuario] = dados.get("porcentagem", 0)
            except json.JSONDecodeError:
                print("Erro ao decodificar o arquivo JSON.")
    return ranking

# Configuração do modo de execução e tempo de espera
modo_execucao = input("Selecione o modo de execução (automático ou controlado): ").lower()
while modo_execucao not in ("automático", "controlado"):
    print("Modo inválido. Digite 'automático' ou 'controlado'.")
    modo_execucao = input("Selecione o modo de execução (automático ou controlado): ").lower()

tempo_espera = float(input("Digite o tempo de espera padrão para a IA (em segundos): "))

historico_perguntas = {}  
ranking_usuarios = carregar_ranking()

# Configurações do servidor
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

        # Inicializa o histórico e o ranking do usuário
        if nome_usuario not in historico_perguntas:
            historico_perguntas[nome_usuario] = []
        if nome_usuario not in ranking_usuarios:
            ranking_usuarios[nome_usuario] = 0

        # Loop principal de comunicação
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode("utf-8")
            print(f"{nome_usuario}: {message}")

            # Define se a resposta será obtida automaticamente pela IA ou pelo humano
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
            
            acertou = conn.recv(1024).decode('utf-8') == "acertou."

            # Armazena a interação no histórico e atualiza o ranking
            historico_perguntas[nome_usuario].append((message, resposta, origem, acertou))

            if acertou:
                ranking_usuarios[nome_usuario] += 1

        # Salva os dados ao finalizar a comunicação
        salvar_dados(nome_usuario, historico_perguntas, ranking_usuarios)