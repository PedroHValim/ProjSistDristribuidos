import zmq
import json
from datetime import datetime

SEGUNDOS = 10

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.setsockopt(zmq.RCVTIMEO, 5000)
socket.connect("tcp://localhost:7200")

try:
    socket.send_json({"tipo": "historico"})
    historico = socket.recv_json()

    agora = datetime.now().timestamp()
    recentes = [e for e in historico if agora - e['timestamp'] <= SEGUNDOS]

    print(f"\n📋 Histórico recente ({len(recentes)} registros - últimos {SEGUNDOS} seg):\n")
    for entry in recentes:
        usuario = entry.get('usuario', 'Desconhecido')
        ts = datetime.fromtimestamp(entry['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
        print(f"[{ts}] {usuario} → Canal: {entry['canal']} | Mensagem: {entry['mensagem']}")

except zmq.error.Again:
    print("❌ Servidor não respondeu. Tente novamente em alguns segundos.")
finally:
    socket.close()