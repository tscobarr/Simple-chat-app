import socket
import threading
import json

# Configuración del servidor
HOST = '127.0.0.1'
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    """Envía un mensaje a todos los clientes conectados."""
    for client in clients:
        try:
            client.send(message)
        except:
            # Si falla el envío, eliminamos al cliente
            remove_client(client)

def handle(client):
    """Maneja la conexión de un cliente específico."""
    while True:
        try:
            # Recibe el mensaje del cliente
            message = client.recv(1024)
            broadcast(message)
        except:
            # Si ocurre un error, cerramos la conexión
            remove_client(client)
            break

def remove_client(client):
    """Elimina al cliente de las listas y notifica a los demás."""
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        client.close()

        nickname = nicknames[index]
        broadcast(f'{nickname} left the chat!'.encode('utf-8'))
        nicknames.remove(nickname)

def receive():
    """Acepta conexiones de nuevos clientes."""
    while True:
        try:
            client, address = server.accept()
            print(f"Connected with {str(address)}")

            # Solicita el apodo del cliente
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)

            print(f"Nickname of the client is {nickname}!")
            broadcast(f"{nickname} joined the chat!".encode('utf-8'))
            client.send('Connected to the server!'.encode('utf-8'))

            # Inicia un hilo para manejar al cliente
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            server.close()
            break

print("Server is listening...")
receive()