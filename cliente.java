import org.zeromq.ZMQ;
import org.zeromq.ZContext;
import mensagens.MensagensProto.Requisicao;
import mensagens.MensagensProto.Resposta;

public class Cliente {

    public static void main(String[] args) throws Exception {

        try (ZContext context = new ZContext()) {
            ZMQ.Socket socket = context.createSocket(ZMQ.REQ);
            socket.connect("tcp://broker:5555");

            while (true) {

                // ── LOGIN ──────────────────────────────────────────────────
                String usuario = "Pedro Henrique";

                Requisicao loginMsg = Requisicao.newBuilder()
                        .setTipo("login")
                        .setUsuario(usuario)
                        .setTimestamp((int) (System.currentTimeMillis() / 1000))
                        .build();

                socket.send(loginMsg.toByteArray(), 0);

                byte[] respostaBytes = socket.recv(0);
                Resposta respostaLogin = Resposta.parseFrom(respostaBytes);
                System.out.println("Resposta do login: " + respostaLogin);

                // ── LISTAR CANAIS ──────────────────────────────────────────
                Requisicao listarMsg = Requisicao.newBuilder()
                        .setTipo("listar_canais")
                        .setUsuario("")
                        .setTimestamp((int) (System.currentTimeMillis() / 1000))
                        .build();

                socket.send(listarMsg.toByteArray(), 0);

                respostaBytes = socket.recv(0);
                Resposta respostaLista = Resposta.parseFrom(respostaBytes);
                System.out.println("Resposta da lista de canais: " + respostaLista);

                String listaStr = respostaLista.getMensagem();
                String[] canaisArray = listaStr.split(",");
                long quantidade = java.util.Arrays.stream(canaisArray)
                        .map(String::trim)
                        .filter(c -> !c.isEmpty())
                        .count();

                if (quantidade >= 5) {
                    System.out.println("5 Canais foram criados!");
                    break;
                }

                // ── CRIAR CANAL ────────────────────────────────────────────
                Requisicao criarMsg = Requisicao.newBuilder()
                        .setTipo("criar_canal")
                        .setCanal("Canal" + (quantidade + 1))
                        .setTimestamp((int) (System.currentTimeMillis() / 1000))
                        .build();

                socket.send(criarMsg.toByteArray(), 0);

                respostaBytes = socket.recv(0);
                Resposta respostaCriar = Resposta.parseFrom(respostaBytes);
                System.out.println("Resposta criar canal: " + respostaCriar);
            }
        }
    }
}