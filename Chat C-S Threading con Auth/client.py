import socket
import threading
from plyer import notification

class ChatClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
    
    def start(self):
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        while True:
            try:
                message = input()
                if message == '/exit':
                    break
                self.client_socket.send(message.encode())
            except KeyboardInterrupt:
                print("(Si esta deseando interrumpir el programa ingrese el comando '/exit')")
        self.client_socket.close()


    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                data_decoded = data.decode()
                if data_decoded.startswith('Notification'):
                    ChatClient.show_notification(data_decoded)
                else:
                    print(data_decoded)
            except:
                break

    @staticmethod
    def show_notification(data_decoded):
        data_notification = data_decoded.split(':')
        notification.notify(
            title=data_notification[1],
            message=data_notification[2],
            app_name='Chat Cliente-Servidor',
            timeout=10,
        )

def main():
    chat_client = ChatClient()
    chat_client.start()

if __name__ == "__main__":
    main()