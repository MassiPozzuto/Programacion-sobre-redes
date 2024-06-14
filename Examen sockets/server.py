import socket
import threading
#El servidor esta escuchando en el puerto
 
class ServerSocket():
    def __init__(self, host = '127.0.0.1', port = 64333):
        self.HOST = host
        self.PORT = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
    
    def start(self):
        self.server_socket.listen(5)
        print(f"El servidor esta escuchando en el puerto {self.PORT}")
        self.client_socket, self.client_address =  self.server_socket.accept()
        print(f"Conexión aceptada del cliente: {self.client_address[0]}:{self.client_address[1]}")
        
        self.client_socket.send("Bienvenido al chat\n".encode())
        
        send_message_thread = threading.Thread(target=self.sendMessages)
        send_message_thread.start()
        
        login = self.login()
        if login:
            while True:
                try:
                    data = self.client_socket.recv(1024)
                    print(f"Mensaje recibido de {self.client_address[0]}:{self.client_address[1]}: {data.decode()}")
                except ConnectionResetError:
                    print("El cliente se ha desconectado 1")
                    break
        
        self.client_socket.close()
    
    def sendMessages(self):
        while True:
            try:
                message = input()
                if message == '/close':
                    break
                self.client_socket.send(f"Servidor: {message}".encode())
            except KeyboardInterrupt:
                print("Si queres cerrar la conexion ingresa: /close")
    
    
    def login(self):
        self.accounts = []
        self.accounts.append(['Massi', '123'])
        self.accounts.append(['Simon', '12345'])
        self.accounts.append(['Alejandro', 'contraseña'])
        
        self.client_socket.send("Para ingresar al chat debe ingresar sesión\n".encode())
        while True:
            try:
                self.client_socket.send("Ingrese un username:".encode())
                username = self.client_socket.recv(1024).decode()
                self.client_socket.send("Ingrese una contraseña:".encode())
                password = self.client_socket.recv(1024).decode()
            
                for account in self.accounts:
                    if account[0] == username and account[1] == password:
                        self.client_socket.send("Ha iniciado sesión correctamente. Se encuentra conectado al chat".encode())
                        return True
                
                print("Los datos ingresados son incorrectos. Conexión rechazada")
                self.client_socket.send("Los datos ingresados son incorrectos. Conexión rechazada".encode())
                return False
            except ConnectionResetError:
                print("El cliente se ha desconectado 2")
                return False
    

if __name__ == "__main__":
    chat = ServerSocket()
    chat.start()