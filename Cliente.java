import org.zeromq.ZMQ;
import org.zeromq.ZContext;
import mensagens.MensagensProto.Requisicao;
import mensagens.MensagensProto.Resposta;
import org.json.JSONObject;
import java.util.*;

public class Cliente {

    private static int clock = 0;
    public static void main(String[] args) throws Exception {

        try (ZContext context = new ZContext()) {

            ZMQ.Socket req = context.createSocket(ZMQ.REQ);
            req.connect("tcp://broker:5555");

            ZMQ.Socket sub = context.createSocket(ZMQ.SUB);
            sub.connect("tcp://pubsub-proxy:5558");


            // ── THREAD PARA RECEBER MENSAGENS ─────────────────────
            new Thread(() -> {
                while (!Thread.currentThread().isInterrupted()) {
                    String msg = sub.recvStr();
                    String[] partes = msg.split("\\|", 2);

                    String canal = partes[0];
                    JSONObject json = new JSONObject(partes[1]);
                    int clockRecebido = json.getInt("clock");
                    clock = Math.max(clock, clockRecebido);
                    String mensagem = json.getString("mensagem");
                    long timestampEnvio = json.getLong("timestamp_envio");
                    long timestampRecebido = System.currentTimeMillis() / 1000;

                    System.out.println("\n📡 Mensagem recebida:");
                    System.out.println("Canal: " + canal);
                    System.out.println("Mensagem: " + mensagem);
                    System.out.println("Enviada em: " + timestampEnvio);
                    System.out.println("Recebida em: " + timestampRecebido);
                }
            }).start();

            String usuario = "Pedro Henrique";

            // ── LOGIN ─────────────────────────────────────────────
            clock++;
            Requisicao loginMsg = Requisicao.newBuilder()
                    .setTipo("login")
                    .setUsuario(usuario)
                    .setTimestamp(System.currentTimeMillis() / 1000)
                    .setClock(clock)
                    .build();

            req.send(loginMsg.toByteArray(), 0);

            byte[] respostaBytes = req.recv(0);
            Resposta respostaLogin = Resposta.parseFrom(respostaBytes);
            clock = Math.max(clock, respostaLogin.getClock());
            System.out.println("Login: " + respostaLogin.getMensagem());

            // ── LISTAR CANAIS ────────────────────────────────────
            clock++;
            Requisicao listarMsg = Requisicao.newBuilder()
                    .setTipo("listar_canais")
                    .setTimestamp(System.currentTimeMillis() / 1000)
                    .setClock(clock)
                    .build();

            req.send(listarMsg.toByteArray(), 0);

            respostaBytes = req.recv(0);
            Resposta respostaLista = Resposta.parseFrom(respostaBytes);
            clock = Math.max(clock, respostaLista.getClock());
            System.out.println("Canais disponíveis: " + respostaLista.getMensagem());

            List<String> canais = new ArrayList<>();

            for (String c : respostaLista.getMensagem().split(",")) {
                c = c.trim();
                if (!c.isEmpty()) canais.add(c);
            }

            // ── GARANTIR PELO MENOS 5 CANAIS ─────────────────────
            while (canais.size() < 5) {

                String novoCanal = "Canal" + (canais.size() + 1);
                clock++;
                Requisicao criarMsg = Requisicao.newBuilder()
                        .setTipo("criar_canal")
                        .setCanal(novoCanal)
                        .setTimestamp(System.currentTimeMillis() / 1000)
                        .setClock(clock)
                        .build();

                req.send(criarMsg.toByteArray(), 0);

                respostaBytes = req.recv(0);
                Resposta respostaCriar = Resposta.parseFrom(respostaBytes);
                clock = Math.max(clock, respostaCriar.getClock());
                System.out.println("Criar canal: " + respostaCriar.getMensagem());

                canais.add(novoCanal);
            }

            // ── INSCREVER EM ATÉ 3 CANAIS ────────────────────────
            Collections.shuffle(canais);
            List<String> inscritos = new ArrayList<>();

            for (int i = 0; i < Math.min(3, canais.size()); i++) {
                String canal = canais.get(i);
                if (!inscritos.contains(canal)) {
                    sub.subscribe(canal.getBytes());
                    inscritos.add(canal);
                    System.out.println("Inscrito no canal: " + canal);
                }
            }

            Random random = new Random();

            // ── LOOP INFINITO (ENVIO DE MENSAGENS) ───────────────
            while (true) {

                String canalEscolhido = canais.get(random.nextInt(canais.size()));

                for (int i = 0; i < 10; i++) {

                    String mensagem = "Msg " + random.nextInt(1000);
                    clock++;
                    Requisicao pubMsg = Requisicao.newBuilder()
                            .setTipo("publicar")
                            .setCanal(canalEscolhido)
                            .setTimestamp(System.currentTimeMillis() / 1000)
                            .setClock(clock)
                            .setPub(
                                    Requisicao.Publicacao.newBuilder()
                                            .setMensagem(mensagem)
                                            .setTimestampEnvio(System.currentTimeMillis() / 1000)
                                            .setClock(clock)
                                            .build()
                            )
                            .build();

                    req.send(pubMsg.toByteArray(), 0);

                    respostaBytes = req.recv(0);
                    Resposta respostaPub = Resposta.parseFrom(respostaBytes);
                    clock = Math.max(clock, respostaPub.getClock());
                    System.out.println("Publicação: " + respostaPub.getMensagem());

                    Thread.sleep(1000);
                }
            }
        }
    }
}