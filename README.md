# ProjSistDristribuidos

# 📡 Sistema de Troca de Mensagens Instantânea

## 🧠 Introdução

Este projeto tem como objetivo desenvolver um sistema simples de troca de mensagens instantâneas inspirado em BBS e IRC, utilizando conceitos de sistemas distribuídos.

A aplicação permite que clientes (bots) se conectem a um servidor, criem canais públicos e troquem mensagens entre si. Toda a comunicação é feita por meio do ZeroMQ e executada em um ambiente com containers.

O sistema foi desenvolvido sem interação manual, onde os próprios clientes realizam ações automaticamente, como login, criação de canais e envio de mensagens.

---

## ⚙️ Escolhas do Projeto

### 🔹 Linguagem

O projeto foi desenvolvido em **Python**, escolhido pela simplicidade e rapidez no desenvolvimento de aplicações distribuídas.
  *importante destacar que a segunda linguagem de programação será implementada a partir da parte2*

---

### 🔹 Comunicação

Foi utilizado o **ZeroMQ** para a troca de mensagens entre cliente e servidor, utilizando o padrão **REQ/REP**, garantindo comunicação estruturada entre as partes.

---

### 🔹 Serialização

A serialização das mensagens foi feita com **Protocol Buffers (protobuf)**, permitindo uma comunicação eficiente e padronizada entre os serviços.

---

### 🔹 Persistência

As mensagens e dados do sistema podem ser armazenados em arquivos locais (ex: `.txt` ou `.json`), garantindo que informações possam ser recuperadas posteriormente.

---

## 🚀 Considerações Finais

O projeto atende aos requisitos propostos, utilizando comunicação distribuída, execução automatizada via bots e estrutura preparada para expansão futura, como suporte a múltiplos servidores e linguagens.
