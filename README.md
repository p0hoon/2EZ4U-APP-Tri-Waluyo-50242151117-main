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