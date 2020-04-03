import pyhanlp
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    doc = socket.reecv().decode('utf8')

    return_doc = '.'.encode('utf8')
    socket.send(return_doc)