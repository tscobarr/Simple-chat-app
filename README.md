# Encrypted Chat Application with Python (Client-Server)

This is a chat application built with Python, using socket programming for client-server communication. It features real-time encrypted messaging and a graphical user interface (GUI) implemented with Tkinter. The application now incorporates AES encryption for secure message transmission and Kyber key exchange for secure key establishment.

## Features
- Real-time encrypted messaging between multiple clients.
- AES encryption for securing message content.
- Kyber post-quantum cryptography for key exchange.
- User-friendly GUI for seamless interaction.
- Notifications when users join or leave the chat.
- Multi-client support with threaded connections.
- Messages can be sent using the Enter key or a "Send" button.

## Technologies Used
- Python:
  - Socket programming for network communication.
  - Tkinter for the graphical interface.
  - Cryptography libraries for AES encryption.
  - [kyber-py](https://github.com/GiacomoPope/kyber-py) for Kyber implementation.
- Threading for handling multiple clients concurrently.

## How It Works
1. **Server**:
   - Accepts connections from clients and manages the list of active users.
   - Facilitates secure key exchange using Kyber.
   - Broadcasts encrypted messages to all connected clients.
2. **Client**:
   - Connects to the server, performs a secure key exchange, and participates in the chat.
   - Encrypts outgoing messages with AES and decrypts incoming ones.
   - Provides a GUI for an enhanced user experience.

### Steps to Run
1. Clone this repository:
   ```bash
   git clone https://github.com/tscobarr/Simple-chat-app
   ```

2. Navigate to the project directory:
   ```bash
   cd secure-chat-application
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the server:
   ```bash
   python server.py
   ```

5. Start a client in a separate terminal or machine:
   ```bash
   python client.py
   ```

6. Enter a nickname when prompted and start chatting securely!

### Encryption Details
- **AES Encryption**:
  - Used for message confidentiality.
  - Ensures that messages remain private during transmission.
- **Kyber Key Exchange**:
  - Post-quantum cryptographic algorithm.
  - Establishes secure session keys resistant to quantum attacks.

### Stopping the Application
- To disconnect a client, close the client window.
- To stop the server, terminate the server terminal.

## Future Improvements
- Make our own implementation of kyber.

## Screenshots
![Chat Interface](https://i.ibb.co/2FWWTP5/img-chat-app.png)

## Acknowledgments
- [kyber-py](https://github.com/GiacomoPope/kyber-py) repository for the Kyber implementation.

Made By: [tscobarr](mailto:escobar.tomas2004@gmail.com)

**Free Software!**