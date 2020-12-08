from tkinter import *
import tkinter.font as font
from functions import func_gui
from PIL import Image, ImageTk, ImageFilter
from tkinter import filedialog
import os


# Bilder öffnen
def open_image():
    global img, ori_img, panel, file_menu, x, info_label

    x = filedialog.askopenfilename(title='Bild öffnen')
    img = Image.open(x)
    img = ImageTk.PhotoImage(img)
    ori_img = img
    panel.config(image=img)
    panel.image = img
    panel.place(anchor="center", relx=0.5, rely=0.5)
    info_label.config(text="Datei: " + x + " | " + "Size: " + str(img.height()) + ' x ' + str(img.width()))
    file_menu.entryconfig("Speichern unter ...", state="normal")


# Bilder speichern
def save_image():
    global img, panel, x

    y = filedialog.asksaveasfilename(title='Bild speichern unter', filetypes=(
                ("PNG Datei (*.png)", "*.png"),
                ("JPEG Datei (*.jpeg)", "*.jpeg"),
                ("GIF Datei (*.gif)", "*.gif"),
                ("Alle Dateien", "*.*"),
            ), defaultextension='.png', initialfile=os.path.basename(x))

    new_image = func_gui.covert_imgtk2img(panel)
    new_image.save(y)


# bearbeitet Bild mit Gauss Filter (zum test)
def gauss():
    global panel, img
    g_img = func_gui.covert_imgtk2img(panel)
    img = g_img.filter(ImageFilter.GaussianBlur(radius=5))
    img = ImageTk.PhotoImage(img)
    panel.config(image=img)
    panel.image = img


# setzt das Bild zum Ursprung urück
def reset():
    global panel, img, ori_img
    img = ori_img
    panel.config(image=img)
    panel.image = img


# Äußeres Fenster erstellen
root = Tk()
root.title("Bokeh Effekt")
root.config(background="#99aab5")

# Innere Fenster erstellen
info_frame = Frame(root, width=700, height=20, background="#23272a")
info_frame.pack(side=BOTTOM, fill=BOTH)

tool_frame = Frame(root, width=200, background="#2c2f33")
tool_frame.pack(side=LEFT, fill=BOTH)

main_frame = Frame(root, width=500, height=500, background="#3a3e43")
main_frame.pack(side=LEFT, fill=BOTH, expand=True)

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

# Label für Bilddarstellung
panel = Label(main_frame)

# Buttons für Effekte erstellen
title_font = font.Font(family='Arial', size=16, weight='bold')

options_label = Label(tool_frame, text="Effekte", background="#2c2f33", fg="white")
options_label.config(font=title_font)
options_label.pack(pady=10)

no_button = Button(tool_frame, image=noe, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                   command=reset)
no_button.pack(padx=35, pady=35, fill=BOTH)

ring_button = Button(tool_frame, image=ring, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                     command=gauss)
ring_button.pack(padx=35, pady=35, fill=BOTH)

star_button = Button(tool_frame, image=star, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                     command=gauss)
star_button.pack(padx=35, pady=35, fill=BOTH)

square_button = Button(tool_frame, image=sqr, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                       command=gauss)
square_button.pack(padx=35, pady=35, fill=BOTH)

# label für Bildinfo erstellen
info_label = Label(info_frame, background="#23272a", fg="white")
info_label.pack(side=RIGHT)
version_label = Label(info_frame, background="#23272a", text="Version: Alpha 0.01", fg="white").pack(side=LEFT)

# Menü erstellen
menu = Menu(root)

# Reiter für das Menü erstellen
file_menu = Menu(menu, tearoff=0)
help_menu = Menu(menu, tearoff=0)

# Unterreiter für 'Datei'
file_menu.add_command(label="Neu ...")
file_menu.add_command(label="Öffnen ...", command=open_image)
file_menu.add_command(label="Speichern unter ...", command=save_image, state="disabled")
file_menu.add_separator()
file_menu.add_command(label="Beenden", command=root.quit)
menu.add_cascade(label="Datei", menu=file_menu)

# Unterreiter für 'Hilfe'
help_menu.add_command(label="Über das Projekt", command=func_gui.help_about)
help_menu.add_command(label="Tutorial", command=func_gui.help_tut)
menu.add_cascade(label="Hilfe", menu=help_menu)

root.config(menu=menu)

# reserviere Speicherplatz für zu bearbeitendes Bild und kopie für reset
img = ImageTk.PhotoImage(Image.open('images/placeholder.png'))
ori_img = img
x = ' '

# Schleife die auf Nutzerinput wartet
root.mainloop()
