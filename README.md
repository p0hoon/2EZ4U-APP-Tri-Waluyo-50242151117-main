# 2EZ4U Food Delivery

Aplikasi desktop **Python Tkinter** untuk simulasi pesanan makanan, kasir, antrean dapur, serta pelaporan & pencarian data **200.000 baris** (`pesanan.csv`).
Proyek ini membandingkan jumlah operasi dan waktu eksekusi nyata antar struktur data/algoritma pada dataset yang sama.

> **Mata Kuliah:** Struktur Data & Analisa Algoritma (EC234303) · **Cakupan:** M1 Array vs Linked List · M2 Stack & Queue · M3 Sort & Search

## Aturan Implementasi

- Project **individu**, semua struktur data & algoritma dibuat **from scratch**.
- **Dilarang:** `dict`, `set`, `sorted()`, `.sort()`, `heapq`, `bisect`, `collections.*`, literal `{}`, dan comprehension dict/set.
- **Diizinkan:** `list` murni (array primitif), `tuple`, aritmetika, dan I/O berkas standar.
- UI memakai `tkinter` bawaan Python.

## Struktur Repositori

```text
2EZ4U-APP/
├── backend/
│   ├── m1_pesanan.py    # Dynamic Array & Singly Linked List
│   ├── m2_antrean.py    # Stack, Queue Naif/Circular, Postfix, Undo/Redo
│   ├── m3_laporan.py    # Insertion/Merge Sort, Linear/Binary Search
│   └── m4–m6 (.py)      # Tahap lanjutan: Hash Table, Tree, Graph
├── data/                # pesanan.csv (200.000 baris), peta.csv
├── frontend/ui.py       # GUI Tkinter terintegrasi M1–M3
├── app.py               # Entry-point
└── README.md
```

## Menjalankan

**Prasyarat:** Python 3.11 – 3.13 dengan `tkinter` terpasang.

```bash
python app.py          # GUI (Windows: py app.py)
```
## Screenshot UI
<img width="1919" height="1010" alt="Screenshot 2026-10-15 044518" src="https://github.com/user-attachments/assets/f4b07b18-0914-46ad-8c0f-e2caec1a495f" />


## Ringkasan Modul

### M1 — Array vs Linked List

| Operasi | Array | Linked List | Alasan |
| :--- | :---: | :---: | :--- |
| Lihat pesanan ke-`i` | `O(1)` | `O(n)` | Akses indeks langsung vs telusur pointer dari `head` |
| Tambah **Reguler** (belakang) | `O(1)` amortized | `O(1)` | Array menggandakan kapasitas saat penuh; list sambung ke `tail` |
| Tambah **Prioritas** (tengah) | `O(n)` | `O(n)` | Array menggeser ≈ n/2 elemen; list menelusuri n/2 simpul |
| Tambah **VIP** (depan) | `O(n)` | `O(1)` | Array menggeser semua elemen; list cukup ubah `head` |
| Hapus pesanan ke-`i` | `O(n)` | `O(n)` | Geser elemen vs telusur sampai posisi `i-1` |

### M2 — Stack & Queue

**Mesin Kasir (Stack)** — tokenizer mandiri → Infix ke Postfix (stack operator) → evaluasi Postfix (stack operand). Saat `pop()`, operand **kanan (`b`)** keluar lebih dulu, lalu **kiri (`a`)**, sehingga `a - b` dan `a // b` akurat.

**Antrean Dapur**

| | Queue Naif | Queue Circular |
| :--- | :---: | :---: |
| Dequeue | `O(n)` (geser ke kiri) | `O(1)` (majukan `front`, modulo `(ptr+1) % K`) |
| Contoh 19.850 pesanan, layani 100 | ≈ 2 juta geseran | 0 geseran |

> **Mengapa Circular Queue memakai `count`?** Antrean kosong dan penuh sama-sama menghasilkan `front == rear`. Variabel `count` membedakannya: kosong jika `count == 0`, penuh jika `count == capacity` (memicu penggandaan kapasitas 2×).

**Undo/Redo (Stack)**
- Aksi `ORDER`, `ENQUEUE`, `DEQUEUE`, `DELETE_M1` dicatat di `undo_stack` bersama objek pesanan yang terdampak.
- `undo_last()` membalik aksi (ENQUEUE dibatalkan dari belakang, DEQUEUE dikembalikan ke **depan**) lalu mendorongnya ke `redo_stack`; `redo_last()` kebalikannya.
- Aksi baru akan mengosongkan `redo_stack` agar riwayat tidak bercabang.

### M3 — Sort & Search

| Algoritma | Kompleksitas | Catatan |
| :--- | :---: | :--- |
| Insertion Sort | `O(n²)` | Stabil (geser dengan `>`); dibatasi **maks. 20.000 baris** agar UI tidak membeku |
| Merge Sort | `O(n log n)` | Stabil (merge dengan `<=`); mengurutkan 200.000 baris ≈ 1,13 detik |
| Linear Search | `O(n)` | Tanpa syarat terurut; cocok untuk pencarian sesekali |
| Binary Search | `O(log n)` | Butuh daftar terurut `oid` (dibangun sekali via `merge_sort`, biayanya dicatat); ≤ 18 perbandingan untuk 200.000 baris |

## Benchmark M3 (jumlah perbandingan, kunci: `harga`)

| n | Insertion Sort | Merge Sort | Rasio Insertion | Rasio Merge |
| ---: | ---: | ---: | :---: | :---: |
| 500 | 61.420 | 3.842 | basis | basis |
| 1.000 | 246.310 | 8.694 | ≈ 4,01× | ≈ 2,26× |
| 2.000 | 985.440 | 19.380 | ≈ 4,00× | ≈ 2,23× |
| 4.000 | 3.941.820 | 42.760 | ≈ 4,00× | ≈ 2,21× |
| 8.000 | 15.768.100 | 93.520 | ≈ 4,00× | ≈ 2,19× |
| 20.000 | 98.540.000 | 263.800 | — | — |
| 200.000 | ditolak (> 20.000) | 3.226.139 | proteksi aktif | selesai |

*Rasio = kenaikan perbandingan saat n naik 2×.*
## Grafik Sort

<p align="center">
  <img src="grafik_.svg" width="750" alt="Grafik Pertumbuhan Perbandingan Insertion Sort vs Merge Sort">
</p>


**Kesimpulan**
1. **Insertion Sort kuadratik:** n dua kali lipat → perbandingan ≈ **4×** (`(2n)²/n² = 4`).
2. **Merge Sort linear-logaritmik:** n dua kali lipat → perbandingan hanya ≈ **2,2×**.
3. **Pencarian pada n = 200.000:** Linear Search 200.000 perbandingan (≈ 25 ms) vs Binary Search 17–18 perbandingan (≈ 0,03 ms).

## Integrasi Antar Modul

Pesanan baru di **M1** otomatis masuk ke antrean **M2** (Naif & Circular), tercatat di Stack Undo, dan langsung muncul di daftar **M3**. Pesanan baru (mis. `O-200001`) bisa langsung dicari lewat Linear/Binary Search dan dibatalkan lewat Undo.

## Checklist

- [x] Bebas `dict`, `set`, `sorted()`, `.sort()`, `heapq`, `bisect`, `collections.*`
- [x] M1: Lihat, Tambah Reguler/Prioritas/VIP, Hapus (Array & Linked List)
- [x] M2: Infix → Postfix + tabel langkah evaluasi struk kasir
- [x] M2: Queue Naif & Circular (dengan `count`) + Undo/Redo
- [x] M3: Insertion & Merge Sort, Linear & Binary Search, dengan pencacah perbandingan
- [x] Kedua sort terbukti stabil pada kunci kembar
- [x] Proteksi Insertion Sort untuk data > 20.000 baris
