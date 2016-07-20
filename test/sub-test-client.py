# just testing that the test server is working
import sys
import zmq
import json

context = zmq.Context()

info_socket = context.socket(zmq.REQ)
info_socket.connect("tcp://localhost:5557")
print("Asking server for a list of available streams")
info_socket.send("HELP")
response = info_socket.recv()
print("Server responds with...")
print(response)
print('')
knownStreamVersions = json.loads(response)

sub_socket = context.socket(zmq.SUB)

print("Collecting updates from data server...")
sub_socket.connect("tcp://localhost:5556")

# set default stream to 0 or use specified stream
stream_filter = sys.argv[1] if len(sys.argv) > 1 else '1'

for sub_stream in knownStreamVersions.keys():
    if knownStreamVersions[sub_stream]["id"] == int(stream_filter):
        break

keyOrder = knownStreamVersions[sub_stream]["keyOrder"]
num_entries = len(keyOrder)

stream_filter = stream_filter.zfill(4)
print("subscribing to stream: %s [%s]" % (sub_stream, stream_filter) )
print("expecting %i entries per measurement" % num_entries)

# ascii to unicode str
if isinstance(stream_filter, bytes):
    stream_filter = stream_filter.decode('ascii')
sub_socket.setsockopt_string(zmq.SUBSCRIBE, stream_filter)

# process 5 updates
total_readings = 0
for update_nbr in range(5):
    [streamID, content] = sub_socket.recv_multipart()
    timestamp, readings = content.split(',',1)
    print("[%s] %s" % (streamID, content))
    total_readings += int(readings.split(',',1)[0])

print float(total_readings)
print update_nbr
print float(total_readings)/(update_nbr+1)
print("Average readings for streamID: '%s' was %dF" % (stream_filter, float(total_readings)/(update_nbr+1)))

info_socket.close()
sub_socket.close()
context.term()
