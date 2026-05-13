import zmq
import mensagens_pb2
import json
import time
import os
import threading

context = zmq.Context()

socket = context.socket(zmq.REP)
socket.connect("tcp://broker:5556")

pub_socket = context.socket(zmq.PUB)
pub_socket.connect("tcp://pubsub-proxy:5557")

ref_socket = context.socket(zmq.REQ)
ref_socket.connect("tcp://reference:6000")

coordenador = None

SERVER_PORT = int(os.getenv("SERVER_PORT", 7000)) #Pega a variável q eu declarei lá no '.yml' ou usa a padrão 7000

inter_socket = context.socket(zmq.REP)
inter_socket.bind(f"tcp://*:{SERVER_PORT}")

REPL_PORT = SERVER_PORT + 100

repl_socket = context.socket(zmq.REP)
repl_socket.bind(f"tcp://*:{REPL_PORT}")

HIST_PORT = SERVER_PORT + 200

hist_socket = context.socket(zmq.REP)
hist_socket.bind(f"tcp://*:{HIST_PORT}")


usuarios_aceitos = ["Pedro Henrique","Leonardo","João","Matheus"]
usuarios_logados = []
clock = 0
contador_mensagens = 0
#------------referencia------------
nome_servidor = os.getenv("HOSTNAME", "server1")
ref_socket.send_json({
    "tipo": "register",
    "nome": nome_servidor
})
resposta_ref = ref_socket.recv_json()
rank = resposta_ref["rank"]
print(f"Servidor {nome_servidor} com rank {rank}")
#--------------------------------

CANAIS_FILE = "/data/canais.json"
PUBLICACOES_FILE = "/data/publicacoes.jsonl"

def carregar_canais():
    if os.path.exists(CANAIS_FILE):
        with open(CANAIS_FILE, "r") as f:
            return json.load(f)
    return {"Canal1": []}

def salvar_canais(canais):
    with open(CANAIS_FILE, "w") as f:
        json.dump(canais, f)

canais = carregar_canais()
#---------------------------

def salvar_publicacao(data):
    with open(PUBLICACOES_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

#---------------------------
def eleger_coordenador():
    print("Elegendo Coordenador!!!!!!!!!!!")
    global coordenador
    ref_socket.send_json({"tipo": "list"})
    lista = ref_socket.recv_json()
    
    if lista:
        eleito = max(lista, key=lambda s: s["rank"])
        coordenador = eleito["nome"]
        
        pub_socket.send_string(f"servers {coordenador}")
        print(f"[ELEIÇÃO] Coordenador eleito: {coordenador}")

#---------------------------

def sincronizar_relogio(): #Berkeley
    global clock, coordenador
    if coordenador == nome_servidor:
        return
    try:
        sync_socket = context.socket(zmq.REQ)
        sync_socket.setsockopt(zmq.RCVTIMEO, 3000)
        sync_socket.connect(f"tcp://{coordenador}:{SERVER_PORT}")
        sync_socket.send_json({"tipo": "relogio"})
        resposta = sync_socket.recv_json()
        clock = resposta.get("clock", clock)
        print(f"[BERKELEY] Relógio sincronizado: {clock}")
    except zmq.error.Again:
        print(f"[BERKELEY] Coordenador {coordenador} não respondeu, iniciando eleição")
        eleger_coordenador()
    finally:
        sync_socket.close()

#---------------------------

def responder_inter_servidores():
    while True:
        msg = inter_socket.recv_json()
        
        if msg.get("tipo") == "relogio":
            inter_socket.send_json({"clock": clock})
        
        elif msg.get("tipo") == "replicar":
            # backup recebe publicação e salva
            salvar_publicacao(msg["data"])
            print(f"[REPLICAÇÃO] Publicação recebida e salva")
            inter_socket.send_json({"status": "OK"})
        
        elif msg.get("tipo") == "replicar_todos":
            # coordenador recebe de um backup e replica para todos
            salvar_publicacao(msg["data"])
            replicar_para_backups(msg["data"])
            inter_socket.send_json({"status": "OK"})

#---------------------------

def replicar_para_backups(data):
    if coordenador != nome_servidor:
        return  # só o coordenador replica para os backups
    
    ref_socket.send_json({"tipo": "list"})
    lista = ref_socket.recv_json()
    
    for servidor in lista:
        if servidor["nome"] != nome_servidor:
            try:
                rep_socket = context.socket(zmq.REQ)
                rep_socket.setsockopt(zmq.RCVTIMEO, 3000)
                rep_socket.connect(f"tcp://{servidor['nome']}:{REPL_PORT}")
                rep_socket.send_json({"tipo": "replicar", "data": data})
                rep_socket.recv_json()
                print(f"[REPLICAÇÃO] Enviado para {servidor['nome']}")
            except zmq.error.Again:
                print(f"[REPLICAÇÃO] Falhou para {servidor['nome']}")
            finally:
                rep_socket.close()

def encaminhar_para_coordenador(data):
    if coordenador is None or coordenador == nome_servidor:
        return
    try:
        enc_socket = context.socket(zmq.REQ)
        enc_socket.setsockopt(zmq.RCVTIMEO, 3000)
        enc_socket.connect(f"tcp://{coordenador}:{REPL_PORT}")
        enc_socket.send_json({"tipo": "replicar_todos", "data": data})
        enc_socket.recv_json()
        print(f"[REPLICAÇÃO] Encaminhado para coordenador {coordenador}")
    except zmq.error.Again:
        print(f"[REPLICAÇÃO] Coordenador não respondeu")
        eleger_coordenador()
    finally:
        enc_socket.close()

def responder_replicacao():
    while True:
        msg = repl_socket.recv_json()
        if msg.get("tipo") in ("replicar", "replicar_todos"):
            salvar_publicacao(msg["data"])
            if msg.get("tipo") == "replicar_todos":
                replicar_para_backups(msg["data"])
            print(f"[REPLICAÇÃO] Publicação recebida e salva")
            repl_socket.send_json({"status": "OK"})
        elif msg.get("tipo") == "historico":
            historico = []
            if os.path.exists(PUBLICACOES_FILE):
                with open(PUBLICACOES_FILE, "r") as f:
                    for linha in f:
                        historico.append(json.loads(linha))
            repl_socket.send_json(historico)
            return  # importante para não cair no send_json abaixo

threading.Thread(target=responder_replicacao, daemon=True).start()

#---------------------------

def responder_historico():
    while True:
        msg = hist_socket.recv_json()
        if msg.get("tipo") == "historico":
            historico = []
            if os.path.exists(PUBLICACOES_FILE):
                with open(PUBLICACOES_FILE, "r") as f:
                    for linha in f:
                        historico.append(json.loads(linha))
            hist_socket.send_json(historico)

threading.Thread(target=responder_historico, daemon=True).start()

#-------PRINCIPAL------------

while True:
    info = socket.recv()
    contador_mensagens += 1

    requisicao = mensagens_pb2.Requisicao()
    requisicao.ParseFromString(info)
    print(f"Recebido: {requisicao}", flush=True)

    clock = max(clock, requisicao.clock)
    if requisicao.HasField("pub"):
        clock = max(clock, requisicao.pub.clock)
    resposta = mensagens_pb2.Resposta()

    if requisicao.tipo == "login":
        usuario = requisicao.usuario
        if usuario in usuarios_logados:
            resposta.mensagem = "Login já logado"
        elif usuario in usuarios_aceitos:
            usuarios_logados.append(usuario)
            resposta.mensagem = "Login realizado com sucesso"
        elif usuario not in usuarios_aceitos:
            resposta.mensagem = "Usuário inválido"

    elif requisicao.tipo == "criar_canal":
        canal = requisicao.canal
        if canal in canais:
            resposta.mensagem = "Canal já existe"
        else:
            canais[canal] = []
            salvar_canais(canais)
            resposta.mensagem = f"Canal '{canal}' criado com sucesso"

    elif requisicao.tipo == "listar_canais":
        canais = carregar_canais()
        resposta.mensagem = ", ".join(canais.keys())
        
    elif requisicao.tipo == "publicar":
        canais = carregar_canais()
        canal = requisicao.canal
        if not requisicao.HasField("pub"):
            resposta.mensagem = "Erro: publicação inválida"
        elif canal not in canais:
            resposta.mensagem = "Canal não existe"
        else:
            mensagem = requisicao.pub.mensagem
            timestamp = requisicao.pub.timestamp_envio
            clock += 1
            pub_msg = {
                "mensagem": mensagem,
                "timestamp_envio": timestamp,
                "timestamp_servidor": int(time.time()),
                "clock": clock
            }
            pub_socket.send_string(f"{canal}|{json.dumps(pub_msg)}")
            salvar_publicacao({
                "canal": canal,
                "mensagem": mensagem,
                "timestamp": timestamp,
                "usuario": requisicao.usuario
            })

            data_replicar = {"canal": canal, "mensagem": mensagem, "timestamp": timestamp}
            if coordenador == nome_servidor:
                replicar_para_backups(data_replicar)   # sou primário, replico
            else:
                encaminhar_para_coordenador(data_replicar)

            resposta.mensagem = "Mensagem publicada com sucesso"

#----------- verificação do heartbeater ----------------
    if contador_mensagens % 15 == 0:
        ref_socket.send_json({
            "tipo": "heartbeat",
            "nome": nome_servidor
        })

        resposta_hb = ref_socket.recv_json()

        if resposta_hb.get("status") == "OK":
            print(f"[HEARTBEAT] OK")
            if coordenador is None:
                eleger_coordenador()
            else:
                sincronizar_relogio()
#----------- verificação do heartbeater ----------------

    # ---------------- RESPOSTA ----------------
    clock += 1
    resposta.timestamp = int(time.time())
    resposta.clock = clock
    socket.send(resposta.SerializeToString())
