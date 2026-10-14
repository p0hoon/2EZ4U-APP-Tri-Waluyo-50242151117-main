BATAS_INSERTION = 20000  # Batas aman agar UI tidak membeku pada O(n^2)

def _ambil_kunci(item, kunci="oid"):
    """Mengambil nilai atribut perbandingan dari objek Pesanan atau tipe primitif."""
    if hasattr(item, kunci):
        val = getattr(item, kunci)
        if kunci == "harga" or kunci == "prioritas":
            return int(val)
        return str(val)
    return item

def insertion_sort(larik, kunci="oid"):
    """
    Insertion Sort: Bekerja stabil (syarat geser memakai > bukan >=).
    Kompleksitas: O(n^2) rata-rata/terburuk, O(n) jika hampir terurut.
    Mengembalikan: (larik_terurut, jumlah_perbandingan, jumlah_pemindahan)
    """
    n = len(larik)
    if n > BATAS_INSERTION:
        raise ValueError(f"DITOLAK: batasnya {BATAS_INSERTION:,} baris, pakai merge sort untuk data penuh")

    arr = [larik[i] for i in range(n)]
    perbandingan = 0
    pemindahan = 0

    for i in range(1, n):
        item_kunci = arr[i]
        nilai_kunci = _ambil_kunci(item_kunci, kunci)
        j = i - 1

        while j >= 0:
            perbandingan += 1
            if _ambil_kunci(arr[j], kunci) > nilai_kunci:
                arr[j + 1] = arr[j]
                pemindahan += 1
                j -= 1
            else:
                break

        arr[j + 1] = item_kunci
        pemindahan += 1

    return arr, perbandingan, pemindahan


def merge_sort(array, kunci="oid"):
    """
    Merge Sort: Membelah array menjadi dua lalu menggabungkannya secara stabil (<=).
    Kompleksitas: O(n log n) di semua kasus.
    Mengembalikan: (array_terurut, jumlah_perbandingan, jumlah_pemindahan)
    """
    n = len(array)
    if n <= 1:
        return [array[i] for i in range(n)], 0, 0

    mid = n // 2
    kiri, comp_kiri, move_kiri = merge_sort(array[:mid], kunci)
    kanan, comp_kanan, move_kanan = merge_sort(array[mid:], kunci)

    hasil = []
    i = 0
    j = 0
    perbandingan = comp_kiri + comp_kanan
    pemindahan = move_kiri + move_kanan

    # Gabungkan kedua bagian terurut
    while i < len(kiri) and j < len(kanan):
        perbandingan += 1
        # Pakai <= agar elemen kiri didahulukan saat nilai kunci sama (STABIL)
        if _ambil_kunci(kiri[i], kunci) <= _ambil_kunci(kanan[j], kunci):
            hasil.append(kiri[i])
            i += 1
        else:
            hasil.append(kanan[j])
            j += 1
        pemindahan += 1

    # Salin sisa elemen bagian kiri (jika ada)
    while i < len(kiri):
        hasil.append(kiri[i])
        i += 1
        pemindahan += 1

    # Salin sisa elemen bagian kanan (jika ada)
    while j < len(kanan):
        hasil.append(kanan[j])
        j += 1
        pemindahan += 1

    return hasil, perbandingan, pemindahan


def linear_search(array, target):
    """
    Linear Search: Menelusuri satu per satu dari depan tanpa syarat terurut.
    Kompleksitas: O(n).
    Mengembalikan: (indeks_ditemukan, jumlah_perbandingan)
    """
    perbandingan = 0
    target_str = str(target)

    for i in range(len(array)):
        perbandingan += 1
        if str(_ambil_kunci(array[i], "oid")) == target_str:
            return i, perbandingan

    return -1, perbandingan


def binary_search(array, target):
    """
    Binary Search: Membuang separuh sisa daftar setiap langkah pada data terurut.
    Kompleksitas: O(log n).
    Mengembalikan: (indeks_ditemukan, jumlah_perbandingan)
    """
    lo = 0
    hi = len(array) - 1
    perbandingan = 0
    target_str = str(target)

    while lo <= hi:
        mid = (lo + hi) // 2
        perbandingan += 1
        nilai_tengah = str(_ambil_kunci(array[mid], "oid"))

        if nilai_tengah == target_str:
            return mid, perbandingan
        elif nilai_tengah < target_str:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1, perbandingan


# ==============================================================================
# Pengujian Mandiri M3 (Checklist Siap Submit M3)
# ==============================================================================
if __name__ == "__main__":
    print("=== UJI MANDIRI M3: SORT & SEARCH ===")
    data_uji = [38, 27, 43, 9, 27, 10]

    res_ins, c_ins, m_ins = insertion_sort(data_uji)
    res_mrg, c_mrg, m_mrg = merge_sort(data_uji)
    assert res_ins == res_mrg == [9, 10, 27, 27, 38, 43], "Hasil sort tidak cocok!"
    print(f"Insertion Sort : {res_ins} ({c_ins} perbandingan, {m_ins} pemindahan)")
    print(f"Merge Sort     : {res_mrg} ({c_mrg} perbandingan, {m_mrg} pemindahan)")

    # Uji 4 kasus Binary Search (tengah, kiri, kanan, tidak ada) + larik kosong
    arr_urut = ["O-000001", "O-000002", "O-000003", "O-000004", "O-000005"]
    assert binary_search(arr_urut, "O-000003")[0] == 2  # Tengah
    assert binary_search(arr_urut, "O-000001")[0] == 0  # Kiri
    assert binary_search(arr_urut, "O-000005")[0] == 4  # Kanan
    assert binary_search(arr_urut, "O-999999")[0] == -1 # Tidak ada
    assert binary_search([], "O-000001")[0] == -1       # Larik kosong
    print("Status         : SEMUA UJI CHECKLIST M3 LOLOS!")
