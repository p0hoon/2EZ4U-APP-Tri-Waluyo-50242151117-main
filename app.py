# ==============================================================================
# Proyek: 2EZ4U Food Delivery Desktop App (EC234303)
# File: app.py (Main Entry Point)
# ==============================================================================

import tkinter as tk
from frontend.ui import AppUI

if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()