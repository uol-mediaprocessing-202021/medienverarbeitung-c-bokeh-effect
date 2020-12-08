from tkinter import *
import tkinter.font as font
from functions import func_gui
from PIL import Image, ImageTk, ImageFilter
from tkinter import filedialog
import os

topx, topy, botx, boty = 0, 0, 0, 0
rect_id = None


# Bilder öffnen
def open_image():
    global img, ori_img, panel, file_menu, x, info_label, rect_id

    # Bild laden und in canvas (panel) speichern
    x = filedialog.askopenfilename(title='Bild öffnen')
    img = Image.open(x)
    img = ImageTk.PhotoImage(img)
    ori_img = img
    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)
    panel.place(anchor="center", relx=0.5, rely=0.5)

    # Fokusbereich initialisieren
    rect_id = panel.create_rectangle(topx, topy, topx, topy, dash=(20, 20), fill='', outline='white')
    panel.bind('<Button-1>', get_mouse_posn)
    panel.bind('<B1-Motion>', update_sel_rect)

    # infoleiste updaten und speichern unter ermöglichen
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

    new_image = func_gui.covert_imgtk2img(img)
    new_image.save(y)


# bearbeitet Bild mit Gauss Filter (zum test)
def gauss():
    global panel, img
    g_img = func_gui.covert_imgtk2img(img)
    img = g_img.filter(ImageFilter.GaussianBlur(radius=5))
    img = ImageTk.PhotoImage(img)
    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)


# setzt das Bild zum Ursprung zurück
def reset():
    global panel, img, ori_img
    img = ori_img
    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)
    reset_sel_rect()


# trackt Maus position
def get_mouse_posn(event):
    global topy, topx

    topx, topy = event.x, event.y


# updated Fokusbereich
def update_sel_rect(event):
    global rect_id, panel
    global topy, topx, botx, boty

    botx, boty = event.x, event.y
    panel.coords(rect_id, topx, topy, botx, boty)  # Update selection rect.


# reset Fokusbereich zu 0
def reset_sel_rect():
    global rect_id, panel
    panel.delete(rect_id)
    rect_id = panel.create_rectangle(topx, topy, topx, topy, dash=(20, 20), fill='', outline='white')
    panel.bind('<Button-1>', get_mouse_posn)
    panel.bind('<B1-Motion>', update_sel_rect)


# Äußeres Fenster erstellen
root = Tk()
root.iconbitmap('images/camera.ico')
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

res = Image.open("images/reset.png")
res = res.resize((35, 35), Image.ANTIALIAS)
res = ImageTk.PhotoImage(res)

# reserviere Speicherplatz für zu bearbeitendes Bild und kopie für reset
img = ImageTk.PhotoImage(Image.open('images/placeholder.png'))
ori_img = img
x = ' '

# Label für Bilddarstellung
panel = Canvas(main_frame)
panel.img = img

# Buttons für Effekte erstellen
title_font = font.Font(family='Arial', size=16, weight='bold')

options_label = Label(tool_frame, text="Effekte", background="#2c2f33", fg="white", font=title_font)
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

fokus_reset = Button(tool_frame, image=res, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                     font=title_font, fg="white", command=reset_sel_rect)
fokus_reset.pack(padx=35, pady=35, fill=BOTH, side=BOTTOM)

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

# Schleife die auf Nutzerinput wartet
root.mainloop()
