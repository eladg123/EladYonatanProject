import socket
import threading

HOST = "192.168.68.106"
PORT = 10000

clients = {}
chat_partner = {}
lock = threading.Lock()


def send_line(file_out, line: str):
    file_out.write(line + "\n")
    file_out.flush()


def safe_close(name: str):
    """Remove client and notify partner if needed."""
    with lock:
        info = clients.pop(name, None)
        partner = chat_partner.pop(name, None)
        if partner and chat_partner.get(partner) == name:
            chat_partner.pop(partner, None)
            partner_info = clients.get(partner)
            if partner_info:
                _, _, _, p_out = partner_info
                send_line(p_out, f"INFO {name} disconnected. Chat closed.")

    if info:
        conn, _, f_in, f_out = info
        try:
            f_in.close()
        except Exception:
            pass
        try:
            f_out.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def handle_client(conn: socket.socket, addr):
    f_in = conn.makefile("r", encoding="utf-8", newline="\n")
    f_out = conn.makefile("w", encoding="utf-8", newline="\n")

    send_line(f_out, "INFO Welcome. Please register: NAME <your_name>")

    name = None
    try:
        first = f_in.readline()
        if not first:
            return
        first = first.strip()

        if not first.startswith("NAME "):
            send_line(f_out, "ERR First command must be: NAME <your_name>")
            return

        requested = first[5:].strip()
        if not requested:
            send_line(f_out, "ERR Name cannot be empty")
            return

        with lock:
            if requested in clients:
                send_line(f_out, "ERR Name already taken")
                return
            name = requested
            clients[name] = (conn, addr, f_in, f_out)

        send_line(f_out, f"OK Registered as {name}")
        print(f"[+] {name} connected from {addr}")


        while True:
            line = f_in.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            if line == "LIST":
                with lock:
                    names = sorted(clients.keys())
                send_line(f_out, "OK " + " ".join(names))
                continue

            if line.startswith("CHAT "):
                target = line[5:].strip()
                if not target:
                    send_line(f_out, "ERR Usage: CHAT <name>")
                    continue

                with lock:
                    if target not in clients:
                        send_line(f_out, "ERR User not online")
                        continue
                    if target == name:
                        send_line(f_out, "ERR Cannot chat with yourself")
                        continue


                    chat_partner[name] = target
                    chat_partner[target] = name

                    _, _, _, t_out = clients[target]
                    send_line(t_out, f"INFO {name} started a chat with you. You are now connected.")

                send_line(f_out, f"OK Chat connected with {target}")
                continue

            if line.startswith("MSG "):
                msg = line[4:]
                with lock:
                    partner = chat_partner.get(name)
                    if not partner:
                        send_line(f_out, "ERR No active chat. Use CHAT <name> first.")
                        continue
                    partner_info = clients.get(partner)
                    if not partner_info:
                        send_line(f_out, "ERR Partner went offline.")
                        chat_partner.pop(name, None)
                        continue

                    _, _, _, p_out = partner_info
                    send_line(p_out, f"FROM {name} {msg}")

                send_line(f_out, "OK Sent")
                continue

            if line == "QUIT":
                send_line(f_out, "OK Bye")
                break

            send_line(f_out, "ERR Unknown command. Use LIST / CHAT / MSG / QUIT")

    except ConnectionResetError:
        pass
    finally:
        if name:
            print(f"[-] {name} disconnected")
            safe_close(name)
        else:
            try:
                f_in.close()
                f_out.close()
                conn.close()
            except Exception:
                pass


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = server_socket.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()


if __name__ == "__main__":
    start_server()
