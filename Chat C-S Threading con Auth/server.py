import socket
import threading
from database import Database

# Lista para almacenar todos los clientes conectados
connected_clients = []

# Diccionario que contendra en que chat se encuentra cada usuario actualmente
currentChats = dict()


def commands(command, client_socket, database, user):
    global currentChats
    response = "El comando ingresado no existe"
    if (command == '/help'):
        response = "Los comandos disponibles son: \n  /sendTo <username>: Seleccionar el chat en el que enviaras mensajes, si colocas 'global' iras a un chat con todos los usuarios\n  /info: Indica el chat en el que te encuentras en ese momento\n  /help: Muestra todos los comandos disponibles y sus funciones\n  /exit: Cierra la conexión"

    elif (command.find('/sendTo') != -1):
        chatToChange = command.split()
        if len(chatToChange) == 1:
            response = f"Debes ingresar un parametro como un usuario o global"

        elif chatToChange[1] == 'global':
            if (currentChats[user['username']] == []):
                response = f"Ya te encuentras en el chat global"
            else:
                currentChats[user['username']] = []
                response = f"Te has cambiado al chat global"
        else:
            if (chatToChange[1] != user['username']):
                if (currentChats[user['username']] != [] and currentChats[user['username']]['username'].lower() == chatToChange[1].lower()):
                    response = f"Ya te encuentras en el chat de '{chatToChange[1]}'"
                else:
                    # Verificar que exista ese usuario
                    targetUser = database.DBQuery(f"SELECT * FROM usuarios WHERE username = '{chatToChange[1]}'")
                    if (len(targetUser) == 1):
                        currentChats[user['username']] = targetUser[0]  
                        response = f"Te has cambiado al chat de '{targetUser[0]['username']}'"
                    else:
                        response = f"El nombre de usuario '{chatToChange[1]}' no existe"
            else:
                response = "No puedes tener un chat contigo mismo"

    elif (command == '/info'):
        if (currentChats[user['username']] == []):
            response = f"Te encontras en el chat global"
        else:
            response = f"Te encontras en el chat de '{currentChats[user['username']]['username']}'"    
    
    client_socket.send(response.encode())
    return currentChats[user['username']]

# Funcion para loguearse
def login(client_socket, database):
    client_socket.send("Para conectarte al chat, primero debes iniciar sesión.".encode())
    while True:
        try:
            client_socket.send("Ingresa el nombre de usuario: ".encode())
            username = client_socket.recv(1024).decode()
            client_socket.send("Ingresa la contraseña: ".encode())
            password = client_socket.recv(1024).decode()
        except:
            return False
        
        user = database.DBQuery(f"SELECT * FROM usuarios WHERE username = '{username}' AND password = '{password}'")
        if(len(user) == 1):
            user = user[0]
            client_socket.send("Se ha iniciado sesión correctamente".encode())
            return user
        else:
            client_socket.send("Error, nombre de usuario y/o contraseña incorrectos".encode())

#Funcion para cargar los mensajes previos de los chats
def chargePreviousMesage(currentChat, user, client_socket, database):
    chargeMessages = ""
    if currentChat == []:
        # Chat global
        previousMessages = database.DBQuery(f"""SELECT m.*, u.username FROM mensajes m
                                                INNER JOIN usuarios u ON m.id_origen = u.id
                                                WHERE m.id_destino IS NULL""")
    else:
        # Chat específico
        previousMessages = database.DBQuery(f"""SELECT u.username, m.mensaje, m.created_at  FROM mensajes m
                                                INNER JOIN usuarios u ON m.id_origen = u.id
                                                WHERE 
                                                    (m.id_origen = {user['id']} AND m.id_destino = {currentChat['id']}) 
                                                    OR 
                                                    (m.id_origen = {currentChat['id']} AND m.id_destino = {user['id']})""")
        # Actualizo los mensajes que no habia leido aún
        database.DBQuery(f"UPDATE mensajes SET readed = 1 WHERE id_destino = {user['id']} AND readed IS NULL")

    if previousMessages != []:
        for i, previousMessage in enumerate(previousMessages):
            chargeMessages += f"{previousMessage['username']} ({previousMessage['created_at']}): {previousMessage['mensaje']}"
            if(i != len(previousMessages) - 1): chargeMessages += f"\n"
    else: 
        chargeMessages = "Aún no hay mensajes en este chat. Envia un mensaje para iniciar la conversación"

    client_socket.send(chargeMessages.encode())


# Función para reenviar los mensajes de un cliente a todos los demas clientes
def broadcast(message, sender_socket, user, database):
    global currentChats
    if currentChats[user['username']] == []:
        # Enviar el mensaje por el chat global
        # Guardo el mensaje en la base de datos
        database.DBQuery(f"INSERT INTO mensajes(id_origen, mensaje, id_destino, readed) VALUES ({user['id']},'{message}', NULL, NULL)")
        for client_socket, _, username in connected_clients:
            if client_socket != sender_socket:
                try:
                    if currentChats[username] != []:
                        # El usuario (de x iteración) que esta conectado en el chat pero que no se encuentra en el global, recibira una notificacion 
                        client_socket.send(f"Notification:Tienes una nueva notificación:Hay nuevos mensajes en el chat global".encode())
                    else:
                        client_socket.send(f"{user['username']}: {message}".encode())
                except:
                    # En caso de que haya un error al enviar el mensaje a algun cliente, se cierra la conexión y se elimina de la lista de clientes conectados
                    connected_clients.remove((client_socket, _, username))
                    del currentChats[username]
                    client_socket.close()
    else:
        # Enviar el mensaje a un usuario especifico
        # Guardo el mensaje en la base de datos
        insertMesaggeToBD = f"INSERT INTO mensajes(id_origen, mensaje, id_destino, readed) VALUES ({user['id']},'{message}', {currentChats[user['username']]['id']}, NULL)"
        for client_socket, _, username in connected_clients:
            if username == currentChats[user['username']]['username']:
                try:
                    if currentChats[username] != [] and currentChats[username]['username'] == user['username']:
                            # El usuario (de x iteración) que esta conectado en el chat mutuo, recibira el mensaje (siguiendo el chat) 
                            client_socket.send(f"{user['username']}: {message}".encode())
                            # Inserto el mensaje en la BD marcando la columna readed como true
                            insertMesaggeToBD = (f"INSERT INTO mensajes(id_origen, mensaje, id_destino, readed) VALUES ({user['id']},'{message}', {currentChats[user['username']]['id']}, 1)")
                    else:
                        # El usuario (de x iteración) que esta conectado en el chat pero que no se encuentra en el mutuo, recibira una notificacion
                        client_socket.send(f"Notification:Tienes una nueva notificación:{user['username']} te envió un mensaje por privado".encode())
                except:
                    connected_clients.remove((client_socket, _, username))
                    del currentChats[username]
                    client_socket.close()
                break
        database.DBQuery(insertMesaggeToBD)

# Función que contiene lo que realizan los threads
def handleClient(client_socket, client_address, database):
    global connected_clients
    global currentChats
    print(f"Conexión aceptada de {client_address[0]}:{client_address[1]}")
    
    #Log-in
    user = login(client_socket, database)
    if user == False:
        print(f"Conexión cerrada de {client_address[0]}:{client_address[1]}")
        client_socket.close()
        return
        
    # Se agrega el nuevo cliente a la lista de clientes conectados 
    connected_clients.append((client_socket, client_address, user['username']))
    currentChats[user['username']] = []   
    
    # Recibo los mensajes del cliente y los reenvió a los demás
    client_socket.send(f"Te encuentras en el chat global, tus mensajes los podrán ver todos. Para saber como enviar mensajes a otros ingresa '/help'".encode())
    
    chargePreviousMesage([], user, client_socket, database)

    # Reviso si tiene mensajes sin leer
    unreadMessages = database.DBQuery(f"""SELECT u.username FROM mensajes m 
                                            INNER JOIN usuarios u ON u.id = m.id_origen 
                                            WHERE m.readed IS NULL AND m.id_destino = {user['id']} GROUP BY u.username""")
    if unreadMessages != []:
        noticeMessage = "Notification:Tienes mensajes sin leer:Tienes mensajes sin leer en el chat de "
        for indice, unreadMessagesChat in enumerate(unreadMessages):
            if (indice > 0 and indice != len(unreadMessages) - 1) : noticeMessage += ", de "
            elif (indice == len(unreadMessages) - 1) : noticeMessage += " y de "
            noticeMessage += f"{unreadMessagesChat['username']}"
        client_socket.send(noticeMessage.encode())
                                            
    currentChats[user['username']] = []
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"Mensaje recibido de {client_address[0]}:{client_address[1]}: {message}")
            
            if message[0] == '/':
                prevChat = currentChats[user['username']]
                currentChats[user['username']] = commands(message, client_socket, database, user)
                if message.startswith('/sendTo') and currentChats[user['username']] != prevChat:
                    chargePreviousMesage(currentChats[user['username']], user, client_socket, database)
            else:
                # Llamo a la funcion broadcast para reenviar este mensaje a los demas clientes
                broadcast(message, client_socket, user, database)
        except:
            print(f"Conexión cerrada de {client_address[0]}:{client_address[1]}")
            connected_clients.remove((client_socket, client_address, user['username']))
            del currentChats[user['username']]
            client_socket.close()
            break
    

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
            client_thread = threading.Thread(target=handleClient, args=(client_socket, client_address, database))
            client_thread.start()

if __name__ == "__main__":
    main()
