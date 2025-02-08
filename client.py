import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from AES import encrypt_message, decrypt_message
from kyberKEM import encapsulate
from kyber_params import KYBER_PARAMS

class Client:
    def __init__(self, host="localhost", port=5555):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sharedKey = None
        self.params = KYBER_PARAMS["kyber512"]

    def connect(self):
        self.client.connect((self.host, self.port))
        self.key_exchange()
        username_prompt = decrypt_message(self.client.recv(4096), self.sharedKey)
        username = input(username_prompt + " ")
        self.client.sendall(encrypt_message(username, self.sharedKey))

    def send_message(self, message):
        encrypted_message = encrypt_message(message, self.sharedKey)
        self.client.sendall(encrypted_message)

    def key_exchange(self):
        serverPublicKey = self.client.recv(4096)
        self.sharedKey, ciphertext = encapsulate(serverPublicKey, self.params)
        print(f"Shared key (client): {self.sharedKey}")  # Debug print
        self.client.sendall(ciphertext)

    def receive_messages(self):
        while True:
            try:
                encrypted_message = self.client.recv(4096)
                if not encrypted_message:
                    break
                print(f"Encrypted message received: {encrypted_message}")  # Debug print
                message = decrypt_message(encrypted_message, self.sharedKey)
                print(f"Decrypted message: {message}")  # Debug print
                self.display_message(message)
            except Exception as e:
                error_message = f"Error receiving message or disconnected: {e}"
                print(error_message)
                self.display_message(error_message)
                break

    def display_message(self, message):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def start_gui(self):

        def send_message(event=None):
            message = input_field.get()
            if message.strip():
                self.send_message(message)
                self.display_message(f"You: {message}")
                input_field.delete(0, tk.END)

        root = tk.Tk()
        root.title("Chat App")
        root.geometry("500x600")
        root.resizable(False, False)

        canvas = tk.Canvas(root, width=500, height=600)
        canvas.pack(fill="both", expand=True)
        canvas.create_rectangle(0, 0, 500, 600, fill="#2C2F33", outline="")

        title_label = tk.Label(root, text="Chat Application", bg="#2C2F33", fg="#FFFFFF",
                               font=("Helvetica", 16, "bold"))
        title_label.place(x=150, y=10)

        self.chat_display = ScrolledText(root, state=tk.DISABLED, width=58, height=20, wrap=tk.WORD,
                                         bg="#23272A", fg="#FFFFFF", font=("Helvetica", 10), bd=0)
        self.chat_display.place(x=20, y=50)

        input_field = tk.Entry(root, width=40, bg="#3A3D41", fg="#FFFFFF", font=("Helvetica", 12),
                               insertbackground="white", bd=0)
        input_field.place(x=20, y=500)
        input_field.bind("<Return>", send_message)

        send_button = tk.Button(root, text="Send", command=send_message, bg="#7289DA", fg="#FFFFFF",
                                font=("Helvetica", 10, "bold"), activebackground="#5B6EAE", bd=0)
        send_button.place(x=420, y=495)

        exit_button = tk.Button(root, text="Exit", command=root.destroy, bg="#FF5555", fg="#FFFFFF",
                                font=("Helvetica", 10, "bold"), activebackground="#D64343", bd=0)
        exit_button.place(x=420, y=20)

        thread = threading.Thread(target=self.receive_messages, daemon=True)
        thread.start()

        root.mainloop()

    def start(self):
        self.connect()
        self.start_gui()

client = Client()
client.start()