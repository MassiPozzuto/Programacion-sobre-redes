import socket

HOST = "127.0.0.1" # Server IP
PORT = 65432 # Puerto de escucha del server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect((HOST, PORT))
  s.sendall(b"Hola soy el pela")
  data = s.recv(1024)

print(f"Received {data!r}")