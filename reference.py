import zmq
import time
import threading
import json

context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind("tcp://*:6000")

servidores = {}
proximo_rank = 1

TIMEOUT = 30


def limpar_servidores():
    global servidores
    while True:
        agora = time.time()
        remover = []

        for nome, dados in servidores.items():
            if agora - dados["last_seen"] > TIMEOUT:
                remover.append(nome)

        for nome in remover:
            print(f"[REMOVIDO] Servidor {nome} por inatividade")
            del servidores[nome]

        time.sleep(5)


threading.Thread(target=limpar_servidores, daemon=True).start()


while True:
    mensagem = socket.recv_json()

    tipo = mensagem.get("tipo")

    # ---------------- RANK ----------------
    if tipo == "register":
        nome = mensagem.get("nome")

        if nome not in servidores:
            servidores[nome] = {
                "rank": proximo_rank,
                "last_seen": time.time()
            }
            print(f"[NOVO] {nome} registrado com rank {proximo_rank}")
            proximo_rank += 1

        resposta = {
            "rank": servidores[nome]["rank"]
        }

        socket.send_json(resposta)

    # ---------------- LIST ----------------
    elif tipo == "list":
        lista = []

        for nome, dados in servidores.items():
            lista.append({
                "nome": nome,
                "rank": dados["rank"]
            })

        socket.send_json(lista)

    # ---------------- HEARTBEAT ----------------
    elif tipo == "heartbeat":
        nome = mensagem.get("nome")

        if nome in servidores:
            servidores[nome]["last_seen"] = time.time()

            resposta = {
                "status": "OK",
            }
        else:
            resposta = {
                "status": "NOT_REGISTERED"
            }

        socket.send_json(resposta)

    # ---------------- ERRO ----------------
    else:
        socket.send_json({"erro": "tipo inválido"})