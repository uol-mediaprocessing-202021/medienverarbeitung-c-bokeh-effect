from tkinter import messagebox
from PIL import Image
from functions import global_vars
from model import pool
from model import rcnn
import numpy as np
import time
import threading


# Text für Punkt 'Über das Projekt' im Reiter 'Hilfe'
def help_about():
    about_text = "\
Projekt: Medienverarbeitung Gruppe C\n\
Carl-von-Ossietzky Universität Oldenburg\n\
Authors: Jona Schrader, Roman Kammer, Malte Trauernicht\n\
Version: 1.0.0"
    messagebox.showinfo(message=about_text, title="Über das Projekt")


# Text für Punkt 'Tutorial' im Reiter 'Hilfe'
def help_colab():
    about_text = "\
Google Colab Dokumentation des Projektes:\n\
\n\
https://colab.research.google.com/drive/16Y4wp7qCuzpu2yXUFqc7jMICxJSavPgH"
    messagebox.showinfo(message=about_text, title="Colaboratory")


# Konvertiere PIL.ImageTk aus Label in ein PIL.Image
def covert_imgtk2img(img):
    width, height = img._PhotoImage__size
    rgb = np.empty((height, width, 3))
    for j in range(height):
        for i in range(width):
            rgb[j, i, :] = img._PhotoImage__photo.get(x=i, y=j)

    new_img = Image.fromarray(rgb.astype('uint8'))
    return new_img


# Setzt Position der grünen Linie im Ladebalken fest
def bar(progress, frame):

    while not global_vars.progress_bar_check:
        for x in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            if not global_vars.progress_bar_check:
                progress['value'] = x
                frame.update_idletasks()
                time.sleep(0.1)
            else:
                break

        for y in [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]:
            if not global_vars.progress_bar_check:
                progress['value'] = y
                frame.update_idletasks()
                time.sleep(0.1)
            else:
                break


# Klasse für ImageProcessing_Thread
class IPThread(threading.Thread):
    def __init__(self, edge_var, x, scale_var, blur_style, blur_dim, que):
        threading.Thread.__init__(self)
        self.edge_var = edge_var
        self.x = x
        self.scale_var = scale_var
        self.blur_style = blur_style
        self.blur_dim = blur_dim
        self.que = que

    def run(self):
        time.sleep(0.5)
        self.que.put(process_image(self.edge_var, self.x, self.scale_var, self.blur_style, self.blur_dim))


# Function des ImageProcessing_Thread
# Alle Veränderungen am Bild werden auf diesem Bild ausgeführt
def process_image(edge_var, x, scale_var, blur_style, blur_dim):
    if edge_var == 0:
        blur_img = pool.pool(x, scale_var, blur_style, blur_dim)
        global_vars.progress_bar_check = True
        return blur_img
    else:
        blur_img = rcnn.rcnn_blur(x, blur_style, blur_dim)
        global_vars.progress_bar_check = True
        return blur_img
