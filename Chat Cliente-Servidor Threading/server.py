import socket
import threading

# Lista para almacenar todos los clientes conectados
connected_clients = []

# Función para reenviar los mensajes de un cliente a todos los demas clientes
def broadcast(message, sender_socket):
    for index, (client_socket, _) in enumerate(connected_clients):
        if client_socket != sender_socket:
            try:
                client_socket.send(f"Persona {index}: {message.decode()}".encode())
            except:
                # En caso de que haya un error al enviar el mensaje a algun cliente, se cierra la conexión y se elimina de la lista de clientes conectados
                client_socket.close()
                connected_clients.remove((client_socket, _))


# Función que contiene lo que realizan los threads
def handle_client(client_socket, client_address):
    print(f"Conexión aceptada de {client_address[0]}:{client_address[1]}")
    
    # Se agrega el nuevo cliente a la lista de clientes conectados
    connected_clients.append((client_socket, client_address))

    client_socket.send(f"Servidor: Las demás personas te identifican en el chat como 'Persona {len(connected_clients) - 1}'. Escribe en la consola para enviar un mensaje por el chat :).".encode())

    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(f"Mensaje recibido de {client_address[0]}:{client_address[1]}: {data.decode()}")
        # Llamo a la funcion broadcast para reenviar este mensaje a los demas clientes
        broadcast(data, client_socket)

    print(f"Conexión cerrada de {client_address[0]}:{client_address[1]}")
    client_socket.close()
    connected_clients.remove((client_socket, client_address))


# Función principal se abre el servidor y se crean los threads
def main():
    HOST = '127.0.0.1'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Servidor escuchando en {HOST}:{PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

if __name__ == "__main__":
    main()
