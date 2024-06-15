import socket
import threading
#El servidor esta escuchando en el puerto
 
class ServerSocket():
    def __init__(self, host = '127.0.0.1', port = 64333):
        self.HOST = host
        self.PORT = port
        self.connected_clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
        
        self.accounts = []
        self.accounts.append(['Massi', '123'])
        self.accounts.append(['Simon', '12345'])
        self.accounts.append(['Alejandro', 'contraseña'])
    
    def start(self):
        self.server_socket.listen(5)
        print(f"El servidor esta escuchando en el puerto {self.PORT}")
        
        send_message_thread = threading.Thread(target=self.sendMessages)
        send_message_thread.start()
        
        while True:
            client_socket, client_address =  self.server_socket.accept()
            print(f"Conexión aceptada del cliente: {client_address[0]}:{client_address[1]}")
            client_thread = threading.Thread(target=self.handleClient, args=(client_socket, client_address))
            client_thread.start()
    
    
    def sendMessages(self):
        while True:
            try:
                message = input()
                
                if message.startswith('/'):
                    if message == '/close':
                        break
                    
                    if message.startswith('all') == False:
                        print(self.commands(message))
                    else:
                        print("Ya le envias mensajes a todos los clientes")
                else:
                    if self.connected_clients != []:
                        for client_socket, _, _ in self.connected_clients:
                            client_socket.send(f"Servidor: {message}".encode())
                    else:
                        print("Actualmente no hay clientes conectados")
            except KeyboardInterrupt:
                print("Si queres cerrar la conexion ingresa: /close")
    
    
    def handleClient(self, client_socket, client_address):
        client_socket.send("Bienvenido al chat\n".encode())
        
        userConnected = self.login(client_socket)
        if not userConnected:
            client_socket.close()
            return
        
        self.connected_clients.append((client_socket, client_address, userConnected))
        print(f"Actualmente hay conectados: {len(self.connected_clients)} clientes")
        
        while True:
            try:
                message = client_socket.recv(1024).decode()
                print(f"Mensaje recibido de {client_address[0]}:{client_address[1]}: {message}")
                if message.startswith('/'):
                    response_command = self.commands(message, client_socket, userConnected) 
                    if message.startswith('/all') == False:
                        client_socket.send(response_command) 
            except:
                print("El cliente se ha desconectado 1")
                self.connected_clients.remove((client_socket, client_address, userConnected))
                client_socket.close()
        
    def commands(self, message, sender_socket = '', sender_username = ''):
        if message.startswith('/all'):
            messageClear = message.split('/all ')
            if len(self.connected_clients) > 1:
                for client_socket, _, _ in self.connected_clients:
                    if client_socket != sender_socket:
                        client_socket.send(f"{sender_username}: {messageClear[1]}".encode())
            else:
                sender_socket.send("Actualmente no hay clientes conectados")
        elif message == '/ips':
            if self.connected_clients != []:
                response = "Las IPS de los clientes conectados son:\n"
                for _, client_address, _ in self.connected_clients:
                    response += f"  - {client_address[0]}:{client_address[1]}\n"
            else:
                response = "Actualmente no hay clientes conectados"
        elif message == '/users':
            if self.connected_clients != []:
                response = "Los usernames conectados son:\n"
                for _, _, usernameConnected in self.connected_clients:
                    response += f"  - {usernameConnected}\n"
            else:
                response = "Actualmente no hay clientes conectados"
        else:
            response = "El comando ingresado no existe"
        
        #return response
                    
            
        
    
    def login(self, client_socket):        
        client_socket.send("Para ingresar al chat debe ingresar sesión\n".encode())
        while True:
            try:
                client_socket.send("Ingrese un username:".encode())
                username = client_socket.recv(1024).decode()
                client_socket.send("Ingrese una contraseña:".encode())
                password = client_socket.recv(1024).decode()

                if self.connected_clients != []:
                    for _, _, usernameConnected in self.connected_clients:
                        if username == usernameConnected:
                            client_socket.send("Ya hay un usuario conectado a esa cuenta. Conexión rechazada".encode())
                            return False
            
                for account in self.accounts:
                    if account[0] == username and account[1] == password:
                        client_socket.send("Ha iniciado sesión correctamente. Se encuentra conectado al chat".encode())
                        return username
                
                print("Los datos ingresados son incorrectos. Conexión rechazada")
                client_socket.send("Los datos ingresados son incorrectos. Conexión rechazada".encode())
                return False
            except ConnectionResetError:
                print("El cliente se ha desconectado 2")
                return False
    

if __name__ == "__main__":
    chat = ServerSocket()
    chat.start()
    print("Finish")