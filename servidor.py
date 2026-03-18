import zmq
import mensagens_pb2

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://broker:5556")

usuarios_aceitos = ["Pedro Henrique","Leonardo","João","Matheus"]
usuarios_logados = []

canais = {
    "Canal1": []
}

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
            resposta.mensagem = f"Canal '{canal}' criado com sucesso"

    elif requisicao.tipo == "listar_canais":
        resposta.mensagem = ", ".join(canais.keys())

    socket.send(resposta.SerializeToString())
