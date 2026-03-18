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
    sleep(0.5)

    usuario = ""
    msg = mensagens_pb2.Requisicao()
    msg.tipo = "listar_canais"
    msg.usuario = usuario
    msg.timestamp = int(time.time())
    socket.send(msg.SerializeToString())
    