import tkinter as tk
from tkinter import ttk, messagebox
import time

from backend.m1_pesanan import Array, LinkList
from backend.m2_antrean import (
    Pesanan, QueueNaive, QueueCircular, 
    ke_postfix, hitung, UndoRedoManager, baca_csv_pesanan
)

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        # Perbaikan format geometry (1150x740 bukan koma)
        self.root.geometry("1150x740")
        self.root.minsize(980, 620)

        # Inisialisasi Struktur Data M1 & M2
        self.arr = Array()
        self.ll = LinkList()
        self.q_naive = QueueNaive()
        self.q_circular = QueueCircular(capacity=32768)
        self.ur_mgr = UndoRedoManager(self.q_naive, self.q_circular)
        self.next_oid = 200001

        # Muat 19.850 data awal
        self.muat_data(19850)

        # Layout GUI
        self._init_layout()
        self.buka_m2_postfix()

    def muat_data(self, batas=20000):
        data_list = baca_csv_pesanan("data/pesanan.csv", limit=batas)
        for p in data_list:
            self.arr.append(p)
            self.ll.append(p)
            self.q_naive.enqueue(p)
            self.q_circular.enqueue(p)

    def _init_layout(self):
        # Header
        header = tk.Frame(self.root, bg="#203a43", height=38)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="  2EZ4U Food Delivery", fg="white", bg="#203a43", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, pady=6)

        # Body
        body = tk.Frame(self.root)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Sidebar Menu
        canvas = tk.Canvas(body, width=245, bg="#f5f6f8", highlightthickness=0)
        scroll_sb = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        self.sidebar = tk.Frame(canvas, bg="#f5f6f8")
        self.sidebar.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.sidebar, anchor="nw", width=245)
        canvas.configure(yscrollcommand=scroll_sb.set)

        canvas.pack(side=tk.LEFT, fill=tk.Y)
        scroll_sb.pack(side=tk.LEFT, fill=tk.Y)

        # Main Area
        self.main_area = tk.Frame(body, bg="white")
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bottom Command Log & Status
        bottom = tk.Frame(self.root, height=130, bg="#ebebeb")
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(bottom, text="COMMAND LOG", anchor="w", font=("Courier", 8, "bold"), bg="#ebebeb", fg="#444").pack(fill=tk.X, padx=6, pady=(3, 0))
        self.txt_log = tk.Text(bottom, height=5, font=("Courier", 8), bg="white", fg="#222")
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)

        self.status_bar = tk.Label(self.root, text="[Ready] 0.00 ms", bg="#1b2a32", fg="white", font=("Courier", 9, "bold"), anchor="w", padx=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self._build_sidebar()

    def _build_sidebar(self):
        self._add_hdr("DATA")
        self._add_btn("Load CSV Data", lambda: messagebox.showinfo("Info Data", f"Berhasil memuat data: {len(self.arr):,} baris."))

        self._add_hdr("M1 - DATA PESANAN")
        self._add_btn("ARRAY - LIHAT PESANAN", lambda: self.buka_m1_lihat("array"))
        self._add_btn("ARRAY - TAMBAH PESANAN REGULER", lambda: self.buka_m1_tambah("array", "REGULER"))
        self._add_btn("ARRAY - TAMBAH PESANAN PRIORITAS", lambda: self.buka_m1_tambah("array", "PRIORITAS"))
        self._add_btn("ARRAY - TAMBAH PESANAN VIP", lambda: self.buka_m1_tambah("array", "VIP"))
        self._add_btn("ARRAY - HAPUS PESANAN", lambda: self.buka_m1_hapus("array"))

        self._add_btn("LINKEDLIST - LIHAT PESANAN", lambda: self.buka_m1_lihat("ll"))
        self._add_btn("LINKEDLIST - TAMBAH PESANAN REGULER", lambda: self.buka_m1_tambah("ll", "REGULER"))
        self._add_btn("LINKEDLIST - TAMBAH PESANAN PRIORITAS", lambda: self.buka_m1_tambah("ll", "PRIORITAS"))
        self._add_btn("LINKEDLIST - TAMBAH PESANAN VIP", lambda: self.buka_m1_tambah("ll", "VIP"))
        self._add_btn("LINKEDLIST - HAPUS PESANAN", lambda: self.buka_m1_hapus("ll"))

        self._add_hdr("M2 - STACK DAN QUEUE")
        self._add_btn("STACK - POSTFIX (MESIN KASIR)", self.buka_m2_postfix)
        self._add_btn("STACK - UNDO", self.buka_m2_undo)
        self._add_btn("STACK - REDO", self.buka_m2_redo)
        self._add_btn("QUEUE - ENQUEUE", self.buka_m2_enqueue)
        self._add_btn("QUEUE - DEQUEUE NAIF", self.buka_m2_dequeue_naive)
        self._add_btn("QUEUE - DEQUEUE CIRCULAR", self.buka_m2_dequeue_circular)

    def _add_hdr(self, text):
        tk.Label(self.sidebar, text=text, bg="#e2e5ea", fg="#333", font=("Helvetica", 7, "bold"), anchor="w", padx=8, pady=3).pack(fill=tk.X, pady=(4, 1))

    def _add_btn(self, text, cmd):
        tk.Button(self.sidebar, text=text, anchor="w", relief=tk.FLAT, bg="#f5f6f8", activebackground="#dde3ea", font=("Helvetica", 8), padx=10, pady=2, command=cmd).pack(fill=tk.X)

    def _log(self, cmd_name, mod_name, ms, note=""):
        self.txt_log.insert(tk.END, f"{cmd_name:<26} -> {mod_name:<18} {ms:>8.2f} ms   {note}\n")
        self.txt_log.see(tk.END)
        self.status_bar.config(text=f"[{mod_name}]  {ms:.2f} ms")

    def _clear_main(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    def _create_table(self, parent):
        t_frame = tk.Frame(parent)
        t_frame.pack(fill=tk.BOTH, expand=True, pady=6)
        cols = ("#", "oid", "pelanggan", "resto", "menu", "masuk")
        tree = ttk.Treeview(t_frame, columns=cols, show="headings", height=8)
        for c in cols:
            tree.heading(c, text=c.upper())
        tree.column("#", width=40, anchor="center")
        tree.column("oid", width=95, anchor="center")
        tree.column("masuk", width=100, anchor="center")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scr = ttk.Scrollbar(t_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scr.set)
        scr.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    # ================= M1 UI =================
    def buka_m1_lihat(self, struktur):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        nama = "Array" if struktur == "array" else "Linked List"
        tk.Label(p, text=f"{nama}: Lihat Pesanan ke-i", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        tk.Label(r, text="Indeks ke-i:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 6))
        ent = tk.Entry(r, width=10)
        ent.insert(0, str(len(self.arr) // 2))
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text=f"Total data: {len(self.arr):,} pesanan.", font=("Helvetica", 9), bg="white")
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            idx = int(ent.get().strip())
            t0 = time.perf_counter()
            item = self.arr.get(idx) if struktur == "array" else self.ll.get(idx)
            ms = (time.perf_counter() - t0) * 1000
            self._log(f"{struktur}_lihat", f"M1 - {struktur}", ms, f"idx {idx}")
            lbl.config(text=f"Akses indeks [{idx}] selesai dalam {ms:.4f} ms.")
            for row in tree.get_children(): tree.delete(row)
            tree.insert("", tk.END, values=(idx, item.oid, item.pelanggan, item.resto, item.menu, item.masuk))

        tk.Button(r, text="LIHAT PESANAN", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), command=aksi).pack(side=tk.LEFT)

    def buka_m1_tambah(self, struktur, jenis):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        nama = "Array" if struktur == "array" else "Linked List"
        tk.Label(p, text=f"{nama}: Tambah Pesanan {jenis}", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        tk.Label(r, text="Nama Pelanggan:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 6))
        ent = tk.Entry(r, width=20)
        ent.insert(0, f"Pelanggan-{jenis}")
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text=f"Total pesanan {nama}: {len(self.arr if struktur == 'array' else self.ll):,}.", font=("Helvetica", 9), bg="white")
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            oid = f"O-{self.next_oid}"
            self.next_oid += 1
            baru = Pesanan(oid, ent.get().strip())
            t0 = time.perf_counter()
            target = self.arr if struktur == "array" else self.ll
            if jenis == "REGULER": target.tambah_reguler(baru)
            elif jenis == "PRIORITAS": target.tambah_prioritas(baru)
            else: target.tambah_vip(baru)
            ms = (time.perf_counter() - t0) * 1000
            self._log(f"{struktur}_{jenis.lower()}", f"M1 - {struktur}", ms)
            lbl.config(text=f"Ditambahkan {oid} ({jenis}). Panjang sekarang: {len(target):,}.")
            for row in tree.get_children(): tree.delete(row)
            tree.insert("", tk.END, values=(1, baru.oid, baru.pelanggan, baru.resto, baru.menu, baru.masuk))

        tk.Button(r, text=f"TAMBAH {jenis}", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), command=aksi).pack(side=tk.LEFT)

    def buka_m1_hapus(self, struktur):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        nama = "Array" if struktur == "array" else "Linked List"
        tk.Label(p, text=f"{nama}: Hapus Pesanan ke-i", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        tk.Label(r, text="Indeks yang dihapus:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 6))
        ent = tk.Entry(r, width=10)
        ent.insert(0, "0")
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text=f"Total pesanan: {len(self.arr if struktur == 'array' else self.ll):,}.", font=("Helvetica", 9), bg="white")
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            idx = int(ent.get().strip())
            t0 = time.perf_counter()
            terhapus = self.arr.delete(idx) if struktur == "array" else self.ll.delete(idx)
            ms = (time.perf_counter() - t0) * 1000
            self._log(f"{struktur}_hapus", f"M1 - {struktur}", ms, f"idx {idx}")
            lbl.config(text=f"Dihapus {terhapus.oid}. Sisa elemen: {len(self.arr if struktur == 'array' else self.ll):,}.")
            for row in tree.get_children(): tree.delete(row)
            tree.insert("", tk.END, values=(idx, terhapus.oid, terhapus.pelanggan, terhapus.resto, terhapus.menu, terhapus.masuk))

        tk.Button(r, text="HAPUS PESANAN", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), command=aksi).pack(side=tk.LEFT)

    # ================= M2 UI =================
    def buka_m2_postfix(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Stack: hitung struk lewat postfix", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        ent = tk.Entry(r, font=("Courier", 10))
        ent.insert(0, "( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        lbl = tk.Label(p, text="", font=("Courier", 9), justify=tk.LEFT, bg="#f9f9f9", relief=tk.GROOVE, padx=8, pady=4)
        lbl.pack(fill=tk.X, pady=5)

        t_frame = tk.Frame(p)
        t_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        cols = ("langkah", "token", "tindakan", "stack", "output")
        tree = ttk.Treeview(t_frame, columns=cols, show="headings", height=9)
        for c in cols: tree.heading(c, text=c.capitalize())
        tree.column("langkah", width=65, anchor="center")
        tree.column("token", width=60, anchor="center")
        tree.column("tindakan", width=230)
        tree.column("stack", width=120)
        tree.column("output", width=240)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def aksi():
            expr = ent.get().strip()
            t0 = time.perf_counter()
            post, s_conv = ke_postfix(expr)
            tot, s_eval = hitung(post)
            ms = (time.perf_counter() - t0) * 1000
            lbl.config(text=f"Struk  : {expr}\nPostfix: {' '.join(post)}\nTOTAL  : Rp {tot:,.0f}".replace(",", "."))
            for item in tree.get_children(): tree.delete(item)
            for s in s_conv: tree.insert("", tk.END, values=s)
            for s in s_eval: tree.insert("", tk.END, values=s)
            self._log("stack_postfix", "M2 - stack", ms)

        tk.Button(r, text="HITUNG", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), command=aksi).pack(side=tk.LEFT)
        aksi()

    def buka_m2_enqueue(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Queue: pesanan baru masuk ke belakang", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        ent = tk.Entry(r, width=18)
        ent.insert(0, f"X{len(self.q_circular) + 1}")
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text=f"Panjang antrean: Naif {len(self.q_naive):,}, Circular {len(self.q_circular):,}.", font=("Helvetica", 9), bg="white")
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            oid = f"O-{self.next_oid}"
            self.next_oid += 1
            baru = Pesanan(oid, ent.get().strip())
            t0 = time.perf_counter()
            self.q_naive.enqueue(baru)
            self.q_circular.enqueue(baru)
            self.ur_mgr.catat_aksi("ENQUEUE", [baru])
            ms = (time.perf_counter() - t0) * 1000
            self._log("queue_enqueue", "M2 - queue", ms)
            lbl.config(text=f"{oid} masuk ke barisan belakang KEDUA antrean.\nPanjang sekarang: Naif {len(self.q_naive):,}, Circular {len(self.q_circular):,}.")
            for row in tree.get_children(): tree.delete(row)
            tree.insert("", tk.END, values=(1, baru.oid, baru.pelanggan, baru.resto, baru.menu, baru.masuk))

        tk.Button(r, text="ENQUEUE", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), command=aksi).pack(side=tk.LEFT)

    def buka_m2_dequeue_naive(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Queue naif: ambil dari depan dengan menggeser isi", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        ent = tk.Entry(r, width=8)
        ent.insert(0, "2")
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text=f"Sisa antrean naif: {len(self.q_naive):,}.", font=("Helvetica", 9), bg="white", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            k = int(ent.get().strip())
            keluar = []
            geser_sebelum = self.q_naive.total_geseran
            t0 = time.perf_counter()
            for _ in range(k):
                x = self.q_naive.dequeue()
                self.q_circular.dequeue()
                if x: keluar.append(x)
            ms = (time.perf_counter() - t0) * 1000
            if keluar: self.ur_mgr.catat_aksi("DEQUEUE", keluar)
            geser = self.q_naive.total_geseran - geser_sebelum
            rata = geser // len(keluar) if keluar else 0
            lbl.config(text=f"{len(keluar)} pesanan keluar.\nTotal {geser:,} elemen digeser (rata-rata {rata:,} per layanan).\nSisa antrean: {len(self.q_naive):,}.")
            for row in tree.get_children(): tree.delete(row)
            for i, it in enumerate(keluar, 1): tree.insert("", tk.END, values=(i, it.oid, it.pelanggan, it.resto, it.menu, it.masuk))
            self._log("queue_dequeue_naive", "M2 - queue naif", ms)

        tk.Button(r, text="DEQUEUE", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), command=aksi).pack(side=tk.LEFT)

    def buka_m2_dequeue_circular(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Queue circular: ambil dari depan dengan memajukan penunjuk", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        ent = tk.Entry(r, width=8)
        ent.insert(0, "2")
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text=f"Sisa antrean circular: {len(self.q_circular):,}.", font=("Helvetica", 9), bg="white", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            k = int(ent.get().strip())
            keluar = []
            t0 = time.perf_counter()
            for _ in range(k):
                x = self.q_circular.dequeue()
                self.q_naive.dequeue()
                if x: keluar.append(x)
            ms = (time.perf_counter() - t0) * 1000
            if keluar: self.ur_mgr.catat_aksi("DEQUEUE", keluar)
            lbl.config(text=f"{len(keluar)} pesanan keluar dari antrean circular.\nTidak ada elemen yang digeser (front: {self.q_circular.front}, rear: {self.q_circular.rear}).\nSisa antrean: {len(self.q_circular):,}.")
            for row in tree.get_children(): tree.delete(row)
            for i, it in enumerate(keluar, 1): tree.insert("", tk.END, values=(i, it.oid, it.pelanggan, it.resto, it.menu, it.masuk))
            self._log("queue_dequeue_circular", "M2 - queue circular", ms)

        tk.Button(r, text="DEQUEUE", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), command=aksi).pack(side=tk.LEFT)

    def buka_m2_undo(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Stack: batalkan aksi antrean terakhir", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")

        lbl = tk.Label(p, text=f"Panjang antrean: {len(self.q_circular):,}. Undo stack: {self.ur_mgr.undo_stack.size()}.", font=("Helvetica", 9), bg="white")
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            t0 = time.perf_counter()
            res = self.ur_mgr.undo_last()
            ms = (time.perf_counter() - t0) * 1000
            if not res:
                lbl.config(text="Undo stack kosong!")
                return
            tipe, items = res
            lbl.config(text=f"Undo {tipe} berhasil. Panjang antrean sekarang: {len(self.q_circular):,}.")
            for row in tree.get_children(): tree.delete(row)
            for i, it in enumerate(items, 1): tree.insert("", tk.END, values=(i, it.oid, it.pelanggan, it.resto, it.menu, it.masuk))
            self._log("stack_undo", "M2 - stack", ms)

        tk.Button(p, text="UNDO", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), command=aksi).pack(anchor="w", pady=4)

    def buka_m2_redo(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Stack: kerjakan lagi aksi yang dibatalkan", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")

        lbl = tk.Label(p, text=f"Panjang antrean: {len(self.q_circular):,}. Redo stack: {self.ur_mgr.redo_stack.size()}.", font=("Helvetica", 9), bg="white")
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            t0 = time.perf_counter()
            res = self.ur_mgr.redo_last()
            ms = (time.perf_counter() - t0) * 1000
            if not res:
                lbl.config(text="Redo stack kosong!")
                return
            tipe, items = res
            lbl.config(text=f"Redo {tipe} berhasil. Panjang antrean sekarang: {len(self.q_circular):,}.")
            for row in tree.get_children(): tree.delete(row)
            for i, it in enumerate(items, 1): tree.insert("", tk.END, values=(i, it.oid, it.pelanggan, it.resto, it.menu, it.masuk))
            self._log("stack_redo", "M2 - stack", ms)

        tk.Button(p, text="REDO", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), command=aksi).pack(anchor="w", pady=4)
