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

from model import slic, blur
from functions import func_gui, global_vars


# Bilder öffnen
def open_image():
    global img, ori_img, x, blur_img, sec_edit, blur_style, blur_dim
    global panel, file_menu, info_label
    global ori_resize, auto_mode, focus_mode, revert_button

    global_vars.img_is_scaled = False

    # Bild laden und in canvas (panel) speichern
    x = filedialog.askopenfilename(title='Bild öffnen')

    if x != '':
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

        blur_img = blur.bokeh(cv2.imread(x), blur_style, blur_dim.get())
        sec_edit = cv2.imread(x)

        # infoleiste updaten und speichern unter ermöglichen
        info_label.config(text="Datei: " + x + " | " + "Size: " + str(ori_img.height()) + ' x ' + str(ori_img.width()))

        file_menu.entryconfig("Speichern unter ...", state="normal")

        auto_mode.config(state=NORMAL)
        focus_mode.config(state=NORMAL)
        revert_button.config(state=NORMAL)


# Bilder speichern
def save_image():
    global img, x, sec_edit

    # Benutzer sucht pfad und name zum speichern aus
    y = filedialog.asksaveasfilename(title='Bild speichern unter', filetypes=(
        ("PNG Datei (*.png)", "*.png"),
        ("JPEG Datei (*.jpeg)", "*.jpeg"),
        ("Alle Dateien", "*.*"),
    ), defaultextension=os.path.splitext(x), initialfile=os.path.basename(x))

    cv2.imwrite(y, sec_edit)


# Bearbeitet Bild mit Torch oder PoolNet
def blur_image():
    global x, img, edge_var, scale_var, info_frame, version_label, sec_edit, blur_style, blur_dim
    global auto_mode, focus_mode

    auto_mode.config(background="#23272a")
    focus_mode.config(background="#2c2f33")

    que = Queue()

    # Erstellt einen Thread auf dem die Bildbearbeitung statt findet
    try:
        image_thread = func_gui.IPThread(edge_var.get(), x, scale_var.get(), blur_style, blur_dim.get(), que)
        image_thread.start()
    except KeyboardInterrupt:
        print("[Error] unable to start ImageProcessing_Thread")
        time.sleep(1)

    # Zeige Ladebalken an, damit Benuter weiß, dass der Algorithmus ausgeführt wird
    version_label.config(text=" ")
    progress = Progressbar(info_frame, orient=HORIZONTAL, length=75, mode='indeterminate')
    progress.pack(side=LEFT)
    func_gui.bar(progress, info_frame)

    # Hohle das fertige Bild aus der queue und konvertiere es in PhotoImage
    if not que.empty():
        sec_edit = que.get()
        result = Image.fromarray(cv2.cvtColor(sec_edit, cv2.COLOR_BGR2RGB))
        result = resize_image(result)
        img = ImageTk.PhotoImage(result)

    # Zeige fertiges Bild an
    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    progress.destroy()
    version_label.config(text="Version: " + global_vars.version)

    global_vars.progress_bar_check = False

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#2c2f33")


# Setzt das Bild zum Ursprung zurück
def reset_image():
    global panel, img, ori_img, ori_resize
    global blur_img, sec_edit
    global blur_style, blur_dim

    img = ori_img

    if (ori_img.width() >= int(win_w * global_vars.scale_fac)) or \
            (ori_img.height() >= int(win_h * global_vars.scale_fac)):
        img = ori_resize
        img = ImageTk.PhotoImage(img)

    blur_img = blur.bokeh(cv2.imread(x), blur_style, blur_dim.get())
    sec_edit = cv2.imread(x)

    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    panel.delete(rect_id)

    panel.unbind('<Button-1>')
    panel.unbind('<B1-Motion>')
    panel.unbind('<ButtonRelease-1>')

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#2c2f33")


# Setzt Einstellungen zurück
def reset_setup():
    global edge_var, scale_var
    edge_var.set(0)
    scale_var.set(0)


# Trackt Maus position
# Event linker Mausklick
def get_mouse_posn(event):
    global x_start, y_start, x_end, y_end

    x_start, y_start = event.x, event.y
    x_end, y_end = event.x, event.y


# Updated Fokusbereich
# Event Mauszeiger bewegungen
def update_sel_rect(event):
    global rect_id, panel, sec_edit, img, ori_img
    global x_start, y_start, x_end, y_end, slider_var, check_var

    x_end, y_end = event.x, event.y
    panel.coords(rect_id, x_start, y_start, x_end, y_end)


# Setzt prozess für Unschärfe auf Segmentierte Bereiche an
# Event linke Maustaste loslassen
def blur_area(event):
    global rect_id, panel, sec_edit, img, ori_img, image_scale
    global x_start, y_start, x_end, y_end, slider_var, check_var, blur_style, blur_dim

    original_img = cv2.imread(x)

    # Editiere die ausgewählten Segmente
    sec_edit = slic.edit_segment(sec_edit, original_img, slider_var.get(), int(x_start / image_scale),
                                 int(x_end / image_scale), int(y_start / image_scale), int(y_end / image_scale),
                                 check_var.get(), blur_style, blur_dim.get())

    # Konvertiere Ergebnis in PhotoImage und zeige an
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


# Wechsel zu Fokus Modus
def focus_blur():
    global panel, img, x, sec_edit, rect_id, slider_var

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#23272a")

    # Erstelle segmentiertes Bild für Benuzer
    cv_img = cv2.imread(x)
    seg = slic.show_segmentation(sec_edit, cv_img, slider_var.get())

    # Konvertiere und zeige an
    result = Image.fromarray(cv2.cvtColor(seg, cv2.COLOR_BGR2RGB).astype(numpy.uint8))
    result = resize_image(result)
    img = ImageTk.PhotoImage(result)

    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    # Zeichne Rechteck um Maus
    rect_id = panel.create_rectangle(y_start, x_start, y_start, x_start, dash=(20, 20), fill='', outline='white')

    panel.bind('<Button-1>', get_mouse_posn)
    panel.bind('<B1-Motion>', update_sel_rect)
    panel.bind('<ButtonRelease-1>', blur_area)


# Skaliert Bilder wenn diese Größer als das Fenster sind
def resize_image(image):
    global ori_img, win_w, win_h, image_scale

    # Berechne die Maximal Höhe und Breite des Bildes in relation zur Bildschirmgröße
    max_w = int(win_w * global_vars.scale_fac)
    max_h = int(win_h * global_vars.scale_fac)

    image_scale = 1

    # Skaliere wenn Bild zu groß für Anwendungsfenster
    if (ori_img.width() >= max_w) or (ori_img.height() >= max_h):

        # Berechne Aspect Radio und die neue Breite des Bildes
        aspect = ori_img.height() / ori_img.width()
        new_w = int(max_h / aspect)

        # Skaliere Bild auf neue maße
        if isinstance(image, numpy.ndarray):
            result = cv2.resize(image, (new_w, max_h))
        else:
            result = image.resize((new_w, max_h), Image.ANTIALIAS)

        global_vars.img_is_scaled = True
        image_scale = new_w / ori_img.width()
        return result
    else:
        return image


# Passt die variable blur_style an damit richtige Unschärfe-Objekte gezeigt werden
def change_blur_style(value):
    global blur_style, round_button, ring_button, cross_button

    blur_style = value

    # Hintergrundfarbe der passenden Buttons wird geändert
    if blur_style == 0:
        cross_button.config(background="#23272a")
        ring_button.config(background="#2c2f33")
        round_button.config(background="#2c2f33")
    elif blur_style == 1:
        cross_button.config(background="#2c2f33")
        ring_button.config(background="#23272a")
        round_button.config(background="#2c2f33")
    else:
        cross_button.config(background="#2c2f33")
        ring_button.config(background="#2c2f33")
        round_button.config(background="#23272a")


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

effect_frame = Frame(root, background="#2c2f33")
effect_frame.pack(side=LEFT, fill=BOTH)

# Icons für Buttons laden
noe = ImageTk.PhotoImage(Image.open("images/tool_icons/revert.png").resize((35, 35), Image.ANTIALIAS))
foc = ImageTk.PhotoImage(Image.open("images/mode_icons/focus.png").resize((35, 35), Image.ANTIALIAS))
auto = ImageTk.PhotoImage(Image.open("images/mode_icons/auto.png").resize((35, 35), Image.ANTIALIAS))

round_i = ImageTk.PhotoImage(Image.open("images/tool_icons/circles.png").resize((35, 35), Image.ANTIALIAS))
ring_i = ImageTk.PhotoImage(Image.open("images/tool_icons/rings.png").resize((35, 35), Image.ANTIALIAS))
cross_i = ImageTk.PhotoImage(Image.open("images/tool_icons/cross.png").resize((35, 35), Image.ANTIALIAS))

# Reserviere Speicherplatz für zu bearbeitendes Bild und Kopie für reset
x = 'images/placeholder.png'
img = ImageTk.PhotoImage(Image.open(x))
ori_img = img
ori_resize = img
blur_img = cv2.imread(x)
sec_edit = cv2.imread(x)

# Für Markierung des Rechtecks im Fokusmodus
y_start, x_start, x_end, y_end = 0, 0, 0, 0
rect_id = None
blur_style = 2
image_scale = 1

# Label für Bilddarstellung
panel = Canvas(main_frame)
panel.img = img

# Fonts für Bedienelemente
label_font = font.Font(family='Arial', size=10, weight='bold')
title_font = font.Font(family='Arial', size=20, weight='bold')

# Buttons, Slider und ander Bedienelemente für Modi erstellen
title_label = Label(tool_frame, text="Modi", background="#2c2f33", fg="white", font=title_font)
title_label.pack(pady=35)

revert_label = Label(tool_frame, text="Zurücksetzen", background="#2c2f33", fg="white", font=label_font)
revert_label.pack()

sep = Separator(tool_frame, orient=HORIZONTAL)
sep.pack(padx=5, fill=BOTH)

revert_button = Button(tool_frame, image=noe, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                       command=reset_image, state=DISABLED)
revert_button.pack(padx=30, pady=30, fill=BOTH)

auto_label = Label(tool_frame, text="Auto-Modus", background="#2c2f33", fg="white", font=label_font)
auto_label.pack()

sep1 = Separator(tool_frame, orient=HORIZONTAL)
sep1.pack(padx=5, fill=BOTH)

auto_mode = Button(tool_frame, image=auto, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                   font=title_font, fg="white", command=blur_image, relief="sunken", height=40, width=40,
                   state=DISABLED)
auto_mode.pack(padx=30, pady=30, fill=BOTH)

focus_label = Label(tool_frame, text="Fokus-Modus", background="#2c2f33", fg="white", font=label_font)
focus_label.pack()

sep2 = Separator(tool_frame, orient=HORIZONTAL)
sep2.pack(padx=5, fill=BOTH)

focus_mode = Button(tool_frame, image=foc, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                    font=title_font, fg="white", command=focus_blur, relief="sunken", height=40, width=40,
                    state=DISABLED)
focus_mode.pack(padx=30, pady=20, fill=BOTH)

slider_var = DoubleVar()
slider = Scale(tool_frame, from_=5, to=1000, bg="#2c2f33", bd=3, fg="white", troughcolor="#3a3e43",
               length=80, sliderlength=20, variable=slider_var, resolution=5, highlightbackground="#2c2f33",
               activebackground="#2c2f33")
slider.set(100)
slider.pack(padx=10, pady=20, fill=BOTH)

check_var = BooleanVar()
check_var.set(True)
check = Checkbutton(tool_frame, text="Blur", variable=check_var, bg="#2c2f33", activebackground="#2c2f33",
                    font=label_font, fg="white", selectcolor="#2c2f33")
check.pack(padx=25, pady=20, fill=BOTH)
check.select()

sep3 = Separator(tool_frame, orient=HORIZONTAL)
sep3.pack(padx=5, pady=5, fill=BOTH)

# Buttons, Slider und ander Bedienelemente für Effekte erstellen
effect_label = Label(effect_frame, text="Bokeh", background="#2c2f33", fg="white", font=title_font)
effect_label.pack(pady=35, padx=15)

type_label = Label(effect_frame, text="Effekt-Typ", background="#2c2f33", fg="white", font=label_font)
type_label.pack()

sepr = Separator(effect_frame, orient=HORIZONTAL)
sepr.pack(padx=5, fill=BOTH)

round_button = Button(effect_frame, image=round_i, background="#23272a", borderwidth=0, activebackground="#2c2f33",
                      command=lambda *args: change_blur_style(2), height=40, width=40, relief="sunken")
round_button.pack(padx=30, pady=30, fill=BOTH)

ring_button = Button(effect_frame, image=ring_i, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                     command=lambda *args: change_blur_style(1), height=40, width=40, relief="sunken")
ring_button.pack(padx=30, pady=30, fill=BOTH)

cross_button = Button(effect_frame, image=cross_i, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
                      command=lambda *args: change_blur_style(0), height=40, width=40, relief="sunken")
cross_button.pack(padx=30, pady=30, fill=BOTH)

blur_label = Label(effect_frame, text="Effekt-Stärke", background="#2c2f33", fg="white", font=label_font)
blur_label.pack()

sepr1 = Separator(effect_frame, orient=HORIZONTAL)
sepr1.pack(padx=5, fill=BOTH)

blur_dim = IntVar()
slider = Scale(effect_frame, from_=3, to=100, bg="#2c2f33", bd=3, fg="white", troughcolor="#3a3e43",
               length=150, sliderlength=20, variable=blur_dim, highlightbackground="#2c2f33",
               activebackground="#2c2f33")
slider.set(10)
slider.pack(padx=30, pady=20, fill=BOTH)

sepr2 = Separator(effect_frame, orient=HORIZONTAL)
sepr2.pack(padx=5, fill=BOTH)


# Label für Bildinfo erstellen
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
help_menu.add_command(label="Colaboratory", command=func_gui.help_colab)
menu.add_cascade(label="Hilfe", menu=help_menu)

root.config(menu=menu)

# Schleife die auf Nutzerinput wartet
root.mainloop()
