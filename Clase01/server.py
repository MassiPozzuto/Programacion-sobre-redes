import socket

HOST = "127.0.0.1" # Localhost
PORT = 65432 # Puerto de escucha

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.bind((HOST, PORT))
  print(f"Escuchando en el puerto {PORT} en la IP {HOST}")
  s.listen()
  conn, addr = s.accept()
  with conn:
    print(f"Conectando a {addr}")
    while True:
      data = conn.recv(1024)
      if not data:
        break
      conn.sendall(data)