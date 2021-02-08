from tkinter import *
from tkinter.ttk import Progressbar, Separator, Style
import tkinter.font as font
from functions import func_gui
from functions import global_vars
from detection import slic, blur
from PIL import Image, ImageTk
from tkinter import filedialog
from queue import Queue
import cv2
import os
import time
import numpy

topx, topy, botx, boty = 0, 0, 0, 0
rect_id = None


# Bilder öffnen
def open_image():
    global img, ori_img, x, blur_img, sec_edit
    global panel, file_menu, info_label
    global auto_mode, focus_mode
    global win_h, win_w, ori_resize

    # Bild laden und in canvas (panel) speichern
    x = filedialog.askopenfilename(title='Bild öffnen')
    img = Image.open(x)
    ori_img = ImageTk.PhotoImage(img)

    img = resize_image(img)
    ori_resize = img

    img = ImageTk.PhotoImage(img)

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
    global img, panel, x

    y = filedialog.asksaveasfilename(title='Bild speichern unter', filetypes=(
        ("PNG Datei (*.png)", "*.png"),
        ("JPEG Datei (*.jpeg)", "*.jpeg"),
        ("Alle Dateien", "*.*"),
    ), defaultextension=os.path.splitext(x), initialfile=os.path.basename(x))

    new_image = func_gui.covert_imgtk2img(img)
    new_image.save(y)


# bearbeitet Bild mit Torch
def blur_image():
    global x, img, edge_var, scale_var, info_frame, version_label
    global ori_img, win_w, win_h

    auto_mode.config(background="#23272a")
    focus_mode.config(background="#2c2f33")

    que = Queue()
    try:
        image_thread = func_gui.IPThread(edge_var.get(), x, scale_var.get(), que)
        image_thread.start()
    except KeyboardInterrupt:
        print("[Error] unable to start ImageProcessing_Thread")
        time.sleep(1)

    version_label.config(text=" ")
    progress = Progressbar(info_frame, orient=HORIZONTAL, length=75, mode='indeterminate')
    progress.pack(side=LEFT)
    func_gui.bar(progress, info_frame)

    if not que.empty():
        result = Image.fromarray(que.get())
        result = resize_image(result)

        img = ImageTk.PhotoImage(result)

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
    img = ori_img

    if (ori_img.width() >= int(win_w * 0.7)) or (ori_img.height() >= int(win_h * 0.7)):
        img = ori_resize

    img = ImageTk.PhotoImage(img)

    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    panel.unbind('<Button-1>')

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#2c2f33")


# setzt Einstellungen zurück
def reset_setup():
    global edge_var, scale_var
    edge_var.set(0)
    scale_var.set(0)


# trackt Maus position
def get_mouse_posn(event):
    global panel, img, x, sec_edit
    global topy, topx

    topx, topy = event.x, event.y


# updated Fokusbereich
def update_sel_rect(event):
    global rect_id, panel, sec_edit, img, ori_img
    global topy, topx, botx, boty, slider_var, check_var
    global win_h, win_w

    botx, boty = event.x, event.y
    panel.coords(rect_id, topx, topy, botx, boty)

    original_img = cv2.imread(x)

    sec_edit = slic.edit_segment(original_img, sec_edit, slider_var.get(), topy, topx, botx, boty, check_var.get())

    result = Image.fromarray(sec_edit.astype(numpy.uint8))

    result = resize_image(result)

    img = ImageTk.PhotoImage(result)

    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#2c2f33")

    panel.unbind('<Button-1>')


# wechsel zu fokus Modus
def activate_focus_mode():
    global panel, img, x, blur_img, sec_edit, rect_id, slider_var, ori_img
    global win_h, win_w

    auto_mode.config(background="#2c2f33")
    focus_mode.config(background="#23272a")

    cv_img = cv2.imread(x)
    seg = slic.show_segmentation(cv_img, sec_edit, slider_var.get())

    result = Image.fromarray(seg.astype(numpy.uint8))

    result = resize_image(result)

    img = ImageTk.PhotoImage(result)

    panel.config(width=img.width(), height=img.height())
    panel.create_image(0, 0, image=img, anchor=NW)

    rect_id = panel.create_rectangle(topx, topy, topx, topy, dash=(20, 20), fill='', outline='white')

    panel.bind('<Button-1>', get_mouse_posn)
    panel.bind('<B1-Motion>', update_sel_rect)


def resize_image(image):
    global ori_img, win_w, win_h
    scale_fac = 0.7
    max_w = int(win_w * scale_fac)
    max_h = int(win_h * scale_fac)

    if (ori_img.width() >= max_w) or (ori_img.height() >= max_h):
        aspect = ori_img.height() / ori_img.width()

        new_w = int(max_h / aspect)

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
# ring = ImageTk.PhotoImage(Image.open("images/tool_icons/circles.png").resize((35, 35), Image.ANTIALIAS))
# star = ImageTk.PhotoImage(Image.open("images/tool_icons/stars.png").resize((35, 35), Image.ANTIALIAS))
# hexa = ImageTk.PhotoImage(Image.open("images/tool_icons/hexa.png").resize((35, 30), Image.ANTIALIAS))
# heart = ImageTk.PhotoImage(Image.open("images/tool_icons/hearts.png").resize((35, 35), Image.ANTIALIAS))
foc = ImageTk.PhotoImage(Image.open("images/mode_icons/focus.png").resize((35, 35), Image.ANTIALIAS))
auto = ImageTk.PhotoImage(Image.open("images/mode_icons/auto.png").resize((35, 35), Image.ANTIALIAS))

# reserviere Speicherplatz für zu bearbeitendes Bild und kopie für reset
x = 'images/placeholder.png'
img = ImageTk.PhotoImage(Image.open(x))
ori_img = img
ori_resize = img
blur_img = cv2.imread(x)
sec_edit = cv2.imread(x)

# Label für Bilddarstellung
panel = Canvas(main_frame)
panel.img = img

# Buttons für Modi erstellen
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
                    font=title_font, fg="white", command=activate_focus_mode, relief="sunken", height=40, width=40)
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

# circle_button = Button(tool_frame, image=ring, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
#                      command=blur)
# circle_button.pack(padx=25, pady=25, fill=BOTH)

# star_button = Button(tool_frame, image=star, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
#                    command=blur)
# star_button.pack(padx=25, pady=25, fill=BOTH)

# hex_button = Button(tool_frame, image=hexa, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
#                   command=blur)
# hex_button.pack(padx=25, pady=25, fill=BOTH)

# heart_button = Button(tool_frame, image=heart, background="#2c2f33", borderwidth=0, activebackground="#2c2f33",
#                     command=blur)
# heart_button.pack(padx=25, pady=25, fill=BOTH)

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
