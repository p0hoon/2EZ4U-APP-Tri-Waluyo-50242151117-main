import tkinter as tk
from tkinter import ttk, messagebox
import time

from backend.m1_pesanan import Array, LinkList
from backend.m2_antrean import (
    Pesanan, QueueNaive, QueueCircular,
    ke_postfix, hitung, UndoRedoManager, baca_csv_pesanan
)
from backend.m3_laporan import (
    insertion_sort, merge_sort, linear_search, binary_search
)

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        self.root.geometry("1150x740")
        self.root.minsize(980, 620)

        self.data_master = []
        self.cache_oid_terurut = None
        self.waktu_bangun_cache_ms = 0.0

        self.arr = Array()
        self.ll = LinkList()
        self.q_naive = QueueNaive()
        self.q_circular = QueueCircular(capacity=32768)
        self.ur_mgr = UndoRedoManager(self.q_naive, self.q_circular, self.arr, self.ll)

        self.next_oid = 200001
        self.last_added_oid = None
        self.last_view_idx = 0

        # Muat seluruh data CSV awal
        self.muat_data()

        # Bangun Layout GUI
        self._init_layout()
        self.buka_m1_lihat("array")

    def muat_data(self):
        """Memuat seluruh baris data/pesanan.csv ke M1, M2, dan M3."""
        self.data_master = baca_csv_pesanan("data/pesanan.csv", limit=200000)
        self.cache_oid_terurut = None
        self.arr = Array()
        self.ll = LinkList()
        self.q_naive = QueueNaive()
        self.q_circular = QueueCircular(capacity=32768)
        self.ur_mgr = UndoRedoManager(self.q_naive, self.q_circular, self.arr, self.ll)

        for p in self.data_master:
            self.arr.append(p)
            self.ll.append(p)
            if p.status == "ANTRE":
                self.q_naive.enqueue(p)
                self.q_circular.enqueue(p)

        if len(self.q_circular) == 0:
            for i in range(min(19850, len(self.data_master))):
                self.q_naive.enqueue(self.data_master[i])
                self.q_circular.enqueue(self.data_master[i])

        self.next_oid = len(self.data_master) + 1
        self.last_added_oid = None
        self.last_view_idx = 0

    def _sinkronkan_data_master(self):
        """Menyinkronkan data_master M3 dengan isi Array M1 terkini."""
        self.data_master = self.arr.data[:self.arr.size]
        self.cache_oid_terurut = None

    def _init_layout(self):
        # 1. Header Atas
        header = tk.Frame(self.root, bg="#203a43", height=38)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="  2EZ4U Food Delivery", fg="white", bg="#203a43", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, pady=6)

        # 2. Status Bar & Panel COMMAND Bawah
        self.status_bar = tk.Label(self.root, text="[Ready] 0.00 ms", bg="#1b2a32", fg="white", font=("Courier", 9, "bold"), anchor="w", padx=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        bottom = tk.Frame(self.root, height=130, bg="#ebebeb")
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(bottom, text="COMMAND", anchor="w", font=("Courier", 8, "bold"), bg="#ebebeb", fg="#444").pack(fill=tk.X, padx=6, pady=(3, 0))
        self.txt_log = tk.Text(bottom, height=5, font=("Courier", 8), bg="white", fg="#222")
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)

        # 3. Body Tengah
        body = tk.Frame(self.root)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(body, width=245, bg="#f5f6f8", highlightthickness=0)
        scroll_sb = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        self.sidebar = tk.Frame(canvas, bg="#f5f6f8")
        self.sidebar.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.sidebar, anchor="nw", width=245)
        canvas.configure(yscrollcommand=scroll_sb.set)

        canvas.pack(side=tk.LEFT, fill=tk.Y)
        scroll_sb.pack(side=tk.LEFT, fill=tk.Y)

        self.main_area = tk.Frame(body, bg="white")
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_sidebar()

    def _build_sidebar(self):
        self._add_hdr("DATA")
        self._add_btn("Load", self.buka_menu_load)

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

    def _create_table(self, parent, cols=("#", "oid", "pelanggan", "resto", "menu", "harga", "prioritas", "masuk", "status")):
        t_frame = tk.Frame(parent)
        t_frame.pack(fill=tk.BOTH, expand=True, pady=6)
        tree = ttk.Treeview(t_frame, columns=cols, show="headings", height=9)
        for c in cols:
            tree.heading(c, text=c)
            lebar = 95 if c in ("oid", "harga", "masuk", "selesai", "status") else 130
            if c in ("#", "prioritas", "langkah", "token"):
                lebar = 55
            align = "center" if c in ("#", "oid", "harga", "prioritas", "masuk", "selesai", "status", "langkah", "token") else "w"
            tree.column(c, width=lebar, anchor=align)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scr = ttk.Scrollbar(t_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scr.set)
        scr.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    def _isi_tabel_pesanan_list(self, tree, daftar_pesanan, nomor_awal=1):
        """Mengisi tabel Treeview dari list objek Pesanan."""
        for row in tree.get_children():
            tree.delete(row)
        for idx, it in enumerate(daftar_pesanan, nomor_awal):
            if it is None:
                continue
            hrg_str = f"{it.harga:,}".replace(",", ".")
            tree.insert("", tk.END, values=(idx, it.oid, it.pelanggan, it.resto, it.menu, hrg_str, it.prioritas, it.masuk, it.status))

    def _isi_tabel_m1(self, tree, struktur, mulai_idx=0, batas=50):
        """Menampilkan potongan baris dari Array atau Linked List M1 ke tabel."""
        target = self.arr if struktur == "array" else self.ll
        total = len(target)
        if total == 0:
            for row in tree.get_children():
                tree.delete(row)
            return

        mulai_idx = max(0, min(mulai_idx, total - 1))
        akhir_idx = min(total, mulai_idx + batas)
        potongan = []

        if struktur == "array":
            for i in range(mulai_idx, akhir_idx):
                potongan.append(self.arr.get(i))
        else:
            curr = self.ll.head
            for _ in range(mulai_idx):
                if curr is None:
                    break
                curr = curr.next
            for _ in range(mulai_idx, akhir_idx):
                if curr is None:
                    break
                potongan.append(curr.data)
                curr = curr.next

        self._isi_tabel_pesanan_list(tree, potongan, nomor_awal=mulai_idx)


    # DATA: LOAD CSV
    def buka_menu_load(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)

        tk.Label(p, text="Data: Status & Muat Ulang Dataset CSV (pesanan.csv)", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        lbl = tk.Label(p, text="", font=("Helvetica", 9), bg="white", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)

        def aksi_reset():
            t0 = time.perf_counter()
            self.muat_data()
            ms = (time.perf_counter() - t0) * 1000
            lbl.config(text=f"Dataset di-reset ulang dari data/pesanan.csv: {len(self.data_master):,} baris.\nArray M1: {len(self.arr):,} | Linked List M1: {len(self.ll):,} | Queue M2 (ANTRE): {len(self.q_circular):,}".replace(",", "."))
            self._isi_tabel_m1(tree, "array", 0, 100)
            self._log("load_csv", "DATA - load", ms, f"{len(self.data_master):,} baris")

        tk.Button(p, text="RESET / MUAT ULANG DARI CSV", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=14, command=aksi_reset).pack(anchor="w", pady=4)
        tree = self._create_table(p)

        lbl.config(
            text=f"Dataset aktif saat ini: {len(self.data_master):,} baris.\n"
                 f"Array M1: {len(self.arr):,} | Linked List M1: {len(self.ll):,} | Queue M2 (ANTRE): {len(self.q_circular):,} | Tumpukan Undo: {self.ur_mgr.undo_stack.size()}".replace(",", ".")
        )
        self._isi_tabel_m1(tree, "array", 0, 100)

   
    # M1: LIHAT, TAMBAH (REGULER/PRIORITAS/VIP), & HAPUS PESANAN
    def buka_m1_lihat(self, struktur):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        nama = "Array" if struktur == "array" else "Linked List"
        komp = "O(1) akses langsung" if struktur == "array" else "O(n) telusur simpul"

        tk.Label(p, text=f"{nama}: Lihat Pesanan ke-i ({komp})", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(p, text="Membuka detail pesanan pada indeks ke-i beserta daftar antrean terkini.", font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        tk.Label(r, text="Indeks ke-i:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 6))
        ent = tk.Entry(r, width=12, font=("Helvetica", 9))
        target_obj = self.arr if struktur == "array" else self.ll
        default_idx = min(self.last_view_idx, max(0, len(target_obj) - 1))
        ent.insert(0, str(default_idx))
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text="", font=("Helvetica", 9), bg="white", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            try:
                idx = int(ent.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Indeks harus berupa angka bulat!")
                return

            if idx < 0 or idx >= len(target_obj):
                messagebox.showerror("Error", f"Indeks harus antara 0 sampai {len(target_obj) - 1}!")
                return

            self.last_view_idx = idx
            t0 = time.perf_counter()
            item = self.arr.get(idx) if struktur == "array" else self.ll.get(idx)
            ms = (time.perf_counter() - t0) * 1000

            self._log(f"{struktur}_lihat", f"M1 - {struktur}", ms, f"idx {idx}")
            lbl.config(
                text=f"Ditemukan indeks [{idx:,}] -> OID: {item.oid} | Pelanggan: {item.pelanggan} | Menu: {item.menu} (Rp {item.harga:,})\n"
                     f"Total antrean {nama}: {len(target_obj):,} pesanan. Waktu akses: {ms:.4f} ms.".replace(",", ".")
            )
            self._isi_tabel_m1(tree, struktur, mulai_idx=idx, batas=50)

        tk.Button(r, text="LIHAT PESANAN", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=12, command=aksi).pack(side=tk.LEFT)
        aksi()

    def buka_m1_tambah(self, struktur, jenis):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        nama = "Array" if struktur == "array" else "Linked List"
        target = self.arr if struktur == "array" else self.ll

        tk.Label(p, text=f"{nama}: Tambah Pesanan {jenis}", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        ket = (
            "REGULER masuk di paling belakang." if jenis == "REGULER" else
            "PRIORITAS menyerobot ke tengah barisan (n // 2)." if jenis == "PRIORITAS" else
            "VIP langsung masuk ke urutan paling depan (indeks 0)."
        )
        tk.Label(p, text=ket, font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        tk.Label(r, text="Pelanggan:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 4))
        ent_nama = tk.Entry(r, width=16, font=("Helvetica", 9))
        ent_nama.insert(0, f"Pelanggan-{jenis}")
        ent_nama.pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(r, text="Resto:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 4))
        ent_resto = tk.Entry(r, width=13, font=("Helvetica", 9))
        ent_resto.insert(0, "kafe-teknik")
        ent_resto.pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(r, text="Menu:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 4))
        ent_menu = tk.Entry(r, width=13, font=("Helvetica", 9))
        ent_menu.insert(0, "roti-bakar")
        ent_menu.pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(r, text="Harga:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 4))
        ent_harga = tk.Entry(r, width=9, font=("Helvetica", 9))
        ent_harga.insert(0, "15000")
        ent_harga.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text="", font=("Helvetica", 9), bg="white", fg="#1a5e20", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def refresh_tampilan(pos_fokus, pesan_tambahan=""):
            n_skrg = len(target)
            mulai = max(0, pos_fokus - 2) if jenis == "PRIORITAS" else (0 if jenis == "VIP" else max(0, n_skrg - 15))
            lbl.config(
                text=f"{pesan_tambahan}Total data M1: {n_skrg:,} | Antrean M2: {len(self.q_circular):,} | Tumpukan Undo M2: {self.ur_mgr.undo_stack.size()}.".replace(",", ".")
            )
            self._isi_tabel_m1(tree, struktur, mulai_idx=mulai, batas=40)

        def aksi():
            oid = f"O-{self.next_oid:06d}"
            self.next_oid += 1
            prio_angka = 1 if jenis == "VIP" else (2 if jenis == "PRIORITAS" else 3)
            try:
                hrg = int(ent_harga.get().strip())
            except ValueError:
                hrg = 15000

            baru = Pesanan(
                oid=oid,
                pelanggan=ent_nama.get().strip() or "Pelanggan Baru",
                resto=ent_resto.get().strip() or "kafe-teknik",
                menu=ent_menu.get().strip() or "roti-bakar",
                harga=hrg,
                prioritas=prio_angka,
                masuk="12:30:00",
                status="ANTRE"
            )

            n_awal = len(target)
            pos_masuk = n_awal if jenis == "REGULER" else (n_awal // 2 if jenis == "PRIORITAS" else 0)

            # 1. Tambah ke struktur M1 yang dipilih & ukur waktu murni
            t0 = time.perf_counter()
            if jenis == "REGULER":
                target.tambah_reguler(baru)
            elif jenis == "PRIORITAS":
                target.tambah_prioritas(baru)
            else:
                target.tambah_vip(baru)
            ms = (time.perf_counter() - t0) * 1000

            # 2. Sinkronkan ke struktur pasangan di M1
            pasangan = self.ll if struktur == "array" else self.arr
            if jenis == "REGULER":
                pasangan.tambah_reguler(baru)
            elif jenis == "PRIORITAS":
                pasangan.tambah_prioritas(baru)
            else:
                pasangan.tambah_vip(baru)

            # 3. Hubungkan ke M2 (Queue & Stack Undo) serta M3 (Sort & Search)
            self.q_naive.enqueue(baru)
            self.q_circular.enqueue(baru)
            self.ur_mgr.catat_aksi("ORDER", [baru], pos_m1=pos_masuk)
            self._sinkronkan_data_master()
            self.last_added_oid = oid
            self.last_view_idx = pos_masuk

            self._log(f"{struktur}_{jenis.lower()}", f"M1 - {struktur}", ms, f"{oid} @ idx {pos_masuk}")
            refresh_tampilan(
                pos_masuk,
                f"BERHASIL: {oid} ({baru.pelanggan}) masuk di indeks [{pos_masuk:,}] ({ms:.4f} ms).\n"
                f"Terhubung otomatis ke Antrean M2, Stack Undo M2, dan Pencarian M3!\n"
            )

        tk.Button(r, text=f"TAMBAH {jenis}", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=12, command=aksi).pack(side=tk.LEFT)
        pos_awal = len(target) - 1 if jenis == "REGULER" else (len(target) // 2 if jenis == "PRIORITAS" else 0)
        refresh_tampilan(pos_awal)

    def buka_m1_hapus(self, struktur):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        nama = "Array" if struktur == "array" else "Linked List"
        target = self.arr if struktur == "array" else self.ll

        tk.Label(p, text=f"{nama}: Hapus Pesanan ke-i", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(p, text="Mencabut pesanan pada indeks ke-i dari antrean dan mencatatnya ke Stack Undo M2.", font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        tk.Label(r, text="Indeks yang dihapus:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 6))
        ent = tk.Entry(r, width=10, font=("Helvetica", 9))
        ent.insert(0, str(self.last_view_idx if self.last_view_idx < len(target) else 0))
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text=f"Total pesanan {nama}: {len(target):,} baris.", font=("Helvetica", 9), bg="white", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            try:
                idx = int(ent.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Indeks harus berupa angka!")
                return

            if idx < 0 or idx >= len(target):
                messagebox.showerror("Error", f"Indeks harus antara 0 sampai {len(target) - 1}!")
                return

            t0 = time.perf_counter()
            terhapus = self.arr.delete(idx) if struktur == "array" else self.ll.delete(idx)
            ms = (time.perf_counter() - t0) * 1000

            if struktur == "array":
                self.ll.delete(idx)
            else:
                self.arr.delete(idx)

            # Catat ke Undo M2 & sinkronkan ke M3
            self.ur_mgr.catat_aksi("DELETE_M1", [terhapus], pos_m1=idx)
            self._sinkronkan_data_master()

            self._log(f"{struktur}_hapus", f"M1 - {struktur}", ms, f"idx {idx} ({terhapus.oid})")
            lbl.config(
                text=f"Pesanan {terhapus.oid} ({terhapus.pelanggan}) pada indeks [{idx:,}] telah dihapus ({ms:.4f} ms).\n"
                     f"Sisa data M1 & M3: {len(target):,} pesanan | Tumpukan Undo M2: {self.ur_mgr.undo_stack.size()}.".replace(",", ".")
            )
            self._isi_tabel_m1(tree, struktur, mulai_idx=max(0, idx - 2), batas=50)

        tk.Button(r, text="HAPUS PESANAN", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=12, command=aksi).pack(side=tk.LEFT)
        self._isi_tabel_m1(tree, struktur, mulai_idx=max(0, self.last_view_idx - 2), batas=50)

    # M2: STACK & QUEUE (DENGAN DATA LANGSUNG MUNCUL & TERHUBUNG KE M1/M3)
    
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
        tk.Label(p, text="Menambah pesanan di ujung belakang kedua antrean sekaligus (O(1)) dan menyinkronkannya ke M1 & M3.", font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        tk.Label(r, text="Nama Pelanggan:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 6))
        ent = tk.Entry(r, width=18, font=("Helvetica", 9))
        ent.insert(0, f"X{len(self.q_circular) + 1}")
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text="", font=("Helvetica", 9), bg="white", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def tampilkan_ekor_antrean(pesan_awalan=""):
            jml = len(self.q_circular)
            mulai = max(0, jml - 25)
            potongan = self.q_circular.get_slice(mulai, 25)
            lbl.config(
                text=f"{pesan_awalan}Panjang antrean sekarang: Naif {len(self.q_naive):,}, Circular {jml:,} (menampilkan {len(potongan)} antrean paling belakang).".replace(",", ".")
            )
            self._isi_tabel_pesanan_list(tree, potongan, nomor_awal=mulai + 1)

        def aksi():
            oid = f"O-{self.next_oid:06d}"
            self.next_oid += 1
            baru = Pesanan(oid, ent.get().strip() or "Pelanggan Baru", masuk="12:45:00", status="ANTRE")

            t0 = time.perf_counter()
            self.q_naive.enqueue(baru)
            self.q_circular.enqueue(baru)
            ms = (time.perf_counter() - t0) * 1000

            # Hubungkan ke M1, M3, dan Undo Stack
            pos_m1 = len(self.arr)
            self.arr.append(baru)
            self.ll.append(baru)
            self.ur_mgr.catat_aksi("ENQUEUE", [baru], pos_m1=pos_m1)
            self._sinkronkan_data_master()
            self.last_added_oid = oid
            self.last_view_idx = pos_m1

            self._log("queue_enqueue", "M2 - queue", ms, oid)
            tampilkan_ekor_antrean(f"BERHASIL: {oid} ({baru.pelanggan}) masuk ke barisan paling belakang KEDUA antrean ({ms:.4f} ms).\n")

        tk.Button(r, text="ENQUEUE", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=14, command=aksi).pack(side=tk.LEFT)
        tampilkan_ekor_antrean()

    def buka_m2_dequeue_naive(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Queue naif: ambil dari depan dengan menggeser isi", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(p, text="Mengambil indeks 0 lalu menggeser seluruh sisa isi satu petak ke kiri. Biayanya O(n) setiap kali layanan.", font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        tk.Label(r, text="Berapa kali dequeue:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 6))
        ent = tk.Entry(r, width=8, font=("Helvetica", 9))
        ent.insert(0, "2")
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text="", font=("Helvetica", 9), bg="white", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            try:
                k = max(1, int(ent.get().strip()))
            except ValueError:
                k = 1

            keluar = []
            geser_sebelum = self.q_naive.total_geseran
            t0 = time.perf_counter()
            for _ in range(k):
                x = self.q_naive.dequeue()
                self.q_circular.dequeue()
                if x:
                    x.status = "SELESAI"
                    x.selesai = "13:00:00"
                    keluar.append(x)
            ms = (time.perf_counter() - t0) * 1000

            if keluar:
                self.ur_mgr.catat_aksi("DEQUEUE", keluar)
                self._sinkronkan_data_master()

            geser = self.q_naive.total_geseran - geser_sebelum
            rata = geser // len(keluar) if keluar else 0
            lbl.config(
                text=f"{len(keluar)} pesanan keluar dari depan antrean naif.\n"
                     f"Total {geser:,} elemen digeser, rata-rata {rata:,} geseran per dequeue.\n"
                     f"Sisa antrean naif: {len(self.q_naive):,} pesanan.".replace(",", ".")
            )
            self._isi_tabel_pesanan_list(tree, keluar, nomor_awal=1)
            self._log("queue_dequeue_naive", "M2 - queue naif", ms, f"{len(keluar)} keluar")

        tk.Button(r, text="DEQUEUE", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=14, command=aksi).pack(side=tk.LEFT)

        # Tampilkan 50 antrean terdepan saat menu pertama kali dibuka
        depan = self.q_naive.get_slice(0, 50)
        lbl.config(text=f"Antrean siap dilayani (menampilkan {len(depan)} pesanan terdepan dari total {len(self.q_naive):,} antrean):".replace(",", "."))
        self._isi_tabel_pesanan_list(tree, depan, nomor_awal=1)

    def buka_m2_dequeue_circular(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Queue circular: ambil dari depan dengan memajukan penunjuk", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(p, text="Hanya penunjuk front yang maju memakai sisa bagi terhadap kapasitas. Isi array tidak digeser sama sekali (O(1)).", font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        r = tk.Frame(p, bg="white")
        r.pack(fill=tk.X, pady=5)
        tk.Label(r, text="Berapa kali dequeue:", font=("Helvetica", 9), bg="white").pack(side=tk.LEFT, padx=(0, 6))
        ent = tk.Entry(r, width=8, font=("Helvetica", 9))
        ent.insert(0, "2")
        ent.pack(side=tk.LEFT, padx=(0, 8))

        lbl = tk.Label(p, text="", font=("Helvetica", 9), bg="white", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def aksi():
            try:
                k = max(1, int(ent.get().strip()))
            except ValueError:
                k = 1

            keluar = []
            t0 = time.perf_counter()
            for _ in range(k):
                x = self.q_circular.dequeue()
                self.q_naive.dequeue()
                if x:
                    x.status = "SELESAI"
                    x.selesai = "13:00:00"
                    keluar.append(x)
            ms = (time.perf_counter() - t0) * 1000

            if keluar:
                self.ur_mgr.catat_aksi("DEQUEUE", keluar)
                self._sinkronkan_data_master()

            lbl.config(
                text=f"{len(keluar)} pesanan keluar dari depan antrean circular.\n"
                     f"Tidak ada elemen yang digeser; front sekarang {self.q_circular.front}, rear {self.q_circular.rear}, kapasitas {self.q_circular.capacity:,}.\n"
                     f"Sisa antrean circular: {len(self.q_circular):,} pesanan.".replace(",", ".")
            )
            self._isi_tabel_pesanan_list(tree, keluar, nomor_awal=1)
            self._log("queue_dequeue_circular", "M2 - queue circular", ms, f"{len(keluar)} keluar")

        tk.Button(r, text="DEQUEUE", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=14, command=aksi).pack(side=tk.LEFT)

        # Tampilkan 50 antrean terdepan saat menu pertama kali dibuka
        depan = self.q_circular.get_slice(0, 50)
        lbl.config(
            text=f"Antrean circular siap dilayani (front={self.q_circular.front}, rear={self.q_circular.rear}, total={len(self.q_circular):,} pesanan):".replace(",", ".")
        )
        self._isi_tabel_pesanan_list(tree, depan, nomor_awal=1)

    def buka_m2_undo(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Stack: batalkan aksi antrean terakhir", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(p, text="Mengambil catatan teratas tumpukan undo, lalu menjalankan kebalikannya pada M2, M1, dan M3.", font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        # Tombol UNDO diletakkan di ATAS sebelum tabel (sesuai modul)
        btn_undo = tk.Button(p, text="UNDO", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=18, pady=3)
        btn_undo.pack(anchor="w", pady=4)

        lbl = tk.Label(p, text="", font=("Helvetica", 9), bg="white", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def tampilkan_status_awal():
            jml_undo = self.ur_mgr.undo_stack.size()
            if jml_undo > 0:
                tipe_atas, items_atas, _ = self.ur_mgr.undo_stack.peek()
                lbl.config(
                    text=f"Siap membatalkan aksi terakhir: {tipe_atas} ({len(items_atas)} pesanan).\n"
                         f"Panjang antrean sekarang: naif {len(self.q_naive):,}, circular {len(self.q_circular):,}. Tumpukan undo berisi {jml_undo} catatan.".replace(",", ".")
                )
                self._isi_tabel_pesanan_list(tree, items_atas, nomor_awal=1)
            else:
                depan = self.q_circular.get_slice(0, 30)
                lbl.config(
                    text=f"Panjang antrean sekarang: naif {len(self.q_naive):,}, circular {len(self.q_circular):,}. Tumpukan undo: 0 catatan.\n"
                         f"(Menampilkan 30 pesanan terdepan di antrean. Lakukan Tambah M1 / Enqueue / Dequeue dulu untuk menguji Undo).".replace(",", ".")
                )
                self._isi_tabel_pesanan_list(tree, depan, nomor_awal=1)

        def aksi():
            t0 = time.perf_counter()
            res = self.ur_mgr.undo_last()
            ms = (time.perf_counter() - t0) * 1000
            if not res:
                messagebox.showinfo("Undo Kosong", "Tumpukan undo masih kosong! Lakukan Enqueue, Dequeue, atau Tambah/Hapus Pesanan terlebih dahulu.")
                return

            tipe, items = res
            self._sinkronkan_data_master()
            lbl.config(
                text=f"Pembatalan {tipe} berhasil dijalankan ({len(items)} pesanan terdampak).\n"
                     f"Panjang antrean sekarang: naif {len(self.q_naive):,}, circular {len(self.q_circular):,}. Tumpukan undo tersisa {self.ur_mgr.undo_stack.size()} catatan.".replace(",", ".")
            )
            self._isi_tabel_pesanan_list(tree, items, nomor_awal=1)
            self._log("stack_undo", "M2 - stack", ms, f"undo {tipe}")

        btn_undo.config(command=aksi)
        tampilkan_status_awal()

    def buka_m2_redo(self):
        self._clear_main()
        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)
        tk.Label(p, text="Stack: kerjakan lagi aksi yang dibatalkan", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(p, text="Mengambil catatan teratas tumpukan redo, lalu mengerjakan ulang aksi aslinya. Aksi baru apa pun mengosongkan tumpukan ini.", font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        # Tombol REDO diletakkan di ATAS sebelum tabel (sesuai modul)
        btn_redo = tk.Button(p, text="REDO", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=18, pady=3)
        btn_redo.pack(anchor="w", pady=4)

        lbl = tk.Label(p, text="", font=("Helvetica", 9), bg="white", justify=tk.LEFT)
        lbl.pack(anchor="w", pady=4)
        tree = self._create_table(p)

        def tampilkan_status_awal():
            jml_redo = self.ur_mgr.redo_stack.size()
            if jml_redo > 0:
                tipe_atas, items_atas, _ = self.ur_mgr.redo_stack.peek()
                lbl.config(
                    text=f"Siap mengerjakan ulang aksi: {tipe_atas} ({len(items_atas)} pesanan).\n"
                         f"Panjang antrean sekarang: naif {len(self.q_naive):,}, circular {len(self.q_circular):,}. Tumpukan undo {self.ur_mgr.undo_stack.size()}, redo {jml_redo}.".replace(",", ".")
                )
                self._isi_tabel_pesanan_list(tree, items_atas, nomor_awal=1)
            else:
                depan = self.q_circular.get_slice(0, 30)
                lbl.config(
                    text=f"Panjang antrean sekarang: naif {len(self.q_naive):,}, circular {len(self.q_circular):,}. Tumpukan undo {self.ur_mgr.undo_stack.size()}, redo 0.\n"
                         f"(Tumpukan redo kosong. Jalankan UNDO terlebih dahulu untuk mengisi tumpukan Redo).".replace(",", ".")
                )
                self._isi_tabel_pesanan_list(tree, depan, nomor_awal=1)

        def aksi():
            t0 = time.perf_counter()
            res = self.ur_mgr.redo_last()
            ms = (time.perf_counter() - t0) * 1000
            if not res:
                messagebox.showinfo("Redo Kosong", "Tumpukan redo kosong! Tidak ada aksi yang baru dibatalkan.")
                return

            tipe, items = res
            self._sinkronkan_data_master()
            lbl.config(
                text=f"{tipe} dikerjakan ulang ({len(items)} pesanan).\n"
                     f"Panjang antrean sekarang: naif {len(self.q_naive):,}, circular {len(self.q_circular):,}. Tumpukan undo {self.ur_mgr.undo_stack.size()}, redo {self.ur_mgr.redo_stack.size()}.".replace(",", ".")
            )
            self._isi_tabel_pesanan_list(tree, items, nomor_awal=1)
            self._log("stack_redo", "M2 - stack", ms, f"redo {tipe}")

        btn_redo.config(command=aksi)
        tampilkan_status_awal()

    # M3: SORT & SEARCH
    def buka_m3_sort(self, jenis):
        self._clear_main()
        self._sinkronkan_data_master()

        p = tk.Frame(self.main_area, padx=15, pady=10, bg="white")
        p.pack(fill=tk.BOTH, expand=True)

        judul = "Sort: insertion sort, O(n²)" if jenis == "insertion" else "Sort: merge sort, O(n log n)"
        sub = (
            "Setiap elemen digeser mundur sampai menemukan tempatnya. Sederhana, tetapi kerjanya tumbuh kuadratik."
            if jenis == "insertion" else
            "Array dibelah dua terus-menerus, lalu potongan yang sudah terurut disatukan kembali."
        )
        tk.Label(p, text=judul, font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(p, text=sub, font=("Helvetica", 8), fg="#666", bg="white").pack(anchor="w", pady=(0, 8))

        form = tk.Frame(p, bg="white")
        form.pack(fill=tk.X, pady=4)

        f_jml = tk.Frame(form, bg="white")
        f_jml.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(f_jml, text="Jumlah baris diurutkan", font=("Helvetica", 8, "bold"), bg="white").pack(anchor="w")
        ent_n = tk.Entry(f_jml, width=14, font=("Helvetica", 9))
        ent_n.insert(0, "10" if jenis == "insertion" else "4000")
        ent_n.pack(anchor="w", pady=2)
        tk.Label(f_jml, text=f"total data aktif: {len(self.data_master):,} baris".replace(",", "."), font=("Helvetica", 7), fg="#888", bg="white").pack(anchor="w")

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
            self._sinkronkan_data_master()
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
            for idx, it in enumerate(hasil[:200], 1):
                harga_fmt = f"{it.harga:,}".replace(",", ".")
                tree.insert("", tk.END, values=(idx, it.oid, harga_fmt, it.selesai, it.resto, it.menu))

            self._log(cmd_tag, mod_tag, ms)

        btn = tk.Button(form, text="URUTKAN", bg="#203a43", fg="white", font=("Helvetica", 9, "bold"), padx=18, pady=4, command=aksi_urutkan)
        btn.pack(side=tk.LEFT, pady=8)
        aksi_urutkan()

    def buka_m3_search(self, jenis):
        self._clear_main()
        self.data_master = self.arr.data[:self.arr.size]

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

        oid_terakhir = getattr(self, "last_added_oid", None)
        if oid_terakhir:
            default_oid = oid_terakhir
        else:
            default_idx = min(137441, len(self.data_master) - 1)
            default_oid = self.data_master[default_idx].oid if self.data_master else "O-137442"

        ent_oid.insert(0, default_oid)
        ent_oid.pack(anchor="w", pady=2)
        tk.Label(f_in, text=f"format O-000001 sampai O-{self.next_oid - 1:06d} ({len(self.data_master):,} data)".replace(",", "."), font=("Helvetica", 7), fg="#888", bg="white").pack(anchor="w")

        lbl_info = tk.Label(p, text="", font=("Helvetica", 9), bg="white", fg="#222", justify=tk.LEFT)
        lbl_info.pack(anchor="w", pady=4)

        t_frame = tk.Frame(p)
        t_frame.pack(fill=tk.BOTH, expand=True, pady=6)
        tree = ttk.Treeview(t_frame, columns=("kolom", "isi"), show="headings", height=9)
        tree.heading("kolom", text="kolom")
        tree.heading("isi", text="isi")
        tree.column("kolom", width=180, anchor="w")
        tree.column("isi", width=450, anchor="w")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def aksi_cari():
            self.data_master = self.arr.data[:self.arr.size]
            target = ent_oid.get().strip().upper()

            if jenis == "linear":
                t0 = time.perf_counter()
                idx, comp = linear_search(self.data_master, target)
                ms = (time.perf_counter() - t0) * 1000
                item = self.data_master[idx] if idx != -1 else None

                if item:
                    lbl_info.config(text=f"Ditemukan pada indeks {idx:,} dari {len(self.data_master):,} baris.\n{comp:,} perbandingan.".replace(",", "."))
                else:
                    lbl_info.config(text=f"Pesanan {target} tidak ditemukan.\n{comp:,} perbandingan.".replace(",", "."))
                self._log("linear_search", "M3 - linear search", ms, target)
            else:
                if self.cache_oid_terurut is None or len(self.cache_oid_terurut) != len(self.data_master):
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
                self._log("binary_search", "M3 - binary search", ms, target)

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