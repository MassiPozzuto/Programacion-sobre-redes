#pip install plyer
import socket
import threading
from plyer import notification

def receive_messages(socket_cliente):
    while True:
        try:
            data = socket_cliente.recv(1024)
            if not data:
                break

            dataDecoded = data.decode()
            # Notificaciones de mensajes
            if dataDecoded.startswith('Notification'):
                dataNotification = dataDecoded.split(':')
                notification.notify(
                    title = dataNotification[1],
                    message = dataNotification[2],
                    app_name = 'Chat Cliente-Servidor',
                    timeout = 10,  # Duración de la notificación en segundos
                )
            else:
                print(dataDecoded)
        except:
            break

def main():
    HOST = '127.0.0.1'
    PORT = 65432


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        # Crear un hilo para recibir mensajes mientras se envían
        recibir_thread = threading.Thread(target = receive_messages, args = (client_socket,))
        recibir_thread.start()

        while True:
            message = input()
            if (message == '/exit'): break
            client_socket.send(message.encode())

        client_socket.close()

if __name__ == "__main__":
    main()