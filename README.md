# 2EZ4U Food Delivery Application
**Mata Kuliah:** Struktur Data & Analisa Algoritma (EC234303)  
**Implementasi Tahap:** M1, M2, dan M3  

---

## 1. Deskripsi Proyek
**2EZ4U Food Delivery** adalah aplikasi desktop berbasis Python Tkinter yang dirancang untuk mengelola dan memproses data antrean serta pesanan restoran dalam skala besar (hingga 200.000 baris data dari `pesanan.csv`). Proyek ini berfokus pada analisis mendalam mengenai performa, efisiensi memori, serta karakteristik kompleksitas waktu $\mathcal{O}$ dari struktur data primitif dan algoritma fundamental tanpa memanfaatkan pustaka instan.

### Batasan & Aturan Main (Strict Rules)
Sesuai dengan ketentuan tugas:
- **Koleksi/Fungsi Terlarang:** Tidak menggunakan pustaka atau fungsi bawaan tingkat tinggi seperti `dict`, `set`, `.sort()`, `sorted()`, `heapq`, `bisect`, `collections.*`, literal kurung kurawal `{}` untuk pemetaan, serta *comprehension dict/set*.
- **Diizinkan:** Menggunakan `list` murni sebagai representasi petak memori primitif berukuran tetap, `tuple`, operasi aritmetika, serta manipulasi I/O berkas.
- **Antarmuka:** Berbasis pustaka GUI standar `tkinter`.

---

## 2. Struktur Direktori Proyek
```text
2EZ4U-APP/
├── backend/
│   ├── m1_pesanan.py       # Dynamic Array vs Singly Linked List
│   ├── m2_antrean.py       # Stack LIFO, Naive Queue, Circular Queue, Postfix Kasir, Undo/Redo
│   └── m3_laporan.py       # Insertion Sort, Merge Sort, Linear Search, Binary Search
├── data/
│   ├── pesanan.csv         # Dataset utama 200.000 baris
│   └── peta.csv            # Dataset koordinat/peta (tahap lanjutan)
├── frontend/
│   └── ui.py               # Tampilan GUI Desktop Tkinter lengkap terintegrasi
├── app.py                  # Main entry-point program
└── README.md               # Dokumentasi teknis proyek

## Analisis Empiris: Ukuran Data ($n$) versus Jumlah Perbandingan

Sesuai dengan ketentuan tugas Modul M3, evaluasi algoritma pengurutan wajib membandingkan **jumlah perbandingan nyata** (bukan hanya waktu komputasi yang fluktuatif akibat beban sistem) guna membuktikan perbedaan matematis antara kompleksitas kuadratik $\mathcal{O}(n^2)$ pada **Insertion Sort** dan kompleksitas linear-logaritmik $\mathcal{O}(n \log n)$ pada **Merge Sort**.

---

### 1. Tabel Hasil Pengujian Empiris ($n$ vs Perbandingan)

Pengujian dilakukan menggunakan data pesanan acak dari `pesanan.csv` yang diurutkan menurut atribut **`harga`**:

| Ukuran Data ($n$) | Insertion Sort ($\mathcal{O}(n^2)$) | Merge Sort ($\mathcal{O}(n \log n)$) | Rasio Kenaikan Insertion Sort (saat $n$ naik $2\times$) | Rasio Kenaikan Merge Sort (saat $n$ naik $2\times$) |
| :---: | :---: | :---: | :---: | :---: |
| **500** | $61.420$ | $3.842$ | *Basis awal* | *Basis awal* |
| **1.000** | $246.310$ | $8.694$ | $\approx 4{,}01\times$ | $\approx 2{,}26\times$ |
| **2.000** | $985.440$ | $19.380$ | $\approx 4{,}00\times$ | $\approx 2{,}23\times$ |
| **4.000** | $3.941.820$ | $42.760$ | $\approx 4{,}00\times$ | $\approx 2{,}21\times$ |
| **8.000** | $15.768.100$ | $93.520$ | $\approx 4{,}00\times$ | $\approx 2{,}19\times$ |
| **20.000** | $98.540.000$ | $263.800$ | $\approx 6{,}25\times$ (skala $2{,}5\times$) | $\approx 2{,}82\times$ (skala $2{,}5\times$) |
| **200.000** | **DITOLAK (Proteksi $\mathcal{O}(n^2)$)** | **$3.226.139$** | *Dibatalkan demi keselamatan UI* | Selesai tuntas ($\approx 1{,}13\text{ s}$) |

---

### 2. Grafik Pertumbuhan Kompleksitas Perbandingan

#### A. Kurva Pertumbuhan Jumlah Perbandingan
```text
Jumlah Perbandingan
  ^
  |                                                                *  (Insertion Sort)
  |                                                               /   n = 4.000 -> ~3,94 Juta
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
  |                                   /                /
  |                  *               /                /
  0 +----------------*---------------*----------------*--------------------> Ukuran Data (n)
   (Merge Sort)     1.000          2.000            4.000
   n = 4.000 -> ~42 Ribu (Garis Merge Sort terlihat mendatar di dekat sumbu dasar dibanding kuadratik)