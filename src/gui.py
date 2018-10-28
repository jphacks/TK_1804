from tkinter import *
from tkinter import ttk
from tkinter import messagebox as tkMessageBox
from tkinter import filedialog as tkFileDialog
import os
import subprocess

def play():
    args = ["python", "./src/process.py", filename.get()]
    subprocess.call(args)
    print('Play %s' % filename.get())

def pick():
    print('pick a audio file')
    fTyp = [('wavファイル', '*.wav'), ('mp3ファイル', '*.mp3')]
    iDir = '/home/Documents'
    filename.set(tkFileDialog.askopenfilename(filetypes = fTyp, initialdir = iDir))
    print(filename.get())

root = Tk()
root.title('surroundify')
frame1 = ttk.Frame(root)
frame2 = ttk.Frame(frame1)

filename = StringVar()

logo = PhotoImage(file = './src/assets/logo.gif')
canvas1 = Canvas(frame1, width=500, height=500, bg='#15738c')
canvas1.create_image(250, 250, image=logo)
entry1 = ttk.Entry(frame2, textvariable=filename)
button1 = ttk.Button(frame2, text='pick a audio file', command=pick)
button2 = ttk.Button(frame2, text='play', command=play)

frame1.grid(row=0, column=0, sticky=(N,E,S,W))
canvas1.grid(row=1, column=1, sticky=E)
frame2.grid(row=1, column=2, sticky=W)
entry1.grid(row=1, column=1, sticky=E)
button1.grid(row=1, column=2, sticky=W)
button2.grid(row=2, column=1, sticky=S)

for child in frame1.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.mainloop()
