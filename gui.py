import os
import time
import tkinter.font as font
from queue import Queue
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar, Separator

import cv2
import numpy
from PIL import Image, ImageTk

from detection import slic, blur
from functions import func_gui, global_vars


# Bilder öffnen
def open_image():
    global img, ori_img, x, blur_img, sec_edit
    global panel, file_menu, info_label
    global ori_resize

    # Bild laden und in canvas (panel) speichern
    x = filedialog.askopenfilename(title='Bild öffnen')
    img = Image.open(x)
    ori_img = ImageTk.PhotoImage(img)

    # Bild bei bedarf resizen und in PhotoImage convertieren
    img = resize_image(img)
    ori_resize = img
    img = ImageTk.PhotoImage(img)

    # Bild in der Anwendung anzeigen
    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)
    panel.place(anchor="center", relx=0.5, rely=0.5)

    blur_img = blur.bokeh(cv2.imread(x))
    sec_edit = cv2.imread(x)

    # infoleiste updaten und speichern unter ermöglichen
    info_label.config(text="Datei: " + x + " | " + "Size: " + str(img.height()) + ' x ' + str(img.width()))

    file_menu.entryconfig("Speichern unter ...", state="normal")


# Bilder speichern
def save_image():
    global img, x

    # Benutzer sucht pfad und name zum speichern aus
    y = filedialog.asksaveasfilename(title='Bild speichern unter', filetypes=(
        ("PNG Datei (*.png)", "*.png"),
        ("JPEG Datei (*.jpeg)", "*.jpeg"),
        ("Alle Dateien", "*.*"),
    ), defaultextension=os.path.splitext(x), initialfile=os.path.basename(x))

    # Konvertiere in speicherbares Dateiformat und speichere
    new_image = func_gui.covert_imgtk2img(img)
    new_image.save(y)


# bearbeitet Bild mit Torch oder PoolNet
def blur_image():
    global x, img, edge_var, scale_var, info_frame, version_label
    global auto_mode, focus_mode

    auto_mode.config(background="#23272a")
    focus_mode.config(background="#2c2f33")

    que = Queue()

    # erstellt einen Thread auf dem die Bildbearbeitung statt findet
    try:
        image_thread = func_gui.IPThread(edge_var.get(), x, scale_var.get(), que)
        image_thread.start()
    except KeyboardInterrupt:
        print("[Error] unable to start ImageProcessing_Thread")
        time.sleep(1)

    # zeige Ladebalken an, damit Benuter weiß, dass der Algorithmus ausgeführt wird
    version_label.config(text=" ")
    progress = Progressbar(info_frame, orient=HORIZONTAL, length=75, mode='indeterminate')
    progress.pack(side=LEFT)
    func_gui.bar(progress, info_frame)

    # hohle das fertige Bild aus der que und konvertiere es in PhotoImage
    if not que.empty():
        result = Image.fromarray(cv2.cvtColor(que.get(), cv2.COLOR_BGR2RGB))
        result = resize_image(result)
        img = ImageTk.PhotoImage(result)

    # zeige fertiges Bild an
    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    progress.destroy()
    version_label.config(text="Version: " + global_vars.version)

    global_vars.progress_bar_check = False

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#2c2f33")


# setzt das Bild zum Ursprung zurück
def reset_image():
    global panel, img, ori_img, ori_resize
    global blur_img, sec_edit

    img = ori_img

    if (ori_img.width() >= int(win_w * 0.7)) or (ori_img.height() >= int(win_h * 0.7)):
        img = ori_resize
        img = ImageTk.PhotoImage(img)

    blur_img = blur.bokeh(cv2.imread(x))
    sec_edit = cv2.imread(x)

    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    panel.delete(rect_id)

    panel.unbind('<Button-1>')
    panel.unbind('<B1-Motion>')
    panel.unbind('<ButtonRelease-1>')

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#2c2f33")


# setzt Einstellungen zurück
def reset_setup():
    global edge_var, scale_var
    edge_var.set(0)
    scale_var.set(0)


# trackt Maus position
def get_mouse_posn(event):
    global x_start, y_start, x_end, y_end

    x_start, y_start = event.x, event.y
    x_end, y_end = event.x, event.y


# updated Fokusbereich
def update_sel_rect(event):
    global rect_id, panel, sec_edit, img, ori_img
    global x_start, y_start, x_end, y_end, slider_var, check_var

    x_end, y_end = event.x, event.y
    panel.coords(rect_id, x_start, y_start, x_end, y_end)


def blur_area(event):
    global rect_id, panel, sec_edit, img, ori_img
    global x_start, y_start, x_end, y_end, slider_var, check_var

    print(x_start, y_start, x_end, y_end)

    original_img = cv2.imread(x)

    # editiere die ausgewählten segmente
    sec_edit = slic.edit_segment(sec_edit, original_img, slider_var.get(), x_start, x_end, y_start, y_end, check_var.get())

    # konvertiere Ergebnis in PhotImage und zeige an
    result = Image.fromarray(cv2.cvtColor(sec_edit, cv2.COLOR_BGR2RGB).astype(numpy.uint8))
    result = resize_image(result)
    img = ImageTk.PhotoImage(result)

    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#2c2f33")

    panel.delete(rect_id)

    panel.unbind('<Button-1>')
    panel.unbind('<B1-Motion>')
    panel.unbind('<ButtonRelease-1>')


# wechsel zu fokus Modus
def focus_blur():
    global panel, img, x, sec_edit, rect_id, slider_var

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#23272a")

    # erstelle segmentiertes Bild für Benuzer
    cv_img = cv2.imread(x)
    seg = slic.show_segmentation(sec_edit, cv_img, slider_var.get())

    # konvertiere und zeige an
    result = Image.fromarray(cv2.cvtColor(seg, cv2.COLOR_BGR2RGB).astype(numpy.uint8))
    result = resize_image(result)
    img = ImageTk.PhotoImage(result)

    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    # zeichne Rechteck um Maus
    rect_id = panel.create_rectangle(y_start, x_start, y_start, x_start, dash=(20, 20), fill='', outline='white')

    panel.bind('<Button-1>', get_mouse_posn)
    panel.bind('<B1-Motion>', update_sel_rect)
    panel.bind('<ButtonRelease-1>', blur_area)


# Skaliert Bilder wenn diese Größer als das Fenster sind
def resize_image(image):
    global ori_img, win_w, win_h

    # Berechne die Maximal Höhe und Breite des Bildes in relation zur Bildschirmgröße
    scale_fac = 0.7
    max_w = int(win_w * scale_fac)
    max_h = int(win_h * scale_fac)

    # Skaliere wenn Bild zu groß für Anwendungsfenster
    if (ori_img.width() >= max_w) or (ori_img.height() >= max_h):

        # Berechne Aspect Radio und die neue Breite des Bildes
        aspect = ori_img.height() / ori_img.width()
        new_w = int(max_h / aspect)

        # Skaliere Bild auf neue maße
        result = image.resize((new_w, max_h), Image.ANTIALIAS)
        return result
    else:
        return image


# Äußeres Fenster erstellen
root = Tk()
root.iconbitmap('images/camera.ico')
root.title("Bokeh Effekt")
root.config(background="#99aab5")

win_w = root.winfo_screenwidth()
win_h = root.winfo_screenheight()
root.geometry('%sx%s' % (int(win_w/1.5), int(win_h/1.5)))

# Innere Fenster erstellen
info_frame = Frame(root, background="#23272a")
info_frame.pack(side=BOTTOM, fill=BOTH)

tool_frame = Frame(root, background="#2c2f33")
tool_frame.pack(side=LEFT, fill=BOTH)

main_frame = Frame(root, background="#3a3e43")
main_frame.pack(side=LEFT, fill=BOTH, expand=True)

# Icons für Buttons laden
noe = ImageTk.PhotoImage(Image.open("images/tool_icons/revert.png").resize((35, 35), Image.ANTIALIAS))
foc = ImageTk.PhotoImage(Image.open("images/mode_icons/focus.png").resize((35, 35), Image.ANTIALIAS))
auto = ImageTk.PhotoImage(Image.open("images/mode_icons/auto.png").resize((35, 35), Image.ANTIALIAS))

# reserviere Speicherplatz für zu bearbeitendes Bild und Kopie für reset
x = 'images/placeholder.png'
img = ImageTk.PhotoImage(Image.open(x))
ori_img = img
ori_resize = img
blur_img = cv2.imread(x)
sec_edit = cv2.imread(x)

# Für Markierung des Rechtecks im Fokusmodus
y_start, x_start, x_end, y_end = 0, 0, 0, 0
rect_id = None

# Label für Bilddarstellung
panel = Canvas(main_frame)
panel.img = img

# Buttons, Slider und ander Bedienelemente für Modi erstellen
title_font = font.Font(family='Arial', size=16, weight='bold')

options_label = Label(tool_frame, text="Modi", background="#2c2f33", fg="white", font=title_font)
options_label.pack(pady=35)

revert_button = Button(tool_frame, image=noe, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                       command=reset_image)
revert_button.pack(padx=30, pady=30, fill=BOTH)

sep1 = Separator(tool_frame, orient=HORIZONTAL)
sep1.pack(padx=5, pady=5, fill=BOTH)

auto_mode = Button(tool_frame, image=auto, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                   font=title_font, fg="white", command=blur_image, relief="sunken", height=40, width=40)
auto_mode.pack(padx=30, pady=30, fill=BOTH)

sep2 = Separator(tool_frame, orient=HORIZONTAL)
sep2.pack(padx=5, pady=5, fill=BOTH)

focus_mode = Button(tool_frame, image=foc, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                    font=title_font, fg="white", command=focus_blur, relief="sunken", height=40, width=40)
focus_mode.pack(padx=30, pady=30, fill=BOTH)

slider_var = DoubleVar()
slider = Scale(tool_frame, from_=10, to=200, bg="#2c2f33", bd=0, fg="white", troughcolor="#3a3e43",
               length=70, sliderlength=20, variable=slider_var)
slider.set(100)
slider.pack(padx=30, pady=30, fill=BOTH)

check_var = BooleanVar()
check_var.set(True)
check = Checkbutton(tool_frame, text="Blur", variable=check_var, bg="#2c2f33", activebackground="#2c2f33")
check.pack(padx=25, pady=25, fill=BOTH)
check.select()

sep3 = Separator(tool_frame, orient=HORIZONTAL)
sep3.pack(padx=5, pady=5, fill=BOTH)

# label für Bildinfo erstellen
info_label = Label(info_frame, background="#23272a", fg="white")
info_label.pack(side=RIGHT, padx=2, pady=5)
version_label = Label(info_frame, background="#23272a", text="Version: " + global_vars.version, fg="white")
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
edge_menu.add_radiobutton(label="PoolNET", value=0, variable=edge_var)
edge_menu.add_radiobutton(label="R-CNN", value=1, variable=edge_var)
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
