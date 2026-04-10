# ProjSistDristribuidos
## 📡 Sistema de Troca de Mensagens Instantâneas

## 🧠 Introdução
Este projeto tem como objetivo desenvolver um sistema simples de troca de mensagens instantâneas inspirado em BBS e IRC, utilizando conceitos de sistemas distribuídos.

A aplicação permite que clientes (bots) se conectem a um servidor, criem canais públicos e troquem mensagens entre si. Toda a comunicação é feita por meio do ZeroMQ e executada em um ambiente com containers.

O sistema foi desenvolvido sem interação manual, onde os próprios clientes realizam ações automaticamente, como login, criação de canais e envio de mensagens.

## ⚙️ Escolhas do Projeto

### 🔹 Linguagem
O projeto foi desenvolvido em Python para o servidor e broker, e Java para o cliente, escolhidos pela simplicidade e rapidez no desenvolvimento de aplicações distribuídas. A segunda linguagem (Java) foi introduzida a partir da Parte 2.

### 🔹 Comunicação
Foi utilizado o ZeroMQ para a troca de mensagens entre cliente e servidor, utilizando dois padrões:
- **REQ/REP** via broker (portas 5555/5556): para requisições estruturadas entre cliente e servidor, como login, criação de canais e publicação de mensagens.
- **PUB/SUB** via proxy XSUB/XPUB (portas 5557/5558): para distribuição de mensagens nos canais em tempo real, permitindo que múltiplos clientes recebam mensagens simultaneamente.

### 🔹 Serialização
A serialização das mensagens foi feita com Protocol Buffers (protobuf), permitindo uma comunicação eficiente e padronizada entre os serviços. As mensagens incluem timestamps de envio e recebimento tanto nas requisições quanto nas respostas.

### 🔹 Persistência
As publicações realizadas nos canais são persistidas em disco no arquivo `publicacoes.jsonl`, garantindo que todas as mensagens possam ser recuperadas posteriormente. Os canais criados são armazenados em `canais.json`, compartilhado entre as réplicas do servidor via volume Docker.

### 🔹 Funcionamento dos Bots
Ao se conectar, cada bot automaticamente:
1. Verifica se existem menos de 5 canais e cria novos até atingir esse limite
2. Se inscreve em até 3 canais aleatórios via PUB/SUB
3. Entra em loop infinito escolhendo um canal aleatório e enviando 10 mensagens com intervalo de 1 segundo entre cada uma

## 🚀 Considerações Finais
O projeto atende aos requisitos propostos, utilizando comunicação distribuída, execução automatizada via bots e estrutura preparada para expansão futura. O ambiente é totalmente containerizado via Docker Compose, com múltiplas réplicas de servidor e cliente rodando simultaneamente e compartilhando estado via volume persistente.