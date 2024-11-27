import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# Configuración del cliente
HOST = '127.0.0.1'
PORT = 55555

nickname = input("Choose a nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    """Recibe mensajes del servidor y los muestra en la UI."""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                chat_display.config(state=tk.NORMAL)
                chat_display.insert(tk.END, f"{message}\n")
                chat_display.config(state=tk.DISABLED)
                chat_display.see(tk.END)
        except:
            print("An error occurred!")
            client.close()
            break

def send_message(event=None):
    """Envía el mensaje escrito por el usuario."""
    message = input_field.get()
    if message:
        formatted_message = f"{nickname}: {message}"
        client.send(formatted_message.encode('utf-8'))
        input_field.delete(0, tk.END)  # Limpia el campo de entrada

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Chat App")
root.geometry("500x600")
root.resizable(False, False)

# Fondo con un gradiente simulado
canvas = tk.Canvas(root, width=500, height=600)
canvas.pack(fill="both", expand=True)
canvas.create_rectangle(0, 0, 500, 600, fill="#2C2F33", outline="")  # Fondo oscuro

# Título de la ventana
title_label = tk.Label(root, text="Chat Application", bg="#2C2F33", fg="#FFFFFF",
                       font=("Helvetica", 16, "bold"))
title_label.place(x=150, y=10)

# Cuadro de texto para mostrar mensajes
chat_display = ScrolledText(root, state=tk.DISABLED, width=58, height=20, wrap=tk.WORD,
                             bg="#23272A", fg="#FFFFFF", font=("Helvetica", 10), bd=0)
chat_display.place(x=20, y=50)

# Campo de entrada para escribir mensajes (con fondo más claro)
input_field = tk.Entry(root, width=40, bg="#3A3D41", fg="#FFFFFF", font=("Helvetica", 12),
                        insertbackground="white", bd=0)
input_field.place(x=20, y=500)
input_field.bind("<Return>", send_message)  # Vincula la tecla Enter con el envío de mensajes

# Botón para enviar mensajes
send_button = tk.Button(root, text="Send", command=send_message, bg="#7289DA", fg="#FFFFFF",
                         font=("Helvetica", 10, "bold"), activebackground="#5B6EAE", bd=0)
send_button.place(x=420, y=495)

# Botón de cierre elegante
exit_button = tk.Button(root, text="Exit", command=root.destroy, bg="#FF5555", fg="#FFFFFF",
                         font=("Helvetica", 10, "bold"), activebackground="#D64343", bd=0)
exit_button.place(x=420, y=20)

# Inicia el hilo de recepción
receive_thread = threading.Thread(target=receive)
receive_thread.daemon = True
receive_thread.start()

# Inicia la interfaz gráfica
root.mainloop()