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

### 🔹 Replicação (Parte 5)
O método escolhido para replicação foi a **Replicação Passiva (Primary-Backup)**. Neste modelo, o servidor eleito como coordenador na Parte 4 assume o papel de primário, sendo responsável por propagar as publicações para todos os servidores backup.

O fluxo de replicação funciona da seguinte forma: quando qualquer servidor recebe uma publicação de um cliente, ele salva localmente e em seguida trata a replicação conforme seu papel. Se for o coordenador (primário), ele envia a publicação diretamente para todos os backups via socket REQ/REP dedicado na porta 7100. Se for um backup, ele encaminha a publicação ao coordenador, que por sua vez replica para os demais servidores.

Para isolar o tráfego de replicação do tráfego de atendimento aos clientes, foi criada uma porta exclusiva para comunicação entre servidores (7100), com uma thread dedicada para processar essas requisições em paralelo. O histórico completo de mensagens pode ser consultado via porta 7200, também gerenciada por uma thread separada. Os dados são compartilhados entre as réplicas por meio de um volume Docker persistente, garantindo que todos os servidores tenham acesso ao mesmo estado mesmo após reinicializações.

## 🚀 Considerações Finais
O projeto atende aos requisitos propostos, utilizando comunicação distribuída, execução automatizada via bots e estrutura preparada para expansão futura. O ambiente é totalmente containerizado via Docker Compose, com múltiplas réplicas de servidor e cliente rodando simultaneamente e compartilhando estado via volume persistente.