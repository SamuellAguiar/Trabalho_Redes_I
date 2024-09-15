
# Simulador de Turing

Este projeto foi implementado para o trabalho de Redes de Computadores I. Ele consiste em um chatbot que interage com o usuário, alternando entre respostas geradas por uma IA (utilizando a API do Copilot) e respostas simuladas de um humano.


## Funcionalidades

- **Interação com IA:** Utiliza a API do Copilot para gerar respostas a perguntas do usuário.

- **Simulação de humano:** Permite que o usuário simule respostas de um humano para fins de treinamento.

- **Histórico de conversa:** Armazena o histórico das interações, incluindo perguntas, respostas, origem (IA ou humano) e se o usuário acertou ao identificar a origem.

- **Ranking de usuários:** Calcula a porcentagem de acertos de cada usuário e mantém um ranking ordenado.


## Tecnologias Utilizadas

**Python**


## Estrutura do Projeto

- **server.py**: Contém a lógica principal do servidor, incluindo a interação com a API Copilot, o gerenciamento do histórico e ranking, e a comunicação com os clientes.

- **client.py**: Contém a lógica do cliente, permitindo que o usuário interaja com o chatbot e forneça suas respostas.


## Como Executar

- Garanta que o **Python** esteja configurado na sua máquina.

- **Obtenha uma chave API do Copilot:** Obtenha uma chave do Copilot e troque a chave que está no campo ``x-rapidapi-key`` pela sua chave no arquivo ``server.py``.

- **Primeiro execute o servidor:** Execute o arquivo ``server.py``.

- **Configure suas preferências do servidor:** Responda as perguntas de configuração, como modo automático ou controlado e o tempo de espera da resposta da IA.

- **Execute o cliente:** Depois de executar o server.py, execute o arquivo ``client.py`` para se conectar ao servidor e começar a interação.


## Contato

- gustavo.rolim@aluno.ufop.edu.br

- pamela.miranda@aluno.ufop.edu.br

- samuell.aguiar@aluno.ufop.edu.br
