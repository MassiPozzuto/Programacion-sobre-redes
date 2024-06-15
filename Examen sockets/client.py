import socket
import threading
#El servidor esta escuchando en el puerto
#########
#########
#CLIENTE#
#########
#########
#########

 
class ClientSocket():
    def __init__(self, host = '127.0.0.1', port = 64333):
        self.HOST = host
        self.PORT = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        print(f"El cliente esta conectado al servidor")
    
    def start(self):
        receive_message_thread = threading.Thread(target=self.receiveMessages)
        receive_message_thread.start()
        send_message_thread = threading.Thread(target=self.sendMessages)
        send_message_thread.start()
                
    def receiveMessages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                print(data.decode())
            except ConnectionResetError:
                break
        self.client_socket.close()
        
    def sendMessages(self):
        while True:
            try:
                message = input()
                if message == '/exit':
                    break
                self.client_socket.send(message.encode())
            except KeyboardInterrupt:
                print("Si queres cerrar la conexion ingresa: /exit")
            except:
                print("El servidor ha cerrado la conexión")
                break
        self.client_socket.close()
        
    

        
        

if __name__ == "__main__":
    chat = ClientSocket()
    chat.start()