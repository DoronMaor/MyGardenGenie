import tkinter as tk

def expand_window():
    root.geometry("400x300")

root = tk.Tk()

button = tk.Button(root, text="Click me!", bg="#4CAF50", fg="white", padx=20, pady=10, font=("Segoe UI", 14), borderwidth=0, highlightthickness=0, activebackground="#43A047", activeforeground="white", relief="flat", command=expand_window)
button.pack()

root.geometry("400x100")
root.mainloop()
