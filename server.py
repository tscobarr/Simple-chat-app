import socket
import threading
from AES import encrypt_message, decrypt_message
from Kyber_Toy_Implementation.kyberKEM import keygenKEM, decapsulate
from Kyber_Toy_Implementation.kyber_params import KYBER_PARAMS

class Server:
    def __init__(self, host="localhost", port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = []
        self.clients_lock = threading.Lock()
        self.params = KYBER_PARAMS["kyber512"]
        self.serverPublicKey, self.serverPrivateKey = keygenKEM()
        self.client_keys = {}

    # Broadcast a message to all clients
    def broadcast_message(self, message, sender=None):
        with self.clients_lock:
            for client in self.clients:
                if client != sender:
                    try:
                        sharedKey = self.client_keys[client]  # Get the shared key
                        if isinstance(message, bytes):
                            encrypted_message = message
                        else:
                            encrypted_message = encrypt_message(message, sharedKey)
                        print(f"Sending message to client: {encrypted_message}")  # Debug print
                        client.sendall(encrypted_message)
                    except Exception as e:
                        print(f"Error sending message to a client: {e}")
                        self.clients.remove(client)
                        del self.client_keys[client]  # Remove the shared key

    # Handle each client in a separate thread
    def handle_client(self, client, addr):
        print(f"Client {addr} connected.")
        
        sharedKey = self.key_exchange(client)
        self.client_keys[client] = sharedKey  # Store the shared key
        
        client.sendall(encrypt_message("Enter your username: ", sharedKey))
        username = decrypt_message(client.recv(4096), sharedKey)
        print(f"{username} has joined the chat.")
        self.broadcast_message(f"{username} has joined the chat!")

        while True:
            try:
                encrypted_message = client.recv(4096)
                if not encrypted_message:
                    break
                print(f"Encrypted message received from {username}: {encrypted_message}")  # Debug print
                message = decrypt_message(encrypted_message, sharedKey)
                print(f"Decrypted message from {username}: {message}")  # Debug print
                self.broadcast_message(f"{username}: {message}", sender=client)
            except Exception as e:
                print(f"Error with client {username}: {e}")
                break

        print(f"{username} has left the chat.")
        self.broadcast_message(f"{username} has left the chat.")
        with self.clients_lock:
            if client in self.clients:
                self.clients.remove(client)
                del self.client_keys[client]  # Remove the shared key
        client.close()

    def key_exchange(self, client):
        client.sendall(self.serverPublicKey)
        ciphertext = client.recv(4096)
        sharedKey = decapsulate(self.serverPrivateKey, ciphertext, self.params)
        print(f"Shared key (server): {sharedKey}")  # Debug print
        return sharedKey
    
    def start(self):
        print(f"Server is listening on {self.host}:{self.port}...")
        while True:
            client, addr = self.server.accept()
            with self.clients_lock:
                self.clients.append(client)
            thread = threading.Thread(target=self.handle_client, args=(client, addr))
            thread.start()

server=Server()
server.start()