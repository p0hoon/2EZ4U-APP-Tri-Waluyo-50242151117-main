# test_m2.py
from backend.m2_antrean import (
    Pesanan, QueueNaive, QueueCircular, 
    ke_postfix, hitung, UndoRedoManager
)

print("--- 1. UJI STACK KASIR (INFIX -> POSTFIX -> EVALUASI) ---")
expr = "( 3 * 12000 ) + ( 2 * 8500 ) - 5000"
postfix, steps_conv = ke_postfix(expr)
total, steps_eval = hitung(postfix)
print(f"Infix   : {expr}")
print(f"Postfix : {' '.join(postfix)}")
print(f"Total   : Rp {total:,}")
assert total == 48000, "Perhitungan kasir keliru!"
print("Status  : KASIR POSTFIX VALID!\n")

print("--- 2. UJI ANTREAN MELINGKAR (CIRCULAR QUEUE K=4) ---")
cq = QueueCircular(capacity=4)
cq.enqueue("A")
cq.enqueue("B")
cq.enqueue("C")
assert cq.dequeue() == "A"
assert cq.dequeue() == "B"
cq.enqueue("D")
cq.enqueue("E")  # Penunjuk berputar kembali ke indeks 0
print(f"Front: {cq.front}, Rear: {cq.rear}, Count: {cq.count}")
assert cq.dequeue() == "C"
assert cq.dequeue() == "D"
assert cq.dequeue() == "E"
assert cq.dequeue() is None
print("Status  : CIRCULAR QUEUE VALID!\n")

print("--- 3. UJI UNDO & REDO MANAGER ---")
qn = QueueNaive()
qc = QueueCircular()
mgr = UndoRedoManager(qn, qc)

p1 = Pesanan("O-101", "Ani")
qn.enqueue(p1)
qc.enqueue(p1)
mgr.catat_aksi_baru("ENQUEUE", [p1])

# Batalkan enqueue
mgr.undo_last()
assert len(qn) == 0 and len(qc) == 0, "Gagal membatalkan Enqueue!"

# Kerjakan ulang enqueue
mgr.redo_last()
assert len(qn) == 1 and len(qc) == 1, "Gagal mengulang Enqueue!"
print("Status  : SISTEM UNDO & REDO VALID!")