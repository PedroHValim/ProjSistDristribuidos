import zmq

context = zmq.Context()

sub = context.socket(zmq.XSUB)
sub.bind("tcp://*:5557")

xpub = context.socket(zmq.XPUB)
xpub.bind("tcp://*:5558")

print("Proxy Pub/Sub rodando...")

zmq.proxy(sub, pub)