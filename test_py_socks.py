import socket
import select
import threading

def handle_client(client_sock):
    try:
        # Handshake
        ver, nmethods = client_sock.recv(2)
        methods = client_sock.recv(nmethods)
        client_sock.sendall(b"\x05\x00") # No auth
        
        # Request
        ver, cmd, _, atyp = client_sock.recv(4)
        if cmd != 1: # CONNECT
            client_sock.close()
            return
            
        if atyp == 1: # IPv4
            dest_addr = socket.inet_ntoa(client_sock.recv(4))
        elif atyp == 3: # Domain
            addr_len = client_sock.recv(1)[0]
            dest_addr = client_sock.recv(addr_len).decode('utf-8')
        elif atyp == 4: # IPv6
            dest_addr = socket.inet_ntop(socket.AF_INET6, client_sock.recv(16))
        else:
            client_sock.close()
            return
            
        port_bytes = client_sock.recv(2)
        dest_port = int.from_bytes(port_bytes, 'big')
        
        # Connect to remote
        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_sock.settimeout(10)
        remote_sock.connect((dest_addr, dest_port))
        
        # Reply success
        client_sock.sendall(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")
        
        # Relay
        sockets = [client_sock, remote_sock]
        while True:
            r, _, _ = select.select(sockets, [], [], 30)
            if not r:
                break
            for s in r:
                data = s.recv(8192)
                if not data:
                    return
                if s is client_sock:
                    remote_sock.sendall(data)
                else:
                    client_sock.sendall(data)
    except Exception:
        pass
    finally:
        client_sock.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 10888))
    server.listen(128)
    print("SOCKS5 listening on 127.0.0.1:10888")
    while True:
        client, _ = server.accept()
        t = threading.Thread(target=handle_client, args=(client,), daemon=True)
        t.start()

if __name__ == "__main__":
    main()
