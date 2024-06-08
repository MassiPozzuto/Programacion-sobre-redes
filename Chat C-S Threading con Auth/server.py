import socket
import threading
from database import Database
import datetime

class ChatServer:
    # Cuando inicialice la clase: se abre el servidor y se realiza la conexión con la BD
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        # Inicializo la conexion con la base de datos 'chat'
        self.database = Database("chat")
        # Lista para almacenar todos los clientes conectados
        self.connected_clients = []
        # Diccionario que contendra en que chat se encuentra cada usuario actualmente
        self.current_chats = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        print(f"Servidor escuchando en {self.host}:{self.port}")

    
    # Una vez inicializado, lo pongo en modo listen y creo los threads
    def startThreading(self):
        self.server_socket.listen(5)
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handleClient, args=(client_socket, client_address))
            client_thread.start()


    # Función que contiene lo que realizan los threads
    def handleClient(self, client_socket, client_address):
        print(f"Conexión aceptada de {client_address[0]}:{client_address[1]}")
        
        #Log-in
        user = self.login(client_socket)
        if not user:
            print(f"Conexión cerrada de {client_address[0]}:{client_address[1]}")
            client_socket.close()
            return
        
        # Se agrega el nuevo cliente a la lista de clientes conectados 
        self.connected_clients.append((client_socket, client_address, user['username']))
        self.current_chats[user['username']] = []
        
        client_socket.send("Te encuentras en el chat global, tus mensajes los podrán ver todos. Para saber como enviar mensajes a otros ingresa '/help'".encode())
        # Cargo los mensajes previos del chat global
        self.chargePreviousMessage([], user, client_socket)
        # Notificación en caso de tener mensajes sin leer
        self.notifyUnreadMessages(user, client_socket)
        
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if not message:
                    break
                print(f"Mensaje recibido de {client_address[0]}:{client_address[1]}: {message}")
                
                if message[0] == '/':
                    prev_chat = self.current_chats[user['username']]
                    self.current_chats[user['username']] = self.commands(message, client_socket, user)
                    if message.startswith('/sendTo') and self.current_chats[user['username']] != prev_chat:
                        # Si efectivamente se cambió de chat, entonces cargo los mensajes previos del mismo
                        self.chargePreviousMessage(self.current_chats[user['username']], user, client_socket)
                else:
                    # Llamo a la funcion broadcast para reenviar este mensaje a los demas clientes
                    self.broadcast(message, client_socket, user)
            except:
                print(f"Conexión cerrada de {client_address[0]}:{client_address[1]}")
                self.connected_clients.remove((client_socket, client_address, user['username']))
                del self.current_chats[user['username']]
                client_socket.close()
                break

    # Funcion para loguearse
    def login(self, client_socket):
        client_socket.send("Para conectarte al chat, primero debes iniciar sesión.".encode())
        while True:
            try:
                client_socket.send("Ingresa el nombre de usuario: ".encode())
                username = client_socket.recv(1024).decode()
                client_socket.send("Ingresa la contraseña: ".encode())
                password = client_socket.recv(1024).decode()
            except:
                return False
            
            user = self.database.DBQuery(f"SELECT * FROM usuarios WHERE username = '{username}' AND password = '{password}'")
            if len(user) == 1:
                user = user[0]
                client_socket.send("Se ha iniciado sesión correctamente".encode())
                return user
            else:
                client_socket.send("Error, nombre de usuario y/o contraseña incorrectos".encode())

    def commands(self, command, client_socket, user):
        response = "El comando ingresado no existe"
        if command == '/help':
            response = ("Los comandos disponibles son: \n"
                        "  /sendTo <username>: Seleccionar el chat en el que enviaras mensajes, si colocas 'global' iras a un chat con todos los usuarios, sino deberas colocar el username de determinado usuario.\n"
                        "  /info: Indica el chat en el que te encuentras en ese momento.\n"
                        "  /users: Enseña todos los usuarios conectados en este momento.\n"
                        "  /help: Muestra todos los comandos disponibles y sus funciones.\n"
                        "  /exit: Cierra la conexión.")
        elif command.startswith('/sendTo'):
            response = self.changeChat(command, user)
        elif command == '/info':
            if self.current_chats[user['username']] == []:
                response = "Te encontras en el chat global"
            else:
                response = f"Te encontras en el chat de '{self.current_chats[user['username']]['username']}'"
        elif command == '/users':
            response = "Los usuarios conectados actualmente son: "
            for _, _, username in self.connected_clients:
                response += f"\n   - {username}"
        
        client_socket.send(response.encode())
        return self.current_chats[user['username']]

    def changeChat(self, command, user):
        chat_to_change = command.split()
        if len(chat_to_change) == 1:
            return "Debes ingresar un parametro como un usuario o global"
        elif chat_to_change[1] == 'global':
            if self.current_chats[user['username']] == []:
                return "Ya te encuentras en el chat global"
            else:
                self.current_chats[user['username']] = []
                return "Te has cambiado al chat global"
        else:
            if chat_to_change[1] != user['username']:
                if self.current_chats[user['username']] != [] and self.current_chats[user['username']]['username'].lower() == chat_to_change[1].lower():
                    return f"Ya te encuentras en el chat de '{chat_to_change[1]}'"
                else:
                    # Verificar que exista ese usuario
                    target_user = self.database.DBQuery(f"SELECT * FROM usuarios WHERE username = '{chat_to_change[1]}'")
                    if len(target_user) == 1:
                        self.current_chats[user['username']] = target_user[0]  
                        return f"Te has cambiado al chat de '{target_user[0]['username']}'"
                    else:
                        return f"El nombre de usuario '{chat_to_change[1]}' no existe"
            else:
                return "No puedes tener un chat contigo mismo"       


    #Funcion para cargar los mensajes previos de los chats
    def chargePreviousMessage(self, current_chat, user, client_socket):
        charge_messages = ""
        if current_chat == []:
            # Chat global
            previous_messages = self.database.DBQuery(
                """SELECT m.*, u.username FROM mensajes m
                   INNER JOIN usuarios u ON m.id_origen = u.id
                   WHERE m.id_destino IS NULL"""
            )
        else:
            # Chat específico
            previous_messages = self.database.DBQuery(
                f"""SELECT u.username, m.mensaje, m.created_at FROM mensajes m
                    INNER JOIN usuarios u ON m.id_origen = u.id
                    WHERE 
                        (m.id_origen = {user['id']} AND m.id_destino = {current_chat['id']}) 
                        OR 
                        (m.id_origen = {current_chat['id']} AND m.id_destino = {user['id']})"""
            )
            # Actualizo los mensajes del chat que no habia leido aún
            self.database.DBQuery(f"UPDATE mensajes SET readed = 1 WHERE id_destino = {user['id']} AND id_origen = {current_chat['id']} AND readed IS NULL")

        if previous_messages:
            for i, previous_message in enumerate(previous_messages):
                charge_messages += f"{previous_message['username']} ({previous_message['created_at'].strftime('%d/%m %H:%M')}): {previous_message['mensaje']}"
                if i != len(previous_messages) - 1:
                    charge_messages += "\n"
        else:
            charge_messages = "Aún no hay mensajes en este chat. Envia un mensaje para iniciar la conversación"

        client_socket.send(charge_messages.encode())

    def notifyUnreadMessages(self, user, client_socket):
        unread_messages = self.database.DBQuery(
            f"""SELECT u.username FROM mensajes m 
                INNER JOIN usuarios u ON u.id = m.id_origen 
                WHERE m.readed IS NULL AND m.id_destino = {user['id']} GROUP BY u.username"""
        )
        if unread_messages:
            notice_message = "Notification:Tienes mensajes sin leer:Tienes mensajes sin leer en el chat de "
            for idx, unread_message in enumerate(unread_messages):
                if idx > 0 and idx != len(unread_messages) - 1:
                    notice_message += ", de "
                elif idx == len(unread_messages) - 1:
                    notice_message += " y de "
                notice_message += unread_message['username']
            client_socket.send(notice_message.encode())

    # Función para reenviar los mensajes de un cliente a todos los demas clientes
    def broadcast(self, message, sender_socket, user):
        if self.current_chats[user['username']] == []:
            # Enviar el mensaje por el chat global
            # Guardo el mensaje en la base de datos
            self.database.DBQuery(f"INSERT INTO mensajes(id_origen, mensaje, id_destino, readed) VALUES ({user['id']},'{message}', NULL, NULL)")
            for client_socket, _, username in self.connected_clients:
                if client_socket != sender_socket:
                    try:
                        if self.current_chats[username] != []:
                            # El usuario (de x iteración) que esta conectado en el chat pero que no se encuentra en el global, recibira una notificacion
                            client_socket.send("Notification:Tienes una nueva notificación:Hay nuevos mensajes en el chat global".encode())
                        else:
                            client_socket.send(f"{user['username']} ({datetime.datetime.now().strftime('%d/%m %H:%M')}): {message}".encode())
                    except:
                        # En caso de que haya un error al enviar el mensaje a algun cliente, se cierra la conexión y se elimina de la lista de clientes conectados
                        self.connected_clients.remove((client_socket, _, username))
                        del self.current_chats[username]
                        client_socket.close()
        else:
            # Enviar el mensaje a un usuario especifico
            # Guardo el mensaje en la base de datos
            insert_message_to_bd = f"""INSERT INTO mensajes(id_origen, mensaje, id_destino, readed) 
                                        VALUES ({user['id']},'{message}', {self.current_chats[user['username']]['id']}, NULL)"""
            # Recorro el array que contiene los usuarios actualmente conectados con el servidor (connected_clients)
            for client_socket, _, username in self.connected_clients:
                # Si x iteracion coincide con el usuario al cual desea mandarle el mensaje, entonces es porque esta conectado
                if username == self.current_chats[user['username']]['username']:
                    try:
                        if self.current_chats[username] != [] and self.current_chats[username]['username'] == user['username']:
                            # El usuario (de x iteración) al que se le quiere enviar el mensaje, se encutra en el chat mutuo y recibira el mensaje (por consola)
                            client_socket.send(f"{user['username']} ({datetime.datetime.now().strftime('%d/%m %H:%M')}): {message}".encode())
                            # Modifico la inserción del mensaje a la BD, para marcar la columna readed como true (1)
                            insert_message_to_bd = f"INSERT INTO mensajes(id_origen, mensaje, id_destino, readed) VALUES ({user['id']},'{message}', {self.current_chats[user['username']]['id']}, 1)"
                        else:
                            # El usuario (de x iteración) al que se le quiere enviar el mensaje, se encuentra en otro chat (ej: el global) y recibira una notificacion
                            client_socket.send(f"Notification:Tienes una nueva notificación:{user['username']} te envió un mensaje por privado".encode())
                    except:
                        self.connected_clients.remove((client_socket, _, username))
                        del self.current_chats[username]
                        client_socket.close()
                    break
            self.database.DBQuery(insert_message_to_bd)

if __name__ == "__main__":
    chat_server = ChatServer()
    chat_server.startThreading()
