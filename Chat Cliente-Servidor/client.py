import socket

HOST = "127.0.0.1"  # Dirección IP del servidor
PORT = 65432         # Puerto de escucha del servidor

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect((HOST, PORT))
  print("Conectado al servidor.")
  while True:
    # Mensaje al servidor
    message = input("Cliente (Tu): ")
    s.sendall(message.encode())  # Codificar el mensaje de string a bytes
    if message.lower() == "chau":
      print("Cerraste la conexión con el servidor.")
      break
    # Respuesta del servidor
    data = s.recv(1024)
    reply = data.decode()
    print(f"Servidor: {reply}")  # Decodificar la respuesta de bytes a string
    if reply.lower() == "chau":
      print("El servidor cerró la conexión.")
      break