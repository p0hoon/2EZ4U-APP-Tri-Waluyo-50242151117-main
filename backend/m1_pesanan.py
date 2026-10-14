class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Array:
    """Dynamic Array dengan alokasi memori berlipat 2x saat penuh."""
    def __init__(self, initial_capacity=4):
        self.capacity = initial_capacity
        self.size = 0
        self.data = [None] * self.capacity

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_cap

    def get(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("Indeks di luar rentang.")
        return self.data[i]

    def append(self, v):
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.size] = v
        self.size += 1

    def insert(self, i, v):
        if i < 0 or i > self.size:
            raise IndexError("Indeks tidak valid.")
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        for j in range(self.size, i, -1):
            self.data[j] = self.data[j - 1]
        self.data[i] = v
        self.size += 1

    def delete(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("Indeks di luar rentang.")
        val = self.data[i]
        for j in range(i, self.size - 1):
            self.data[j] = self.data[j + 1]
        self.data[self.size - 1] = None
        self.size -= 1
        return val

    # Pembungkus aturan bisnis M1
    def tambah_reguler(self, v):
        self.append(v)

    def tambah_prioritas(self, v):
        self.insert(self.size // 2, v)

    def tambah_vip(self, v):
        self.insert(0, v)

    def __len__(self):
        return self.size


class LinkList:
    """Singly Linked List dengan penunjuk head dan tail."""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def get(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("Indeks di luar rentang.")
        curr = self.head
        for _ in range(i):
            curr = curr.next
        return curr.data

    def append(self, v):
        node = Node(v)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def insert(self, i, v):
        if i < 0 or i > self.size:
            raise IndexError("Indeks tidak valid.")
        if i == 0:
            node = Node(v)
            node.next = self.head
            self.head = node
            if self.tail is None:
                self.tail = node
            self.size += 1
            return
        if i == self.size:
            self.append(v)
            return

        node = Node(v)
        curr = self.head
        for _ in range(i - 1):
            curr = curr.next
        node.next = curr.next
        curr.next = node
        self.size += 1

    def delete(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("Indeks di luar rentang.")
        if i == 0:
            val = self.head.data
            self.head = self.head.next
            self.size -= 1
            if self.size == 0:
                self.tail = None
            return val

        curr = self.head
        for _ in range(i - 1):
            curr = curr.next
        val = curr.next.data
        curr.next = curr.next.next
        if i == self.size - 1:
            self.tail = curr
        self.size -= 1
        return val

    # Pembungkus aturan bisnis M1
    def tambah_reguler(self, v):
        self.append(v)

    def tambah_prioritas(self, v):
        self.insert(self.size // 2, v)

    def tambah_vip(self, v):
        self.insert(0, v)

    def __len__(self):
        return self.size