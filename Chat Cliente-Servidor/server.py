import socket

HOST = "127.0.0.1"  # Localhost
PORT = 65432         # Puerto de escucha

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.bind((HOST, PORT))
  print(f"Escuchando en el puerto {PORT} en la IP {HOST}")
  s.listen()
  conn, addr = s.accept()
  with conn:
    print(f"Conectando a {addr}")
    while True:
      # Esperar mensaje del cliente
      data = conn.recv(1024)
      if not data:
        break
      message = data.decode()  # Decodificar el mensaje de bytes a string
      print(f"Cliente: {message}")
      if message.lower() == "chau":
        print("El cliente cerró la conexión.")
        break
      # Respuesta al cliente
      reply = input("Servidor (Tu): ")
      conn.sendall(reply.encode())  # Codificar la respuesta de string a bytes
      if reply.lower() == "chau":
        print("Cerraste la conexión con el cliente.")
        break