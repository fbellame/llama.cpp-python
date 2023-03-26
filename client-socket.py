#!/usr/bin/env python3

import socket
import sys

PORT = int(os.environ.get('PORT', 8080))
PROMPT = os.environ.get('PROMPT', "Transcript of a dialog, where the User interacts with an Assistant named Bob. Bob is helpful, kind, honest, good at writing, and never fails to answer the User's requests immediately and with precision.\nUser:Hello, Bob.\nBob:Hello. How may I help you today?\nUser:Please tell me the largest city in Europe.\nBob:Sure. The largest city in Europe is Moscow, the capital of Russia.\nUser:")
RPROMPT = os.environ.get('RPROMPT', "User:")
N_PREDICT = os.environ.get('N_PREDICT', "4096")
REPEAT_PENALTY = os.environ.get('REPEAT_PENALTY', "1.0")
N_THREADS = os.environ.get('N_THREADS', "4")

# Open connection to the chat server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', PORT))

# Pass the arguments. The protocol is really simple:
# 1. Pass the number of arguments followed by a linefeed
# 2. Pass the arguments, with each being followed by "0"
args = [
    b"-t\x00",
    N_THREADS.encode() + b"\x00",
    b"-n\x00",
    N_PREDICT.encode() + b"\x00",
    b"--repeat_penalty\x00",
    REPEAT_PENALTY.encode() + b"\x00",
    b"--color\x00",
    b"-i\x00",
    b"-r\x00",
    RPROMPT.encode() + b"\x00",
    b"-p\x00",
    PROMPT.encode() + b"\x00",
]
num_args = len(args) + 1
args.insert(0, str(num_args).encode() + b"\n")
request = b"".join(args)
sock.send(request)

# When we have passed the arguments, start printing socket data to the screen.
# This is done in a background job because we also want to send data when
# running in interactive mode.
def print_output():
    while True:
        data = sock.recv(1024)
        if not data:
            print("(disconnected, press \"enter\" twice to exit)")
            sys.exit()
        sys.stdout.buffer.write(data)
        sys.stdout.flush()

try:
    print_thread = threading.Thread(target=print_output)
    print_thread.start()

    while True:
        line = input(RPROMPT)
        if line == "":
            break
        sock.send(line.encode() + b"\n")
except KeyboardInterrupt:
    sock.close()
