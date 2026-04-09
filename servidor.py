import zmq
import mensagens_pb2
import json
import time
import os

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://broker:5556")

pub_socket = context.socket(zmq.PUB)
pub_socket.connect("tcp://pubsub-proxy:5557")

usuarios_aceitos = ["Pedro Henrique","Leonardo","João","Matheus"]
usuarios_logados = []

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


#-------PRINCIPAL------------

while True:
    info = socket.recv()

    requisicao = mensagens_pb2.Requisicao()
    requisicao.ParseFromString(info)
    print(f"Recebido: {requisicao}", flush=True)

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
            pub_msg = {
                "mensagem": mensagem,
                "timestamp_envio": timestamp,
                "timestamp_servidor": int(time.time())
            }
            pub_socket.send_string(f"{canal} {json.dumps(pub_msg)}")
            salvar_publicacao({
                "canal": canal,
                "mensagem": mensagem,
                "timestamp": timestamp
            })
            resposta.mensagem = "Mensagem publicada com sucesso"

    # ---------------- RESPOSTA ----------------
    resposta.timestamp = int(time.time())
    socket.send(resposta.SerializeToString())
