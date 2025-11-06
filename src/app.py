import tkinter as tk
from tkinter import ttk, messagebox
import threading, time
from .config import SETTINGS
from .channels import add_channel, remove_channel, list_channels
from .storage import tail_logs, add_log
from .service import SERVICE

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YT → TikTok Reup <10s — Multi-channel")
        self.geometry("880x600")
        self._build_ui()
        self._refresh_ui()
        self.after(1000, self._tick_logs)

    def _build_ui(self):
        frm = ttk.Frame(self); frm.pack(fill="both", expand=True, padx=10, pady=10)
        # row: input + add
        top = ttk.Frame(frm); top.pack(fill="x")
        self.inp = ttk.Entry(top); self.inp.pack(side="left", fill="x", expand=True)
        ttk.Button(top, text="Thêm kênh", command=self._add).pack(side="left", padx=6)
        ttk.Button(top, text="Xoá kênh đã chọn", command=self._del).pack(side="left")
        # channels table
        mid = ttk.Frame(frm); mid.pack(fill="both", expand=True, pady=(8,8))
        self.tree = ttk.Treeview(mid, columns=("cid","sub","last"), show="headings", height=12)
        for c,w in (("cid",420),("sub",120),("last",200)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, side="left")
        sb = ttk.Scrollbar(mid, command=self.tree.yview); sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        # controls
        ctrl = ttk.Frame(frm); ctrl.pack(fill="x")
        self.workers_var = tk.IntVar(value=SETTINGS.encode_workers)
        ttk.Label(ctrl, text="Workers:").pack(side="left")
        ttk.Spinbox(ctrl, from_=1, to=16, textvariable=self.workers_var, width=4).pack(side="left", padx=6)
        self.btn_start = ttk.Button(ctrl, text="Start dịch vụ", command=self._start)
        self.btn_start.pack(side="left", padx=6)
        ttk.Button(ctrl, text="Làm mới", command=self._refresh_ui).pack(side="left")
        ttk.Label(ctrl, text=f"Webhook: http://{SETTINGS.host}:{SETTINGS.port}/websub/callback").pack(side="right")
        # logs
        ttk.Label(frm, text="Logs:").pack(anchor="w")
        self.txt = tk.Text(frm, height=12)
        self.txt.pack(fill="both", expand=False)

    def _add(self):
        raw = self.inp.get().strip()
        if not raw: return
        try:
            meta = add_channel(raw)
            messagebox.showinfo("OK", f"Đã thêm: {meta['channel_id']}")
            self.inp.delete(0, "end")
            self._refresh_ui()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _del(self):
        sel = self.tree.selection()
        if not sel: return
        cid = self.tree.item(sel[0])["values"][0]
        remove_channel(cid)
        self._refresh_ui()

    def _start(self):
        try:
            SERVICE.start(self.workers_var.get())
            self.btn_start.configure(state="disabled", text="Đang chạy…")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _refresh_ui(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for ch in list_channels():
            sub = "subscribed" if ch.get("subscribed") else "not yet"
            last = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ch["last_seen"])) if ch.get("last_seen") else "-"
            self.tree.insert("", "end", values=(ch["channel_id"], sub, last))

    def _tick_logs(self):
        self.txt.delete("1.0","end")
        self.txt.insert("end", tail_logs(300))
        self.after(1500, self._tick_logs)

if __name__ == "__main__":
    App().mainloop()
