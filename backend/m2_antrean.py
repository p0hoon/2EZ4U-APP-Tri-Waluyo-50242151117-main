class Pesanan:
    """Model data pesanan murni tanpa dictionary."""
    def __init__(self, oid, pelanggan, resto="kafe-teknik", menu="roti-bakar",
                 harga=12000, prioritas=2, masuk="00:00:00", selesai="-", status="ANTRE"):
        self.oid = str(oid)
        self.pelanggan = str(pelanggan)
        self.resto = str(resto)
        self.menu = str(menu)
        self.harga = int(harga)
        self.prioritas = int(prioritas)
        self.masuk = str(masuk)
        self.selesai = str(selesai)
        self.status = str(status)


class stack:
    """Implementasi Stack (LIFO)."""
    def __init__(self):
        self.items = []

    def push(self, x):
        self.items.append(x)

    def pop(self):
        return self.items.pop() if len(self.items) > 0 else None

    def peek(self):
        return self.items[-1] if len(self.items) > 0 else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def to_string(self):
        if len(self.items) == 0:
            return "kosong"
        return " ".join([str(x) for x in self.items])


class QueueNaive:
    """Antrean Naif: Dequeue mengambil indeks 0 dan menggeser sisa elemen (O(n))."""
    def __init__(self):
        self.items = []
        self.total_geseran = 0

    def enqueue(self, x):
        self.items.append(x)

    def dequeue(self):
        if len(self.items) == 0:
            return None
        depan = self.items[0]
        self.total_geseran += (len(self.items) - 1)
        self.items = [self.items[i] for i in range(1, len(self.items))]
        return depan

    def undo_dequeue_prepend(self, x):
        self.items.insert(0, x)

    def undo_enqueue_pop(self):
        return self.items.pop() if len(self.items) > 0 else None

    def __len__(self):
        return len(self.items)


class QueueCircular:
    """Antrean Melingkar (Modulo): Operasi Enqueue & Dequeue instan O(1)."""
    def __init__(self, capacity=32768):
        self.capacity = capacity
        self.data = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self.count):
            new_data[i] = self.data[(self.front + i) % self.capacity]
        self.data = new_data
        self.front = 0
        self.rear = self.count
        self.capacity = new_cap

    def enqueue(self, x):
        if self.count == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.capacity
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        val = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return val

    def undo_dequeue_prepend(self, x):
        if self.count == self.capacity:
            self._resize(self.capacity * 2)
        self.front = (self.front - 1 + self.capacity) % self.capacity
        self.data[self.front] = x
        self.count += 1

    def undo_enqueue_pop(self):
        if self.count == 0:
            return None
        self.rear = (self.rear - 1 + self.capacity) % self.capacity
        val = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return val

    def __len__(self):
        return self.count


# Alias penamaan
queue = QueueCircular


# --- Bagian Kasir (Infix ke Postfix) ---

def tokenize(expr):
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c in ' \t':
            i += 1
            continue
        if c in '+-*/()':
            tokens.append(c)
            i += 1
        elif c.isdigit():
            num = ""
            while i < n and expr[i].isdigit():
                num += expr[i]
                i += 1
            tokens.append(num)
        else:
            i += 1
    return tokens


def _precedence(op):
    if op in ('+', '-'):
        return 1
    if op in ('*', '/'):
        return 2
    return 0


def ke_postfix(expr):
    tokens = tokenize(expr)
    st = stack()
    out = []
    steps = []
    no = 1
    for tok in tokens:
        step_id = f"1.{no}"
        no += 1
        if tok.isdigit():
            out.append(tok)
            steps.append((step_id, tok, "operand, langsung ke output", st.to_string(), " ".join(out)))
        elif tok == '(':
            st.push(tok)
            steps.append((step_id, tok, "push ( ke stack", st.to_string(), " ".join(out)))
        elif tok == ')':
            while not st.is_empty() and st.peek() != '(':
                out.append(st.pop())
            if not st.is_empty() and st.peek() == '(':
                st.pop()
            steps.append((step_id, tok, "pop sampai (, lalu buang (", st.to_string(), " ".join(out)))
        else:
            act = f"push {tok}"
            if not st.is_empty() and _precedence(st.peek()) >= _precedence(tok) and st.peek() != '(':
                act = f"pop {st.peek()}, lalu push {tok}"
            while not st.is_empty() and _precedence(st.peek()) >= _precedence(tok) and st.peek() != '(':
                out.append(st.pop())
            st.push(tok)
            steps.append((step_id, tok, act, st.to_string(), " ".join(out)))

    while not st.is_empty():
        out.append(st.pop())
    steps.append(("1.akhir", "-", "pop sisa stack:", st.to_string(), " ".join(out)))
    return out, steps


def hitung(postfix_tokens):
    st = stack()
    steps = []
    no = 1
    for tok in postfix_tokens:
        step_id = f"2.{no}"
        no += 1
        if tok.isdigit():
            st.push(int(tok))
            steps.append((step_id, tok, f"operand, push {tok}", st.to_string(), str(st.peek())))
        else:
            b = st.pop()
            a = st.pop()
            if tok == '+': res = a + b
            elif tok == '-': res = a - b
            elif tok == '*': res = a * b
            elif tok == '/': res = a // b if b != 0 else 0
            st.push(res)
            steps.append((step_id, tok, f"pop {b} dan {a} -> {a}{tok}{b} = {res}", st.to_string(), str(res)))

    total = st.pop() if not st.is_empty() else 0
    return total, steps


class UndoRedoManager:
    """Manajer riwayat aksi undo/redo."""
    def __init__(self, q_naive, q_circular):
        self.q_naive = q_naive
        self.q_circular = q_circular
        self.undo_stack = stack()
        self.redo_stack = stack()

    def catat_aksi(self, tipe, items):
        self.undo_stack.push((tipe, items))
        self.redo_stack = stack()

    def undo_last(self):
        if self.undo_stack.is_empty():
            return None
        aksi = self.undo_stack.pop()
        tipe, items = aksi
        if tipe == "ENQUEUE":
            self.q_naive.undo_enqueue_pop()
            self.q_circular.undo_enqueue_pop()
        elif tipe == "DEQUEUE":
            for i in range(len(items) - 1, -1, -1):
                self.q_naive.undo_dequeue_prepend(items[i])
                self.q_circular.undo_dequeue_prepend(items[i])
        self.redo_stack.push(aksi)
        return aksi

    def redo_last(self):
        if self.redo_stack.is_empty():
            return None
        aksi = self.redo_stack.pop()
        tipe, items = aksi
        if tipe == "ENQUEUE":
            for x in items:
                self.q_naive.enqueue(x)
                self.q_circular.enqueue(x)
        elif tipe == "DEQUEUE":
            for _ in range(len(items)):
                self.q_naive.dequeue()
                self.q_circular.dequeue()
        self.undo_stack.push(aksi)
        return aksi


def baca_csv_pesanan(filepath="data/pesanan.csv", limit=20000):
    """Membaca CSV tanpa dict/set bawaan."""
    hasil = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for idx in range(1, len(lines)):
                if len(hasil) >= limit:
                    break
                baris = lines[idx].strip()
                if not baris:
                    continue
                k = baris.split(",")
                if len(k) >= 2:
                    p = Pesanan(
                        oid=k[0],
                        pelanggan=k[1],
                        resto=k[2] if len(k) > 2 else "kafe-teknik",
                        menu=k[3] if len(k) > 3 else "roti-bakar",
                        harga=int(k[4]) if len(k) > 4 and k[4].isdigit() else 12000,
                        prioritas=int(k[5]) if len(k) > 5 and k[5].isdigit() else 2,
                        masuk=k[6] if len(k) > 6 else "00:00:00"
                    )
                    hasil.append(p)
    except FileNotFoundError:
        # Fallback pembuatan data otomatis jika file CSV belum ditaruh
        for i in range(1, limit + 1):
            hasil.append(Pesanan(f"O-{i:06d}", f"Pelanggan-{i}"))
    return hasil