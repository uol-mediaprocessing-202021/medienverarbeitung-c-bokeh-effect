from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
from tkinter import filedialog
import tkinter.font as font


# Text für Punkt 'Über das Projekt' im Reiter Hilfe
def help_about():
    about_text = "\
Projekt: Medienverarbeitung Gruppe C\n\
Carl-von-Ossietzky Universität Oldenburg\n\
Authors: Jona Schrader, Roman Kammer, Malte Trauernicht\n\
Version: alpha 0.01"
    messagebox.showinfo(message=about_text, title="Über das Projekt")


# Bilder öffnen
def open_image():
    x = filedialog.askopenfilename(title='Bild öffnen')
    global img, ori_img
    img = Image.open(x)
    img = ImageTk.PhotoImage(img)
    ori_img = img
    panel = Label(main_frame, image=img, highlightbackground="black", highlightthickness=1)
    panel.image = img
    panel.place(anchor="center", relx=0.5, rely=0.5)


# Bilder speichern
def save_image():
    y = filedialog.asksaveasfilename(title='Bild speichern unter', defaultextension='.png')
    global img
    print(img.width())
    print(y)


# Äußeres Fenster erstellen
root = Tk()
root.title("Bokeh Effekt")
root.config(background="#474747")

# Innere Fenster erstellen
main_frame = Frame(root, width=500, height=500, background="#5c5c5c", highlightbackground="black", highlightthickness=1)
main_frame.pack(side=LEFT, padx=1, pady=1, fill=BOTH, expand=True)

tool_frame = Frame(root, background="#454545", highlightbackground="black", highlightthickness=1)
tool_frame.pack(side=LEFT, padx=1, pady=1, fill=BOTH)

# Icons für Buttons laden
noe = Image.open("images/nothing.png")
noe = noe.resize((35, 35), Image.ANTIALIAS)
noe = ImageTk.PhotoImage(noe)

ring = Image.open("images/rings.png")
ring = ring.resize((35, 35), Image.ANTIALIAS)
ring = ImageTk.PhotoImage(ring)

star = Image.open("images/stars.png")
star = star.resize((35, 35), Image.ANTIALIAS)
star = ImageTk.PhotoImage(star)

sqr = Image.open("images/squares.png")
sqr = sqr.resize((35, 35), Image.ANTIALIAS)
sqr = ImageTk.PhotoImage(sqr)

# Buttons für Effekte erstellen
title_font = font.Font(family='Arial', size=16, weight='bold')

options_label = Label(tool_frame, text="Effekte", background="#454545", fg="white")
options_label.config(font=title_font)
options_label.pack(pady=10)

no_button = Button(tool_frame, image=noe, background="#454545", borderwidth=0, activebackground="#454545")
no_button.pack(padx=30, pady=30, fill=BOTH)

ring_button = Button(tool_frame, image=ring, background="#454545", borderwidth=0, activebackground="#454545")
ring_button.pack(padx=30, pady=30, fill=BOTH)

star_button = Button(tool_frame, image=star, background="#454545", borderwidth=0, activebackground="#454545")
star_button.pack(padx=30, pady=30, fill=BOTH)

square_button = Button(tool_frame, image=sqr, background="#454545", borderwidth=0, activebackground="#454545")
square_button.pack(padx=30, pady=30, fill=BOTH)

# Menü erstellen
menu = Menu(root)

# Reiter für das Menü erstellen
file_menu = Menu(menu, tearoff=0)
help_menu = Menu(menu, tearoff=0)

# Unterreiter für 'Datei'
file_menu.add_command(label="Neu ...")
file_menu.add_command(label="Bild öffnen ...", command=open_image)
file_menu.add_command(label="Bild speichern unter ...", command=save_image)
file_menu.add_separator()
file_menu.add_command(label="Beenden", command=root.quit)
menu.add_cascade(label="Datei", menu=file_menu)

# Unterreiter für 'Hilfe'
help_menu.add_command(label="Über das Projekt", command=help_about)
menu.add_cascade(label="Hilfe", menu=help_menu)

root.config(menu=menu)

# reserviere Speicherplatz für zu bearbeitendes Bild und kopie für reset
img = ImageTk.PhotoImage(Image.open("images/placeholder.png"))
ori_img = img

# Schleife die auf Nutzerinput wartet
root.mainloop()
