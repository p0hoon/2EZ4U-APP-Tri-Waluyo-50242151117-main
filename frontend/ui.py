# ==============================================================================
# File: frontend/ui.py
# Antarmuka Desktop 2EZ4U Food Delivery (Integrasi M1, M2, & M3)
# ==============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
import time

from backend.m1_pesanan import Array, LinkList
from backend.m2_antrean import (
    Pesanan, QueueNaive, QueueCircular,
    ke_postfix, hitung, UndoRedoManager, baca_csv_pesanan
)
from backend.m3_laporan import (
    BATAS_INSERTION, insertion_sort, merge_sort, linear_search, binary_search
)


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        self.root.geometry("1150x740")
        self.root.minsize(980, 620)

        # Inisialisasi Struktur Data M1, M2, & M3
        self.data_master = []
        self.cache_oid_terurut = None
        self.waktu_bangun_cache_ms = 0.0

        self.arr = Array()
        self.ll = LinkList()
        self.q_naive = QueueNaive()
        self.q_circular = QueueCircular(capacity=32768)
        self.ur_mgr = UndoRedoManager(self.q_naive, self.q_circular)
        self.next_oid = 200001

        # Muat data awal
        self.muat_data()

        # Bangun Layout
        self._init_layout()
        self.buka_m3_sort("insertion")

    def muat_data(self):
        self.data_master = baca_csv_pesanan("data/pesanan.csv", limit=200000)
        self.cache_oid_terurut = None
        self.arr = Array()
        self.ll = LinkList()
        self.q_naive = QueueNaive()
        self.q_circular = QueueCircular(capacity=32768)

        for idx, p in enumerate(self.data_master):
            # Masukkan ke M1 (dibatasi 20.000 agar Linked List tetap responsif saat inisialisasi)
            if idx < 20000:
                self.arr.append(p)
                self.ll.append(p)
            # Masukkan pesanan berstatus ANTRE ke antrean M2
            if p.status == "ANTRE":
                self.q_naive.enqueue(p)
                self.q_circular.enqueue(p)

        # Jika tidak ada status ANTRE pada data dummy, isi dari 20.000 baris pertama
        if len(self.q_circular) == 0:
            for i in range(min(19850, len(self.data_master))):
                self.q_naive.enqueue(self.data_master[i])
                self.q_circular.enqueue(self.data_master[i])

    def _init_layout(self):
        # 1. Header di paling atas
        header = tk.Frame(self.root, bg="#203a43", height=38)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="  2EZ4U Food Delivery", fg="white", bg="#203a43", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, pady=6)

        # 2. Status Bar & Panel COMMAND di paling bawah (di-pack lebih dulu agar tidak tertutup)
        self.status_bar = tk.Label(self.root, text="[Ready] 0.00 ms", bg="#1b2a32", fg="white", font=("Courier", 9, "bold"), anchor="w", padx=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        bottom = tk.Frame(self.root, height=130, bg="#ebebeb")
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(bottom, text="COMMAND", anchor="w", font=("Courier", 8, "bold"), bg="#ebebeb", fg="#444").pack(fill=tk.X, padx=6, pady=(3, 0))
        self.txt_log = tk.Text(bottom, height=5, font=("Courier", 8), bg="white", fg="#222")
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)

        # 3. Body utama di tengah
        body = tk.Frame(self.root)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Sidebar
        canvas = tk.Canvas(body, width=245, bg="#f5f6f8", highlightthickness=0)
        scroll_sb = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        self.sidebar = tk.Frame(canvas, bg="#f5f6f8")
        self.sidebar.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.sidebar, anchor="nw", width=245)
        canvas.configure(yscrollcommand=scroll_sb.set)

        canvas.pack(side=tk.LEFT, fill=tk.Y)
        scroll_sb.pack(side=tk.LEFT, fill=tk.Y)

        # Area Konten Kanan
        self.main_area = tk.Frame(body, bg="white")
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_sidebar()

    def _build_sidebar(self):
        self._add_hdr("DATA")
        self._add_btn("Load", lambda: messagebox.showinfo("Data", f"Total baris dimuat: {len(self.data_master):,} pesanan."))

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

        self._add_hdr("M3 - SORT DAN SEARCH")
        self._add_btn("SORT - INSERTION SORT", lambda: self.buka_m3_sort("insertion"))
        self._add_btn("SORT - MERGE SORT", lambda: self.buka_m3_sort("merge"))
        self._add_btn("SEARCH - LINEAR SEARCH", lambda: self.buka_m3_search("linear"))
        self._add_btn("SEARCH - BINARY SEARCH", lambda: self.buka_m3_search("binary"))

    def _add_hdr(self, text):
        tk.Label(self.sidebar, text=text, bg="#e2e5ea", fg="#333", font=("Helvetica", 7, "bold"), anchor="w", padx=8, pady=3).pack(fill=tk.X, pady=(4, 1))

    def _add_btn(self, text, cmd):
        tk.Button(self.sidebar, text=text, anchor="w", relief=tk.FLAT, bg="#f5f6f8", activebackground="#dde3ea", font=("Helvetica", 8), padx=10, pady=2, command=cmd).pack(fill=tk.X)

    def _log(self, cmd_name, mod_name, ms, note=""):
        self.txt_log.insert("1.0", f"{cmd_name:<22} -> {mod_name:<20} {ms:>8.2f} ms   {note}\n")
        self.status_bar.config(text=f"[{mod_name}]  {ms:.2f} ms")

    def _clear_main(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    def _create_table(self, parent, cols=("#", "oid", "pelanggan", "resto", "menu", "masuk")):
        t_frame = tk.Frame(parent)
        t_frame.pack(fill=tk.BOTH, expand=True, pady=6)
        tree = ttk.Treeview(t_frame, columns=cols, show="headings", height=9)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110, anchor="center" if c in ("#", "oid", "harga", "masuk", "selesai", "langkah", "token") else "w")

        # Cek terlebih dahulu apakah kolom "#" ada
        if "#" in cols:
            tree.column("#", width=45, anchor="center")

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scr = ttk.Scrollbar(t_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scr.set)
        scr.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    # =========================================================================
    # MENU M3: SORT (INSERTION SORT & MERGE SORT)
    # =========================================================================
    def buka_m3_sort(self, jenis):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)

        judul = "Sort: insertion sort, O(n²)" if jenis == "insertion" else "Sort: merge sort, O(n log n)"
        sub = (
            "Setiap elemen digeser mundur sampai menemukan tempatnya. Sederhana, tetapi kerjanya tumbuh kuadratik."
            if jenis == "insertion" else
            "Larik dibelah dua terus-menerus, lalu potongan yang sudah terurut disatukan kembali."
        )
        tk.Label(p, text=judul, font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(p, text=sub, font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        form = tk.Frame(p, bg="white")
        form.pack(fill=tk.X, pady=4)

        # Kolom Jumlah Baris
        f_jml = tk.Frame(form, bg="white")
        f_jml.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(f_jml, text="Jumlah baris diurutkan", font=("Helvetica", 8, "bold"), bg="white").pack(anchor="w")
        ent_n = tk.Entry(f_jml, width=14, font=("Helvetica", 9))
        ent_n.insert(0, "10" if jenis == "insertion" else "4000")
        ent_n.pack(anchor="w", pady=2)
        tk.Label(f_jml, text="diambil dari awal data; coba 1.000 lalu 2.000 lalu 4.000", font=("Helvetica", 7), fg="#888", bg="white").pack(anchor="w")

        # Kolom Kunci Urut
        f_key = tk.Frame(form, bg="white")
        f_key.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(f_key, text="Diurutkan menurut", font=("Helvetica", 8, "bold"), bg="white").pack(anchor="w")
        cmb_key = ttk.Combobox(f_key, values=("oid", "harga", "selesai"), state="readonly", width=14)
        cmb_key.set("harga" if jenis == "insertion" else "oid")
        cmb_key.pack(anchor="w", pady=2)
        tk.Label(f_key, text="oid (teks), harga (angka), selesai (waktu selesai)", font=("Helvetica", 7), fg="#888", bg="white").pack(anchor="w")

        lbl_info = tk.Label(p, text="", font=("Helvetica", 9), bg="white", fg="#222", justify=tk.LEFT)
        lbl_info.pack(anchor="w", pady=4)

        tree = self._create_table(p, cols=("#", "oid", "harga", "selesai", "resto", "menu"))

        def aksi_urutkan():
            try:
                n_baris = int(ent_n.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Jumlah baris harus berupa angka!")
                return

            n_baris = min(n_baris, len(self.data_master))
            kunci = cmb_key.get()
            potongan = self.data_master[:n_baris]

            t0 = time.perf_counter()
            try:
                if jenis == "insertion":
                    hasil, comp, move = insertion_sort(potongan, kunci)
                    mod_tag = "M3 - insertion sort"
                    cmd_tag = "insertion_sort"
                else:
                    hasil, comp, move = merge_sort(potongan, kunci)
                    mod_tag = "M3 - merge sort"
                    cmd_tag = "merge_sort"
            except ValueError as err:
                lbl_info.config(text=str(err), fg="red")
                return

            ms = (time.perf_counter() - t0) * 1000
            lbl_info.config(
                text=f"{len(hasil):,} pesanan diurutkan menurut {kunci}.\n{comp:,} perbandingan, {move:,} pemindahan.".replace(",", "."),
                fg="#222"
            )

            for row in tree.get_children():
                tree.delete(row)
            # Tampilkan maksimal 200 baris teratas di tabel agar GUI tetap ringan
            for idx, it in enumerate(hasil[:200], 1):
                harga_fmt = f"{it.harga:,}".replace(",", ".")
                tree.insert("", tk.END, values=(idx, it.oid, harga_fmt, it.selesai, it.resto, it.menu))

            self._log(cmd_tag, mod_tag, ms)

        btn = tk.Button(form, text="URUTKAN", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=18, pady=4, command=aksi_urutkan)
        btn.pack(side=tk.LEFT, pady=8)
        aksi_urutkan()

    # =========================================================================
    # MENU M3: SEARCH (LINEAR SEARCH & BINARY SEARCH)
    # =========================================================================
    def buka_m3_search(self, jenis):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)

        judul = "Search: linear search, O(n)" if jenis == "linear" else "Search: binary search, O(log n)"
        sub = (
            "Memeriksa pesanan satu per satu dari depan. Tidak menuntut data terurut."
            if jenis == "linear" else
            "Membuang separuh sisa daftar pada setiap perbandingan. Menuntut daftar yang sudah terurut menurut oid."
        )
        tk.Label(p, text=judul, font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(p, text=sub, font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        form = tk.Frame(p, bg="white")
        form.pack(fill=tk.X, pady=4)

        f_in = tk.Frame(form, bg="white")
        f_in.pack(side=tk.LEFT, padx=(0, 15))
        tk.Label(f_in, text="Nomor pesanan (oid)", font=("Helvetica", 8, "bold"), bg="white").pack(anchor="w")
        ent_oid = tk.Entry(f_in, width=18, font=("Helvetica", 9))
        default_idx = min(137441, len(self.data_master) - 1)
        ent_oid.insert(0, self.data_master[default_idx].oid if self.data_master else "O-137442")
        ent_oid.pack(anchor="w", pady=2)
        tk.Label(f_in, text=f"format O-000001 sampai O-{len(self.data_master):06d}", font=("Helvetica", 7), fg="#888", bg="white").pack(anchor="w")

        lbl_info = tk.Label(p, text="", font=("Helvetica", 9), bg="white", fg="#222", justify=tk.LEFT)
        lbl_info.pack(anchor="w", pady=4)

        # Tabel Detail Kolom-Isi seperti di Panduan M3
        t_frame = tk.Frame(p)
        t_frame.pack(fill=tk.BOTH, expand=True, pady=6)
        tree = ttk.Treeview(t_frame, columns=("kolom", "isi"), show="headings", height=9)
        tree.heading("kolom", text="kolom")
        tree.heading("isi", text="isi")
        tree.column("kolom", width=180, anchor="w")
        tree.column("isi", width=450, anchor="w")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def aksi_cari():
            target = ent_oid.get().strip()
            if jenis == "linear":
                t0 = time.perf_counter()
                idx, comp = linear_search(self.data_master, target)
                ms = (time.perf_counter() - t0) * 1000
                item = self.data_master[idx] if idx != -1 else None

                if item:
                    lbl_info.config(text=f"Ditemukan pada indeks {idx:,}.\n{comp:,} perbandingan.".replace(",", "."))
                else:
                    lbl_info.config(text=f"Pesanan {target} tidak ditemukan.\n{comp:,} perbandingan.".replace(",", "."))
                self._log("linear_search", "M3 - linear search", ms)
            else:
                # Bangun daftar terurut oid sekali dengan merge sort bila belum ada
                if self.cache_oid_terurut is None:
                    t_build = time.perf_counter()
                    self.cache_oid_terurut, _, _ = merge_sort(self.data_master, "oid")
                    self.waktu_bangun_cache_ms = (time.perf_counter() - t_build) * 1000

                t0 = time.perf_counter()
                idx, comp = binary_search(self.cache_oid_terurut, target)
                ms = (time.perf_counter() - t0) * 1000
                item = self.cache_oid_terurut[idx] if idx != -1 else None

                info_build = f"Daftar terurut oid dibangun sekali dengan merge sort, {self.waktu_bangun_cache_ms:.2f} ms.\n"
                if item:
                    lbl_info.config(
                        text=info_build + f"Ditemukan pada baris ke-{idx + 1:,} dari {len(self.cache_oid_terurut):,} baris.\n{comp:,} perbandingan, bandingkan dengan linear search.".replace(",", ".")
                    )
                else:
                    lbl_info.config(text=info_build + f"Pesanan {target} tidak ditemukan ({comp} perbandingan).")
                self._log("binary_search", "M3 - binary search", ms)

            for row in tree.get_children():
                tree.delete(row)
            if item:
                detail = (
                    ("oid", item.oid),
                    ("pelanggan", item.pelanggan),
                    ("resto", item.resto),
                    ("menu", item.menu),
                    ("harga", f"{item.harga:,}".replace(",", ".")),
                    ("prioritas", str(item.prioritas)),
                    ("masuk", item.masuk),
                    ("selesai", item.selesai),
                    ("status", item.status),
                )
                for k_col, v_col in detail:
                    tree.insert("", tk.END, values=(k_col, v_col))

        btn = tk.Button(form, text="CARI", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=22, pady=4, command=aksi_cari)
        btn.pack(side=tk.LEFT, pady=8)
        aksi_cari()

    # =========================================================================
    # MENU M1 & M2 (TETAP AKTIF DAN TERINTEGRASI)
    # =========================================================================
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

        lbl = tk.Label(p, text=f"Total data M1: {len(self.arr):,} pesanan.", font=("Helvetica", 9), bg="white")
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

        lbl = tk.Label(p, text="", font=("Helvetica", 9), bg="white")
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

        lbl = tk.Label(p, text="", font=("Helvetica", 9), bg="white")
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

    def buka_m2_postfix(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Stack: hitung struk lewat postfix", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(p, text="Struk ditulis infix, lalu dihitung dua tahap: tahap 1 infix menjadi postfix, tahap 2 postfix dievaluasi.", font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        ent = tk.Entry(r, font=("Courier", 10))
        ent.insert(0, "( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        lbl = tk.Label(p, text="", font=("Courier", 9), justify=tk.LEFT, anchor="w", bg="#f9f9f9", relief=tk.GROOVE, padx=8, pady=6)
        lbl.pack(fill=tk.X, pady=5)

        tree = self._create_table(p, cols=("langkah", "token", "tindakan", "stack", "output"))
        tree.column("langkah", width=70, anchor="center")
        tree.column("token", width=65, anchor="center")
        tree.column("tindakan", width=220, anchor="w")
        tree.column("stack", width=130, anchor="w")
        tree.column("output", width=260, anchor="w")

        def aksi():
            expr = ent.get().strip()
            t0 = time.perf_counter()
            post, s_conv = ke_postfix(expr)
            tot, s_eval = hitung(post)
            ms = (time.perf_counter() - t0) * 1000
            lbl.config(text=f"Struk  : {expr}\nPostfix: {' '.join(post)}\nTOTAL  : Rp {tot:,.0f}".replace(",", "."))
            for item in tree.get_children():
                tree.delete(item)
            for s in s_conv:
                tree.insert("", tk.END, values=s)
            for s in s_eval:
                tree.insert("", tk.END, values=s)
            self._log("stack_postfix", "M2 - stack", ms)

        tk.Button(r, text="HITUNG", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=14, command=aksi).pack(side=tk.LEFT)
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