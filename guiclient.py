import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

HOST = "192.168.68.106"
PORT = 10000

class ChatClientGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chat Client")
        self.root.geometry("720x420")

        self.sock = None
        self.f_in = None
        self.f_out = None

        self.inbox = queue.Queue()
        self.running = False
        self.current_chat = None
        self.name = None

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.after(80, self._poll_inbox)

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Name:").pack(side="left")
        self.name_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.name_var, width=15).pack(side="left", padx=5)

        self.connect_btn = ttk.Button(top, text="Connect", command=self.connect)
        self.connect_btn.pack(side="left", padx=5)

        self.disconnect_btn = ttk.Button(top, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_btn.pack(side="left")

        ttk.Separator(self.root).pack(fill="x")

        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="y")

        ttk.Label(left, text="Online users").pack(anchor="w")
        self.users_list = tk.Listbox(left, height=18, width=18)
        self.users_list.pack(fill="y", expand=False, pady=5)

        btns = ttk.Frame(left)
        btns.pack(fill="x")
        self.refresh_btn = ttk.Button(btns, text="Refresh (LIST)", command=self.request_list, state="disabled")
        self.refresh_btn.pack(fill="x", pady=(0, 5))
        self.chat_btn = ttk.Button(btns, text="Chat (CHAT)", command=self.start_chat_with_selected, state="disabled")
        self.chat_btn.pack(fill="x")

        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self.chat_title = ttk.Label(right, text="Not connected", font=("Arial", 12, "bold"))
        self.chat_title.pack(anchor="w")

        self.chat_box = tk.Text(right, state="disabled", wrap="word")
        self.chat_box.pack(fill="both", expand=True, pady=5)

        bottom = ttk.Frame(right)
        bottom.pack(fill="x")

        self.msg_var = tk.StringVar()
        self.msg_entry = ttk.Entry(bottom, textvariable=self.msg_var)
        self.msg_entry.pack(side="left", fill="x", expand=True)
        self.msg_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ttk.Button(bottom, text="Send", command=self.send_message, state="disabled")
        self.send_btn.pack(side="left", padx=5)

    def connect(self):
        if self.running:
            return
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name cannot be empty")
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            self.f_in = self.sock.makefile("r", encoding="utf-8", newline="\n")
            self.f_out = self.sock.makefile("w", encoding="utf-8", newline="\n")
        except Exception as e:
            messagebox.showerror("Connection failed", str(e))
            self._cleanup()
            return

        self.name = name
        self.running = True
        threading.Thread(target=self._recv_loop, daemon=True).start()
        self._send_line(f"NAME {name}")

        self._ui_connected(True)
        self._append(f"[SYSTEM] Connected as {name}\n")
        self.request_list()

    def disconnect(self):
        if not self.running:
            return
        try:
            self._send_line("QUIT")
        except Exception:
            pass
        self._cleanup()
        self._ui_connected(False)
        self._append("[SYSTEM] Disconnected\n")

    def _cleanup(self):
        self.running = False
        self.current_chat = None
        try:
            if self.f_in: self.f_in.close()
        except Exception:
            pass
        try:
            if self.f_out: self.f_out.close()
        except Exception:
            pass
        try:
            if self.sock: self.sock.close()
        except Exception:
            pass
        self.sock = self.f_in = self.f_out = None

    def _send_line(self, line: str):
        if not self.f_out:
            return
        self.f_out.write(line + "\n")
        self.f_out.flush()

    def _recv_loop(self):

        try:
            while self.running and self.f_in:
                line = self.f_in.readline()
                if not line:
                    break
                self.inbox.put(line.strip())
        except Exception:
            pass
        finally:
            self.inbox.put("__DISCONNECT__")


    def request_list(self):
        if self.running:
            self._send_line("LIST")

    def start_chat_with_selected(self):
        sel = self.users_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a user first")
            return
        target = self.users_list.get(sel[0]).strip()
        if target == self.name:
            messagebox.showinfo("Info", "You can't chat with yourself")
            return
        self._send_line(f"CHAT {target}")

    def send_message(self):
        if not self.running:
            return
        text = self.msg_var.get().strip()
        if not text:
            return
        self.msg_var.set("")
        self._send_line(f"MSG {text}")
        if self.current_chat:
            self._append(f"[You → {self.current_chat}] {text}\n")
        else:
            self._append(f"[You] {text}\n")


    def _ui_connected(self, connected: bool):
        self.connect_btn.configure(state="disabled" if connected else "normal")
        self.disconnect_btn.configure(state="normal" if connected else "disabled")
        self.refresh_btn.configure(state="normal" if connected else "disabled")
        self.chat_btn.configure(state="normal" if connected else "disabled")
        self.send_btn.configure(state="normal" if connected else "disabled")
        self.chat_title.configure(text="Connected (no chat yet)" if connected else "Not connected")
        if not connected:
            self.users_list.delete(0, tk.END)

    def _append(self, text: str):
        self.chat_box.configure(state="normal")
        self.chat_box.insert(tk.END, text)
        self.chat_box.see(tk.END)
        self.chat_box.configure(state="disabled")

    def _poll_inbox(self):
        try:
            while True:
                msg = self.inbox.get_nowait()
                if msg == "__DISCONNECT__":
                    if self.running:
                        self._append("[SYSTEM] Server disconnected\n")
                    self._cleanup()
                    self._ui_connected(False)
                    break
                self._handle_server_line(msg)
        except queue.Empty:
            pass
        self.root.after(80, self._poll_inbox)

    def _handle_server_line(self, line: str):
        if line.startswith("OK "):
            rest = line[3:].strip()
            if " " in rest and not rest.lower().startswith(("registered", "chat", "sent", "bye")):
                names = rest.split()
                self.users_list.delete(0, tk.END)
                for n in names:
                    self.users_list.insert(tk.END, n)
            if rest.startswith("Chat connected with "):
                self.current_chat = rest.replace("Chat connected with ", "").strip()
                self.chat_title.configure(text=f"Chat with {self.current_chat}")
            self._append(f"[SERVER] {line}\n")
            return

        if line.startswith("INFO "):
            self._append(f"[INFO] {line[5:]}\n")
            return

        if line.startswith("ERR "):
            self._append(f"[ERROR] {line[4:]}\n")
            return

        if line.startswith("FROM "):
            parts = line.split(" ", 2)
            if len(parts) >= 3:
                sender = parts[1]
                text = parts[2]
                self.current_chat = sender
                self.chat_title.configure(text=f"Chat with {self.current_chat}")
                self._append(f"[{sender}] {text}\n")
            else:
                self._append(f"[RECV] {line}\n")
            return

        self._append(f"[RECV] {line}\n")

    def on_close(self):
        self.disconnect()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    app = ChatClientGUI(root)
    root.mainloop()