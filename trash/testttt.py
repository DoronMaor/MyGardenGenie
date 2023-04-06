import tkinter as tk

def loop():
    print("asap rocky")
    root.after(1000, loop)  # schedule the next iteration after 1 second

root = tk.Tk()

# set the size and position of the window
root.geometry("400x400+100+100")

# start the loop
loop()

# start the Tkinter mainloop
root.mainloop()
