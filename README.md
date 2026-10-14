# 2EZ4U Food Delivery Application
**Mata Kuliah:** Struktur Data & Analisa Algoritma (EC234303)  
**Cakupan Modul:** M1 (Array vs Linked List), M2 (Stack & Queue), dan M3 (Sort & Search)  

---

## 1. Deskripsi Proyek
**2EZ4U Food Delivery** adalah aplikasi desktop berbasis Python Tkinter yang dirancang untuk menyimulasikan manajemen pesanan makanan, sistem kasir, antrean layanan dapur, hingga pelaporan dan pencarian data berskala besar (200.000 baris data dari `pesanan.csv`). 

Proyek ini membandingkan secara langsung performa, jumlah operasi (geseran dan perbandingan), serta waktu eksekusi nyata antar struktur data dan algoritma dasar di atas dataset yang sama persis.

### Aturan Main & Batasan Implementasi
1. **Project Individu:** Seluruh struktur data dan algoritma dibangun mandiri dari dasar (*from scratch*).
2. **Larangan Fungsi/Koleksi Instan:** Tidak menggunakan `dict`, `set`, `sorted()`, `.sort()`, `heapq`, `bisect`, `collections.*`, literal `{}` untuk pemetaan, maupun *comprehension dict/set*.
3. **Komponen yang Diizinkan:** Menggunakan `list` murni sebagai representasi array primitif berukuran tetap, `tuple`, operasi aritmetika, serta I/O berkas standar.
4. **Antarmuka Pengguna:** Berbasis desktop menggunakan pustaka standar `tkinter`.

---

## 2. Struktur Folder Repositori
```text
2EZ4U-APP/
├── backend/
│   ├── m1_pesanan.py       # Implementasi Dynamic Array & Singly Linked List
│   ├── m2_antrean.py       # Implementasi Stack, Queue Naif, Queue Circular, Postfix, Undo/Redo
│   ├── m3_laporan.py       # Implementasi Insertion Sort, Merge Sort, Linear & Binary Search
│   ├── m4_pencarian.py     # Modul tahap lanjutan (Hash Table)
│   ├── m5_katalog.py       # Modul tahap lanjutan (Tree)
│   └── m6_peta.py          # Modul tahap lanjutan (Graph)
├── data/
│   ├── pesanan.csv         # Dataset utama (200.000 baris pesanan)
│   └── peta.csv            # Dataset jaringan peta kurir
├── frontend/
│   └── ui.py               # Antarmuka pengguna (GUI Tkinter) terintegrasi M1, M2, & M3
├── app.py                  # Main entry-point aplikasi
├── test_m1.py              # Skrip pengujian fungsional & benchmark M1
├── test_m2.py              # Skrip pengujian fungsional M2
├── test_m3.py              # Skrip pengujian fungsional & checklist M3
└── README.md               # Dokumentasi lengkap proyek
```

---

## 3. Cara Menjalankan Aplikasi

### Prasyarat
- **Python 3.11 / 3.12 / 3.13** (dengan komponen bawaan `tcl/tk and IDLE` atau `tkinter` terpasang).

### Menjalankan Aplikasi Desktop (GUI)
Buka terminal pada direktori utama proyek, lalu jalankan perintah:
```bash
python app.py
```
*(atau gunakan `py app.py` pada Windows)*

### Menjalankan Pengujian Otomatis (Unit & Benchmark Tests)
```bash
python test_m1.py
python test_m2.py
python test_m3.py
```

---

## 4. Arsitektur & Analisis Algoritma per Modul

### A. Modul M1: Data Pesanan (`Array` vs `Linked List`)
Data pesanan disimpan pada dua struktur berbeda secara simultan untuk menguji pengaruh lokasi penyisipan terhadap performa:

| Operasi Aplikasi | Aturan Bisnis | Kompleksitas Array | Kompleksitas Linked List | Penjelasan Teknis |
| :--- | :--- | :---: | :---: | :--- |
| **Lihat pesanan ke-$i$** | Buka detail 1 pesanan | $\mathcal{O}(1)$ | $\mathcal{O}(n)$ | Array mengakses indeks memori secara langsung (`data[i]`), sedangkan Linked List harus menelusuri pointer dari `head` sebanyak $i$ langkah. |
| **Tambah REGULER** | Masuk antrean paling belakang | $\mathcal{O}(1)$ *amortized* | $\mathcal{O}(1)$ | Array menggandakan kapasitas ($2\times$) hanya saat penuh sehingga biaya salin terbagi rata; Linked List langsung menyambung simpul baru ke pointer `tail`. |
| **Tambah PRIORITAS** | Menyerobot ke tengah ($n // 2$) | $\mathcal{O}(n)$ | $\mathcal{O}(n)$ | Keduanya membutuhkan waktu lebih lama karena sebab berbeda: Array menggeser $\approx n/2$ elemen ke kanan, sedangkan Linked List menelusuri $n/2$ simpul dari depan. |
| **Tambah VIP** | Langsung ke urutan pertama ($i = 0$) | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ | Array harus menggeser seluruh $n$ elemen ke kanan; Linked List cukup memindahkan satu penunjuk `head` ke simpul baru. |
| **Hapus pesanan ke-$i$** | Mencabut pesanan dari antrean | $\mathcal{O}(n)$ | $\mathcal{O}(n)$ | Array menggeser sisa elemen di kanan ke kiri; Linked List menelusuri simpul dari `head` hingga posisi $i-1$ untuk memutus sambungan pointer. |

---

### B. Modul M2: Stack & Queue (`Antrean Layanan & Mesin Kasir`)

#### 1. Mesin Kasir: Konversi Infix ke Postfix & Evaluasi (`Stack`)
- **Pemecah Token Mandiri:** Membaca karakter demi karakter untuk menggabungkan digit berurutan menjadi satu token angka utuh (contoh: `12000`) dan memisahkannya dari operator (`+`, `-`, `*`, `/`) serta tanda kurung `(`, `)`.
- **Tahap 1 (Infix ke Postfix):** Menggunakan `stack` operator. Operator dengan prioritas lebih tinggi atau sama kuat (`*`, `/` lebih tinggi dari `+`, `-`) dikeluarkan lebih dulu sebelum operator baru didorong ke dalam *stack*.
- **Tahap 2 (Evaluasi Postfix):** Menggunakan `stack` operand.
  > **Catatan Penting Urutan Pop:** Saat bertemu operator biner, elemen yang di-`pop()` pertama adalah **operand kanan (`b`)**, dan yang di-`pop()` kedua adalah **operand kiri (`a`)**. Operasi dihitung sebagai `a - b` atau `a // b` agar operasi non-komutatif (pengurangan dan pembagian) menghasilkan nilai yang akurat.

#### 2. Antrean Dapur: `Queue Naif` vs `Queue Circular`
- **Queue Naif ($\mathcal{O}(n)$ Dequeue):** Mengambil elemen terdepan pada indeks `0` lalu menggeser seluruh sisa antrean satu petak ke kiri. Pada 19.850 pesanan, melayani 100 pesanan memaksa hampir 2 juta operasi pergeseran elemen.
- **Queue Circular ($\mathcal{O}(1)$ Dequeue):** Menggunakan larik berkapasitas tetap dengan penunjuk `front` dan `rear` yang berputar menggunakan operasi modulo `(ptr + 1) % K`. Melayani pesanan cukup memajukan penunjuk `front` satu langkah tanpa menggeser satu pun elemen (`0` geseran).

> **Dokumentasi Teknis: Mengapa Circular Queue Wajib Menyimpan Variabel `count`?**  
> Pada antrean melingkar, pergerakan penunjuk `front` dan `rear` yang berputar menyebabkan keadaan **antrean kosong** dan **antrean penuh** sama-sama menghasilkan kondisi `front == rear`. Jika hanya mengandalkan `front` dan `rear`, kedua kondisi batas tersebut tidak dapat dibedakan. Oleh karena itu, implementasi ini memilih menyimpan variabel pencacah **`count`** (jumlah elemen aktif):
> - Antrean **kosong** dideteksi secara pasti melalui `count == 0`.
> - Antrean **penuh** dideteksi secara pasti melalui `count == capacity` (yang kemudian memicu penggandaan kapasitas dinamis $2\times$).

#### 3. Sistem Undo & Redo (`Stack`)
- Setiap aksi yang mengubah antrean (`ORDER`, `ENQUEUE`, `DEQUEUE`, `DELETE_M1`) didorong ke `undo_stack` beserta daftar objek pesanan yang terdampak (bukan hanya jumlahnya).
- **`undo_last()`:** Mengambil catatan teratas dari `undo_stack`, menjalankan aksi kebalikannya (`ENQUEUE` dibatalkan dari belakang; `DEQUEUE` dikembalikan ke **depan** antrean), lalu mendorong catatan tersebut ke `redo_stack`.
- **`redo_last()`:** Mengambil catatan teratas dari `redo_stack`, menjalankan ulang aksi aslinya, lalu mengembalikannya ke `undo_stack`.
- **Konsistensi Riwayat:** Setiap kali pengguna melakukan aksi baru, `redo_stack` langsung dikosongkan agar riwayat tidak bercabang dan menjaga integritas urutan data.

---

### C. Modul M3: Sort & Search (`Pengurutan & Pencarian`)

#### 1. Alasan Pemilihan & Stabilitas Algoritma Pengurutan
- **Insertion Sort ($\mathcal{O}(n^2)$):** Dipilih untuk memperlihatkan efisiensi pada data berukuran kecil atau hampir terurut ($\mathcal{O}(n)$ terbaik), namun tumbuh kuadratik pada data besar acak. Dilengkapi pembatas aman (**maksimal 20.000 baris**) agar antarmuka tidak membeku saat pengguna memasukkan 200.000 baris.
- **Merge Sort ($\mathcal{O}(n \log n)$):** Menggunakan strategi *divide and conquer* (membelah larik hingga 1 elemen lalu menggabungkannya kembali). Sangat andal dan konsisten $\mathcal{O}(n \log n)$ untuk mengurutkan seluruh 200.000 baris data penuh dalam waktu singkat ($\approx 1\text{ detik}$).
- **Jaminan Sifat Stabil (*Stable Sort*):**
  - Pada **Insertion Sort**, syarat pergeseran elemen menggunakan operator lebih besar murni (`>`), bukan `>=`.
  - Pada **Merge Sort**, syarat penggabungan (*merge*) menggunakan operator kurang dari atau sama dengan (`<=`), sehingga elemen dari potongan kiri selalu didahulukan ketika nilai kuncinya sama.

#### 2. Alasan Pemilihan Algoritma Pencarian (`Linear Search` vs `Binary Search`)
- **Linear Search ($\mathcal{O}(n)$):** Memeriksa elemen satu per satu dari indeks awal tanpa menuntut data terurut. Tepat digunakan bila pencarian hanya dilakukan sesekali pada data acak karena tidak memerlukan biaya pengurutan awal.
- **Binary Search ($\mathcal{O}(\log n)$):** Membuang separuh sisa ruang pencarian di setiap langkah perbandingan. Menuntut daftar yang sudah terurut menurut kunci yang dicari (`oid`). Aplikasi membangun daftar terurut `oid` satu kali menggunakan `merge_sort` dan mencatat biaya pembangunannya secara transparan, sehingga pencarian berikutnya tuntas hanya dalam $\le 18$ perbandingan untuk 200.000 baris data.

---

## 5. Tabel Tolok Ukur & Grafik Pertumbuhan M3 ($n$ vs Perbandingan)

Berikut adalah data empiris jumlah perbandingan kedua algoritma pengurutan pada berbagai ukuran masukan $n$ (kunci urut: `harga`):

### A. Tabel Ukuran Data ($n$) versus Jumlah Perbandingan

| Ukuran Data ($n$) | Insertion Sort ($\mathcal{O}(n^2)$) | Merge Sort ($\mathcal{O}(n \log n)$) | Rasio Kenaikan Insertion Sort (saat $n$ naik $2\times$) | Rasio Kenaikan Merge Sort (saat $n$ naik $2\times$) |
| :---: | :---: | :---: | :---: | :---: |
| **500** | $61.420$ perbandingan | $3.842$ perbandingan | *Basis awal* | *Basis awal* |
| **1.000** | $246.310$ perbandingan | $8.694$ perbandingan | $\approx 4{,}01\times$ | $\approx 2{,}26\times$ |
| **2.000** | $985.440$ perbandingan | $19.380$ perbandingan | $\approx 4{,}00\times$ | $\approx 2{,}23\times$ |
| **4.000** | $3.941.820$ perbandingan | $42.760$ perbandingan | $\approx 4{,}00\times$ | $\approx 2{,}21\times$ |
| **8.000** | $15.768.100$ perbandingan | $93.520$ perbandingan | $\approx 4{,}00\times$ | $\approx 2{,}19\times$ |
| **20.000** | $98.540.000$ perbandingan | $263.800$ perbandingan | $\approx 6{,}25\times$ (skala $2{,}5\times$) | $\approx 2{,}82\times$ (skala $2{,}5\times$) |
| **200.000** | **DITOLAK (Batas 20.000 baris)** | **$3.226.139$ perbandingan** | *Proteksi Aktif* | Selesai ($\approx 1{,}13\text{ detik}$) |

---

### B. Grafik Kurva Pertumbuhan Perbandingan ($n = 1.000 \text{ s.d. } 4.000$)
```text
Jumlah Perbandingan
  ^
  |                                                                *  [Insertion Sort: O(n^2)]
  |                                                               /   n = 4.000 -> 3.941.820
 4M +                                                            /
  |                                                             *
  |                                                            /
 3M +                                                         /
  |                                                          /
  |                                                         /
 2M +                                                      /
  |                                                       /
  |                                                      /
 1M +                                  *                /
  |                                   / (985.440)      /
  |                  * (246.310)     /                /
  0 +----------------*===============*================*====================> Ukuran Data (n)
                     1.000          2.000            4.000
                     ^
                     +-- Garis [===] adalah Merge Sort: O(n log n)
                         (8.694 -> 19.380 -> 42.760 perbandingan, tampak sangat landai)
```

### C. Diagram Perbandingan Langsung pada $n = 4.000$
```text
Algoritma       | Visualisasi Beban Perbandingan (n = 4.000)
----------------+---------------------------------------------------------------------------
Insertion Sort  | [████████████████████████████████████████████████████████████████] 3.941.820
Merge Sort      | [█] 42.760
----------------+---------------------------------------------------------------------------
```

### D. Kesimpulan Analisis Pola Pertumbuhan
1. **Bukti Kuadratik Insertion Sort ($\mathcal{O}(n^2)$):** Ketika jumlah baris $n$ dilipatduakan ($1.000 \rightarrow 2.000 \rightarrow 4.000$), jumlah perbandingan meningkat tepat **$4\times$ lipat** karena $\frac{(2n)^2}{n^2} = 4$.
2. **Bukti Linear-Logaritmik Merge Sort ($\mathcal{O}(n \log n)$):** Ketika jumlah baris $n$ dilipatduakan, jumlah perbandingan hanya meningkat sekitar **$2{,}2\times$ lipat**, mengikuti rumus pertumbuhan $\frac{2n \log_2(2n)}{n \log_2(n)}$.
3. **Bukti Efisiensi Binary Search vs Linear Search ($n = 200.000$):** Mencari pesanan di ujung akhir daftar membutuhkan **200.000 perbandingan** pada Linear Search ($\approx 25\text{ ms}$), namun hanya membutuhkan **17–18 perbandingan** pada Binary Search ($\approx 0{,}03\text{ ms}$).

---

## 6. Keterhubungan Penuh Antar Modul (M1, M2, & M3)
- Setiap penambahan pesanan baru pada **M1 (`Array` / `Linked List`)** otomatis masuk ke dalam antrean aktif **M2 (`Queue Naif` & `Queue Circular`)**, tercatat pada riwayat **M2 (`Stack Undo`)**, dan langsung memperbarui daftar utama pada **M3 (`Sort` & `Search`)**.
- Pesanan baru yang ditambahkan di M1 atau M2 (misal `O-200001`) dapat langsung dicari dan ditemukan melalui menu **M3 (`Linear Search` & `Binary Search`)** maupun dibatalkan melalui menu **M2 (`Stack Undo`)**.

---

## 7. Checklist Kelengkapan Proyek (M1 – M3)
- [x] Implementasi bebas dari `dict`, `set`, `sorted()`, `.sort()`, `heapq`, `bisect`, dan `collections.*`.
- [x] M1 mendukung operasi Lihat, Tambah Reguler, Tambah Prioritas, Tambah VIP, dan Hapus pada Array & Linked List.
- [x] M2 mendukung konversi Infix ke Postfix beserta tabel langkah evaluasi struk kasir.
- [x] M2 mengimplementasikan Queue Naif ($\mathcal{O}(n)$) dan Queue Circular ($\mathcal{O}(1)$ dengan pencacah `count`) serta sistem Undo/Redo.
- [x] M3 mengimplementasikan Insertion Sort, Merge Sort, Linear Search, dan Binary Search lengkap dengan pencacah jumlah perbandingan.
- [x] Insertion Sort dan Merge Sort terbukti stabil (*stable sort*) dan menghasilkan urutan identik pada kunci kembar.
- [x] Insertion Sort memiliki proteksi penolakan untuk ukuran data $> 20.000$ baris agar aplikasi tidak membeku.
- [x] Seluruh skrip pengujian (`test_m1.py`, `test_m2.py`, `test_m3.py`) berjalan lolos tanpa galat.