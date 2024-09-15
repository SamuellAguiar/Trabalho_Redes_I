import socket

HOST = "127.0.0.1"  # Endereço IP do localhost
PORT = 65432        # Mesma porta usada pelo servidor

def obter_resposta_usuario():
    while True:
        opcao = input("A resposta é de um humano ou de IA (h/ia)? ").lower()
        if opcao in ("h", "ia"):
            return opcao
        print("Opção inválida. Digite 'h' para humano ou 'ia' para IA.")

def main():
    # Interação com o cliente
    nome_usuario = input("Digite seu nome: ")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(nome_usuario.encode("utf-8"))

        while True:
            mensagem = input("Digite a pergunta (ou 'sair' para finalizar): ")
            if mensagem.lower() == 'sair':
                break

            s.sendall(mensagem.encode("utf-8"))
            resposta_completa = s.recv(1024).decode("utf-8")

            origem, resposta = resposta_completa.split(" ", 1)
            origem = origem[1:-1]

            print(f"Servidor: {resposta}")

            opcao_usuario = obter_resposta_usuario()

            if (opcao_usuario == "ia" and origem == "IA") or (opcao_usuario == "h" and origem == "Humano"):
                resultado = "acertou."
            else:
                resultado = "errou."

            print(f"Você {resultado}")
            s.sendall(resultado.encode("utf-8"))

            if input("Deseja fazer outra pergunta (s/n)? ").lower() != "s":
                break

    print("Conexão encerrada.")

if __name__ == "__main__":
    main()
