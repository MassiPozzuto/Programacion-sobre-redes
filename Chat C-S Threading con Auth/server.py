import socket
import threading
from database import Database

# Lista para almacenar todos los clientes conectados
connected_clients = []

def commands(command, client_socket, database, user):
    if command == 'help':
        client_socket.send("Los comandos disponibles son: \n'/global': Enviar mensajes por el chat global\n'/sendTo <username>': Enviar mensajes a un usuario en especifico\n'/info': Indica el chat en el que te encuentras en ese momento")
    elif command == 'global':
        return 0
    elif command == 'sendTo':
        return 0
    elif command == 'info':
        return 0

# Función para reenviar los mensajes de un cliente a todos los demas clientes
def broadcast(message, sender_socket, user):
    for client_socket, _ in connected_clients:
        if client_socket != sender_socket:
            try:
                client_socket.send(f"{user['username']}: {message}".encode())
            except:
                # En caso de que haya un error al enviar el mensaje a algun cliente, se cierra la conexión y se elimina de la lista de clientes conectados
                client_socket.close()
                connected_clients.remove((client_socket, _))


# Función que contiene lo que realizan los threads
def handle_client(client_socket, client_address, database):
    print(f"Conexión aceptada de {client_address[0]}:{client_address[1]}")
    
    #Log-in
    client_socket.send("Para conectarte al chat, primero debes iniciar sesión.".encode())
    while True:
        client_socket.send("Ingresa el nombre de usuario: ".encode())
        username = client_socket.recv(1024).decode()
        client_socket.send("Ingresa la contraseña:/".encode())
        password = client_socket.recv(1024).decode()

        user = database.DBQuery(f"SELECT * FROM usuarios WHERE username = '{username}' AND password = '{password}'")
        if(len(user) == 1):
            user = user[0]
            client_socket.send("Se ha iniciado sesión correctamente".encode())
            break
        else:
            client_socket.send("Error, nombre de usuario y/o contraseña incorrectos".encode())
        
        
    # Se agrega el nuevo cliente a la lista de clientes conectados
    connected_clients.append((client_socket, client_address))
    
    # Recibo los mensajes del cliente y los reenvió a los demás
    client_socket.send(f"Te encuentras en el chat global, tus mensajes los podrán ver todos. Para saber como enviar mensajes a alguien especifico ingresa '/help'".encode())
    while True:
        message = client_socket.recv(1024).decode()
        if not message:
            break
        print(f"Mensaje recibido de {client_address[0]}:{client_address[1]}: {message}")
    
        if message[0] == '/':
            commands()
        else:
            # Guardo el mensaje en la base de datos
            database.DBQuery(f"INSERT INTO mensajes(id_origen, mensaje, id_destino) VALUES ({user['id']},'{message}', NULL)")
            # Llamo a la funcion broadcast para reenviar este mensaje a los demas clientes
            broadcast(message, client_socket, username)

    print(f"Conexión cerrada de {client_address[0]}:{client_address[1]}")
    client_socket.close()
    connected_clients.remove((client_socket, client_address, user))
    

# Función principal se abre el servidor y se crean los threads
def main():
    HOST = '127.0.0.1'
    PORT = 65432

    # Inicializo la conexion con la base de datos 'chat'
    database = Database("chat")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Servidor escuchando en {HOST}:{PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, database))
            client_thread.start()

if __name__ == "__main__":
    main()
