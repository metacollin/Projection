import zmq
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop import ioloop
from random import randrange, choice
import time
import string
import json
import threading

def randomName(length):
    return ''.join(choice(string.lowercase) for i in range(length))

def processInfoMsg(info_stream, msg):
    print msg
    info_stream.send(json.dumps(knownStreamVersions))

# format will be csv separated list
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5556")

# generate fake data streams
num_streams = 3
print("knownStreams:")
knownStreamVersions = {}
for i in range(num_streams):
    sname = randomName(6)
    knownStreamVersions[sname] = {
        "id": i,
        "version": randrange(1,4),
        "keyOrder": [randomName(3) for i in range(randrange(1,6))]
    }
    print(sname)
    print(knownStreamVersions[sname])
    print('')

print(knownStreamVersions.keys())

def threaded_loop():
    while run_event.is_set():
        timestamp = time.time()
        stream = knownStreamVersions[knownStreamVersions.keys()[randrange(0,num_streams)]]
        streamID = stream["id"]
        readings = [ randrange(0,100) for i in range(len(stream["keyOrder"])) ]
        data = [timestamp] + readings
        msg = [b"{0:04d}".format(streamID), json.dumps(data)]
        print("Sending data: " + str(msg))
        socket.send_multipart(msg)
        time.sleep(0.1)

run_event = threading.Event()
run_event.set()

t = threading.Thread(target=threaded_loop)
t.daemon = False
t.start()

# listeners can request the knownStreams dictionary on a req-rep socket
info_socket = context.socket(zmq.REP)
info_socket.bind("tcp://*:5557")

info_stream = ZMQStream(info_socket)
info_stream.on_recv_stream(processInfoMsg)

try:
    ioloop.IOLoop.instance().start()
except KeyboardInterrupt:
    print("Halt signal detected. Cleaning up...")
except:
    print "Exception in server code:"
    print '-'*60
    traceback.print_exc(file=sys.stdout)
    print '-'*60
    print("Cleaning up...")
finally:
    run_event.clear()
    t.join()
    info_socket.close()
    socket.close()
    context.term()
    print("Done.")
