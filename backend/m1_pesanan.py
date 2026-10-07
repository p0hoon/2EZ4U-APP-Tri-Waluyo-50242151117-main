import time
import tkinter as tk
from tkinter import messagebox

#Array Dinamis
class ArrayPesanan:
    def __init__(self):
        self.cap, self.n = 4, 0
        self.data = [None] * self.cap

    def _besar(self):
        baru = [None] * (self.cap * 2)
        for i in range(self.n):
            baru[i] = self.data[i]
        self.data, self.cap = baru,self.cap *2

    def _sisip(self, pos, x):
        if self.n == self.cap:
            self._besar()
        for k in range(self.n, pos, -1):
            self.data[k] = self.data[k-1]
        self.data[pos] = x
        self.n += 1

    def lihat(self, i):
        return self.data[i]
    def reguler(self, x):
        self._sisip(self.n, x)
    def prioritas(self, x):
        self._sisip(self.n // 2, x)
    def vip(self, x):
        self._sisip(0, x)

    def hapus(self, i):
        x = self.data[i]
        for k in range(i, self.n - 1):
            self.data[k] = self.data[k + 1]
        self.n -= 1
        self.data[self.n] = None
        return x

    def awal(self, k):
        return [self.data[i] for i in range(min(k, self.n))]

#Singly Linked List
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedPesanan:
    def __init__(self):
        self.head = self.tail = None
        self.n = 0

    def tambah(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            self.n += 1
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node
        self.tail = new_node
        self.n += 1

    def hapus(self, key):
        temp = self.head
        if temp is not None:
            if temp.data == key:
                self.head = temp.next
                temp = None
                self.n -= 1
                return
        while temp is not None:
            if temp.data == key:
                break
            prev = temp
            temp = temp.next
        if temp is None:
            return
        prev.next = temp.next
        temp = None
        self.n -= 1

    def tampilkan(self):
        current = self.head
        while current:
            print(current.data)
            current = current.next
