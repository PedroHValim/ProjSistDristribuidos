import org.zeromq.ZMQ;
import org.zeromq.ZContext;
import mensagens.MensagensProto.Requisicao;
import mensagens.MensagensProto.Resposta;

import java.util.*;

public class Cliente {

    public static void main(String[] args) throws Exception {

        try (ZContext context = new ZContext()) {

            ZMQ.Socket req = context.createSocket(ZMQ.REQ);
            req.connect("tcp://broker:5555");

            ZMQ.Socket sub = context.createSocket(ZMQ.SUB);
            sub.connect("tcp://pubsub-proxy:5558");

            String[] canais = respostaLista.getMensagem().split(",");
            List<String> inscritos = new ArrayList<>();

            for (String canal : canais) {
                canal = canal.trim();

                if (!canal.isEmpty() && inscritos.size() < 3) {
                    sub.subscribe(canal.getBytes());
                    inscritos.add(canal);

                    System.out.println("Inscrito no canal: " + canal);
                }
            }

            // ── THREAD PARA RECEBER MENSAGENS ─────────────────────
            new Thread(() -> {
                while (!Thread.currentThread().isInterrupted()) {
                    String msg = sub.recvStr();
                    String[] partes = msg.split(" ", 2);

                    String canal = partes[0];
                    String conteudo = partes[1];

                    long timestampRecebido = System.currentTimeMillis() / 1000;

                    System.out.println("\n📡 Mensagem recebida:");
                    System.out.println("Canal: " + canal);
                    System.out.println("Conteúdo: " + conteudo);
                    System.out.println("Recebido em: " + timestampRecebido);
                }
            }).start();

            String usuario = "Pedro Henrique";

            // ── LOGIN ─────────────────────────────────────────────
            Requisicao loginMsg = Requisicao.newBuilder()
                    .setTipo("login")
                    .setUsuario(usuario)
                    .setTimestamp(System.currentTimeMillis() / 1000)
                    .build();

            req.send(loginMsg.toByteArray(), 0);

            byte[] respostaBytes = req.recv(0);
            Resposta respostaLogin = Resposta.parseFrom(respostaBytes);
            System.out.println("Login: " + respostaLogin.getMensagem());

            // ── LISTAR CANAIS ────────────────────────────────────
            Requisicao listarMsg = Requisicao.newBuilder()
                    .setTipo("listar_canais")
                    .setTimestamp(System.currentTimeMillis() / 1000)
                    .build();

            req.send(listarMsg.toByteArray(), 0);

            respostaBytes = req.recv(0);
            Resposta respostaLista = Resposta.parseFrom(respostaBytes);

            System.out.println("Canais disponíveis: " + respostaLista.getMensagem());

            List<String> canais = new ArrayList<>();

            for (String c : respostaLista.getMensagem().split(",")) {
                c = c.trim();
                if (!c.isEmpty()) canais.add(c);
            }

            // ── GARANTIR PELO MENOS 5 CANAIS ─────────────────────
            while (canais.size() < 5) {

                String novoCanal = "Canal" + (canais.size() + 1);

                Requisicao criarMsg = Requisicao.newBuilder()
                        .setTipo("criar_canal")
                        .setCanal(novoCanal)
                        .setTimestamp(System.currentTimeMillis() / 1000)
                        .build();

                req.send(criarMsg.toByteArray(), 0);

                respostaBytes = req.recv(0);
                Resposta respostaCriar = Resposta.parseFrom(respostaBytes);

                System.out.println("Criar canal: " + respostaCriar.getMensagem());

                canais.add(novoCanal);
            }

            // ── INSCREVER EM ATÉ 3 CANAIS ────────────────────────
            Collections.shuffle(canais);
            List<String> inscritos = new ArrayList<>();

            for (int i = 0; i < Math.min(3, canais.size()); i++) {
                String canal = canais.get(i);
                sub.subscribe(canal.getBytes());
                inscritos.add(canal);
                System.out.println("Inscrito no canal: " + canal);
            }

            Random random = new Random();

            // ── LOOP INFINITO (ENVIO DE MENSAGENS) ───────────────
            while (true) {

                String canalEscolhido = canais.get(random.nextInt(canais.size()));

                for (int i = 0; i < 10; i++) {

                    String mensagem = "Msg " + random.nextInt(1000);

                    Requisicao pubMsg = Requisicao.newBuilder()
                            .setTipo("publicar")
                            .setCanal(canalEscolhido)
                            .setTimestamp(System.currentTimeMillis() / 1000)
                            .setPub(
                                    Requisicao.Publicacao.newBuilder()
                                            .setMensagem(mensagem)
                                            .setTimestampEnvio(System.currentTimeMillis() / 1000)
                                            .build()
                            )
                            .build();

                    req.send(pubMsg.toByteArray(), 0);

                    respostaBytes = req.recv(0);
                    Resposta respostaPub = Resposta.parseFrom(respostaBytes);

                    System.out.println("Publicação: " + respostaPub.getMensagem());

                    Thread.sleep(1000);
                }
            }
        }
    }
}