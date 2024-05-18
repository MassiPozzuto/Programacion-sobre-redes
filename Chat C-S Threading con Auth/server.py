import socket
import threading
from database import Database

# Lista para almacenar todos los clientes conectados
connected_clients = []


def commands(command, client_socket, database, chatInfo, user):
    response = "El comando ingresado no existe"
    if command == '/help':
        response = "Los comandos disponibles son: \n  /sendTo <username>: Seleccionar el chat en el que enviaras mensajes, si colocas 'global' iras a un chat con todos los usuarios\n  /info: Indica el chat en el que te encuentras en ese momento\n  /help: Muestra todos los comandos disponibles y sus funciones"

    elif command.find('/sendTo') != -1:
        chatToChange = command.split()
        if chatToChange[1] == 'global':
            chatInfo = []
            response = f"Te has cambiado al chat global"
        else:
            if chatToChange[1] != user['username']:
                # Verificar que exista ese usuario
                targetUser = database.DBQuery(f"SELECT * FROM usuarios WHERE username = '{chatToChange[1]}'")
                if(len(targetUser) == 1):
                    chatInfo = targetUser[0]
                    response = f"Te has cambiado al chat de '{targetUser[0]['username']}'"
                else:
                    response = f"El nombre de usuario '{chatToChange[1]}' no existe"
            else:
                response = "No puedes tener un chat contigo mismo"

    elif command == '/info':
        if chatInfo == []:
            response = f"Te encontras en el chat global"
        else:
            response = f"Te encontras en el chat de '{chatInfo['username']}'"
    
    client_socket.send(response.encode())
    return chatInfo
    
# Función para reenviar los mensajes de un cliente a todos los demas clientes
def broadcast(message, sender_socket, user, chatInfo, database):
    if chatInfo == []:
        # Enviar el mensaje por el chat global
        # Guardo el mensaje en la base de datos
        database.DBQuery(f"INSERT INTO mensajes(id_origen, mensaje, id_destino) VALUES ({user['id']},'{message}', NULL)")
        for client_socket, _, _ in connected_clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(f"{user['username']}: {message}".encode())
                except:
                    # En caso de que haya un error al enviar el mensaje a algun cliente, se cierra la conexión y se elimina de la lista de clientes conectados
                    client_socket.close()
                    connected_clients.remove((client_socket, _))
    else:
        # Enviar el mensaje a un usuario especifico
        # Guardo el mensaje en la base de datos
        database.DBQuery(f"INSERT INTO mensajes(id_origen, mensaje, id_destino) VALUES ({user['id']},'{message}', {chatInfo['id']})")
        for client_socket, _, username in connected_clients:
            if username == chatInfo['username']:
                try:
                    client_socket.send(f"{user['username']} te envió el siguiente mensaje por privado: {message}".encode())
                except:
                    client_socket.close()
                    connected_clients.remove((client_socket, _))
                break


# Función que contiene lo que realizan los threads
def handle_client(client_socket, client_address, database):
    print(f"Conexión aceptada de {client_address[0]}:{client_address[1]}")
    
    #Log-in
    client_socket.send("Para conectarte al chat, primero debes iniciar sesión.".encode())
    while True:
        client_socket.send("Ingresa el nombre de usuario: ".encode())
        username = client_socket.recv(1024).decode()
        client_socket.send("Ingresa la contraseña: ".encode())
        password = client_socket.recv(1024).decode()

        user = database.DBQuery(f"SELECT * FROM usuarios WHERE username = '{username}' AND password = '{password}'")
        if(len(user) == 1):
            user = user[0]
            client_socket.send("Se ha iniciado sesión correctamente".encode())
            break
        else:
            client_socket.send("Error, nombre de usuario y/o contraseña incorrectos".encode())
        
        
    # Se agrega el nuevo cliente a la lista de clientes conectados
    connected_clients.append((client_socket, client_address, user['username']))
    print(connected_clients[0][2])
    
    # Recibo los mensajes del cliente y los reenvió a los demás
    client_socket.send(f"Te encuentras en el chat global, tus mensajes los podrán ver todos. Para saber como enviar mensajes a otros ingresa '/help'".encode())
    chatInfo = []
    while True:
        message = client_socket.recv(1024).decode()
        if not message:
            break
        print(f"Mensaje recibido de {client_address[0]}:{client_address[1]}: {message}")
        
        if message[0] == '/':
            chatInfo = commands(message, client_socket, database, chatInfo, user)
        else:
            # Llamo a la funcion broadcast para reenviar este mensaje a los demas clientes
            broadcast(message, client_socket, user, chatInfo, database)

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
