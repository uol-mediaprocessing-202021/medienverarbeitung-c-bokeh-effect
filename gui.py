from tkinter import *
from tkinter.ttk import Progressbar
import tkinter.font as font
from functions import func_gui
from detection import pool
from detection import torch
from PIL import Image, ImageTk
from tkinter import filedialog
from queue import Queue
import os
import time

topx, topy, botx, boty = 0, 0, 0, 0
rect_id = None


# Bilder öffnen
def open_image():
    global img, ori_img, x, rect_id
    global panel, file_menu, info_label
    global auto_mode, focus_mode

    # Bild laden und in canvas (panel) speichern
    x = filedialog.askopenfilename(title='Bild öffnen')
    img = Image.open(x)
    img = ImageTk.PhotoImage(img)
    ori_img = img
    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)
    panel.place(anchor="center", relx=0.5, rely=0.5)

    # infoleiste updaten und speichern unter ermöglichen
    info_label.config(text="Datei: " + x + " | " + "Size: " + str(img.height()) + ' x ' + str(img.width()))

    file_menu.entryconfig("Speichern unter ...", state="normal")
    auto_mode.config(state="normal", background="#23272a")
    focus_mode.config(state="normal")


# Bilder speichern
def save_image():
    global img, panel, x

    y = filedialog.asksaveasfilename(title='Bild speichern unter', filetypes=(
        ("PNG Datei (*.png)", "*.png"),
        ("JPEG Datei (*.jpeg)", "*.jpeg"),
        ("Alle Dateien", "*.*"),
    ), defaultextension=os.path.splitext(x), initialfile=os.path.basename(x))

    new_image = func_gui.covert_imgtk2img(img)
    new_image.save(y)


# bearbeitet Bild mit Torch
def blur():
    global x, img, edge_var, scale_var, info_frame, version_label

    que = Queue()
    try:
        image_thread = func_gui.IPThread(1, "IP_Thread", edge_var.get(), x, scale_var.get(), que)
        image_thread.start()
    except KeyboardInterrupt:
        print("[MAIN][Error] unable to start ObstacleDetection_Thread")
        time.sleep(1)

    version_label.config(text=" ")
    progress = Progressbar(info_frame, orient=HORIZONTAL, length=100, mode='indeterminate')
    progress.pack(side=LEFT, pady=2)
    func_gui.bar(progress, info_frame)

    blur_img = que.get()
    img = ImageTk.PhotoImage(Image.fromarray(blur_img))

    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    progress.destroy()
    version_label.config(text="Version: Alpha 0.01")

    auto_mode.config(state="disabled", background="#2c2f33")
    focus_mode.config(state="disabled", background="#2c2f33")


# setzt das Bild zum Ursprung zurück
def reset_image():
    global panel, img, ori_img
    img = ori_img
    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)
    activate_auto_mode()

    auto_mode.config(state="normal")
    focus_mode.config(state="normal")


# setzt Einstellungen zurück
def reset_setup():
    global edge_var, scale_var
    edge_var.set(0)
    scale_var.set(0)


# trackt Maus position
def get_mouse_posn(event):
    global topy, topx

    topx, topy = event.x, event.y


# updated Fokusbereich
def update_sel_rect(event):
    global rect_id, panel
    global topy, topx, botx, boty

    botx, boty = event.x, event.y
    panel.coords(rect_id, topx, topy, botx, boty)


# wechsel zu fokus Modus
def activate_focus_mode():
    global rect_id, panel
    panel.delete(rect_id)
    rect_id = panel.create_rectangle(topx, topy, topx, topy, dash=(20, 20), fill='', outline='white')
    panel.bind('<Button-1>', get_mouse_posn)
    panel.bind('<B1-Motion>', update_sel_rect)

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#23272a")


# wechsel zum Auto Modus
def activate_auto_mode():
    global rect_id, panel
    global topy, topx, botx, boty

    panel.delete(rect_id)

    auto_mode.config(background="#23272a")
    focus_mode.config(background="#2c2f33")


# Äußeres Fenster erstellen
root = Tk()
root.iconbitmap('images/camera.ico')
root.title("Bokeh Effekt")
root.config(background="#99aab5")

# Innere Fenster erstellen
info_frame = Frame(root, width=720, height=30, background="#23272a")
info_frame.pack(side=BOTTOM, fill=BOTH)

tool_frame = Frame(root, width=220, background="#2c2f33")
tool_frame.pack(side=LEFT, fill=BOTH)

main_frame = Frame(root, width=500, height=500, background="#3a3e43")
main_frame.pack(side=LEFT, fill=BOTH, expand=True)

# Icons für Buttons laden
noe = ImageTk.PhotoImage(Image.open("images/nothing.png").resize((35, 35), Image.ANTIALIAS))
ring = ImageTk.PhotoImage(Image.open("images/rings.png").resize((35, 35), Image.ANTIALIAS))
star = ImageTk.PhotoImage(Image.open("images/stars.png").resize((35, 35), Image.ANTIALIAS))
sqr = ImageTk.PhotoImage(Image.open("images/squares.png").resize((35, 35), Image.ANTIALIAS))
foc = ImageTk.PhotoImage(Image.open("images/focus.png").resize((35, 35), Image.ANTIALIAS))
auto = ImageTk.PhotoImage(Image.open("images/auto.png").resize((35, 35), Image.ANTIALIAS))

# reserviere Speicherplatz für zu bearbeitendes Bild und kopie für reset
x = 'images/placeholder.png'
img = ImageTk.PhotoImage(Image.open(x))
ori_img = img

# Label für Bilddarstellung
panel = Canvas(main_frame)
panel.img = img

# Buttons für Effekte erstellen
title_font = font.Font(family='Arial', size=16, weight='bold')

options_label = Label(tool_frame, text="Effekte", background="#2c2f33", fg="white", font=title_font)
options_label.pack(pady=10)

no_button = Button(tool_frame, image=noe, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                   command=reset_image)
no_button.pack(padx=25, pady=25, fill=BOTH)

ring_button = Button(tool_frame, image=ring, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                     command=blur)
ring_button.pack(padx=25, pady=25, fill=BOTH)

star_button = Button(tool_frame, image=star, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                     command=blur)
star_button.pack(padx=25, pady=25, fill=BOTH)

square_button = Button(tool_frame, image=sqr, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                       command=blur)
square_button.pack(padx=25, pady=25, fill=BOTH)

# Buttons für Modi erstellen
focus_mode = Button(tool_frame, image=foc, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                    font=title_font, fg="white", command=activate_focus_mode, state=DISABLED, relief="sunken",
                    height=40, width=40)
focus_mode.pack(side=BOTTOM, padx=25, pady=25, fill=BOTH)

auto_mode = Button(tool_frame, image=auto, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                   font=title_font, fg="white", state=DISABLED, command=activate_auto_mode, relief="sunken",
                   height=40, width=40)
auto_mode.pack(side=BOTTOM, padx=25, pady=25, fill=BOTH)

options_label = Label(tool_frame, text="Modi", background="#2c2f33", fg="white", font=title_font)
options_label.pack(pady=10, side=BOTTOM)

# label für Bildinfo erstellen
info_label = Label(info_frame, background="#23272a", fg="white")
info_label.pack(side=RIGHT, padx=2, pady=5)
version_label = Label(info_frame, background="#23272a", text="Version: Alpha 0.01", fg="white")
version_label.pack(side=LEFT, padx=2, pady=5)

# Menü erstellen
menu = Menu(root)

# Reiter für das Menü erstellen
file_menu = Menu(menu, tearoff=0)
help_menu = Menu(menu, tearoff=0)
setup_menu = Menu(menu, tearoff=0)

edge_menu = Menu(setup_menu, tearoff=0)
scale_menu = Menu(setup_menu, tearoff=0)

# Unterreiter für 'Datei'
file_menu.add_command(label="Neu ...")
file_menu.add_command(label="Öffnen ...", command=open_image)
file_menu.add_command(label="Speichern unter ...", command=save_image, state="disabled")
file_menu.add_separator()
file_menu.add_command(label="Beenden", command=root.quit)
menu.add_cascade(label="Datei", menu=file_menu)

# Unterreiter für 'Einstellungen'
edge_var = IntVar()
edge_menu.add_radiobutton(label="PyTorch with PoolNET", value=0, variable=edge_var)
edge_menu.add_radiobutton(label="PyTorch only", value=1, variable=edge_var)
edge_var.set(0)
setup_menu.add_cascade(label="Kantenerkennung", menu=edge_menu)

scale_var = IntVar()
scale_menu.add_radiobutton(label="An", value=0, variable=scale_var)
scale_menu.add_radiobutton(label="Aus", value=1, variable=scale_var)
scale_var.set(0)
setup_menu.add_cascade(label="Maske skalieren", menu=scale_menu)

setup_menu.add_separator()
setup_menu.add_command(label="Einstellungen zurücksetzen", command=reset_setup)
menu.add_cascade(label="Einstellungen", menu=setup_menu)

# Unterreiter für 'Hilfe'
help_menu.add_command(label="Über das Projekt", command=func_gui.help_about)
help_menu.add_command(label="Tutorial", command=func_gui.help_tut)
menu.add_cascade(label="Hilfe", menu=help_menu)

root.config(menu=menu)

# Schleife die auf Nutzerinput wartet
root.mainloop()
