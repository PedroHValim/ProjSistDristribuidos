import zmq
import mensagens_pb2
from time import sleep
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://broker:5555")


while True:

    usuario = "Pedro Henrique"
    msg = mensagens_pb2.Requisicao()
    msg.tipo = "login"
    msg.usuario = usuario
    msg.timestamp = int(time.time())
    socket.send(msg.SerializeToString())

    resposta_bytes = socket.recv()
    resposta = mensagens_pb2.Resposta()
    resposta.ParseFromString(resposta_bytes)
    print(f"Resposta do login: {resposta}")



#------------------------------------------------------
    usuario = ""
    msg = mensagens_pb2.Requisicao()
    msg.tipo = "listar_canais"
    msg.usuario = usuario
    msg.timestamp = int(time.time())
    socket.send(msg.SerializeToString())

    resposta_bytes = socket.recv()
    resposta = mensagens_pb2.Resposta()
    resposta.ParseFromString(resposta_bytes)
    print(f"Resposta da lista de canais: {resposta}")

    lista_str = resposta.mensagem
    canais = [c.strip() for c in lista_str.split(",") if c.strip()]
    quantidade = len(canais)

    if(quantidade >= 5):
        print("5 Canais foram criados!")
        break
    

    msg = mensagens_pb2.Requisicao()
    msg.tipo = "criar_canal"
    msg.canal = f"Canal{quantidade + 1}"
    msg.timestamp = int(time.time())
    socket.send(msg.SerializeToString())

    resposta_bytes = socket.recv()
    resposta = mensagens_pb2.Resposta()
    resposta.ParseFromString(resposta_bytes)
    print(f"Resposta criar canal: {resposta}")
#------------------------------------------------------

    
    