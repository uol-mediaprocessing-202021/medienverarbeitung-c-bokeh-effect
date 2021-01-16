from tkinter import messagebox
from PIL import Image
from functions import global_vars
from detection import pool
from detection import torch
import numpy as np
import time
import threading


# Text für Punkt 'Über das Projekt' im Reiter Hilfe
def help_about():
    about_text = "\
Projekt: Medienverarbeitung Gruppe C\n\
Carl-von-Ossietzky Universität Oldenburg\n\
Authors: Jona Schrader, Roman Kammer, Malte Trauernicht\n\
Version: Alpha 0.01"
    messagebox.showinfo(message=about_text, title="Über das Projekt")


# Text für Punkt 'Tutorial' im Reiter Hilfe
def help_tut():
    about_text = "\
1: Lade ein Bild unter Datei --> Öffnen...\n\
2: Klicke auf den gewünschten Effekt in der Effektleiste\n\
3: Speicher das Bild unter Datei --> Speichern unter..."
    messagebox.showinfo(message=about_text, title="Tutorial")


# Konvertiere PIL.ImageTk aus Label in ein PIL.Image
def covert_imgtk2img(img):
    width, height = img._PhotoImage__size
    rgb = np.empty((height, width, 3))
    for j in range(height):
        for i in range(width):
            rgb[j, i, :] = img._PhotoImage__photo.get(x=i, y=j)

    new_img = Image.fromarray(rgb.astype('uint8'))
    # new_img = new_img.convert("RGBA")
    return new_img


# Function responsible for the updation
# of the progress bar value
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


# Class for ImageProcessing_Thread
class IPThread(threading.Thread):
    def __init__(self, thread_id, name, edge_var, x, scale_var, que):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.edge_var = edge_var
        self.x = x
        self.scale_var = scale_var
        self.que = que

    def run(self):
        print("\n[LDThread][INFO] starting " + self.name + "\n")
        time.sleep(0.5)
        self.que.put(process_image(self.edge_var, self.x, self.scale_var))


def process_image(edge_var, x, scale_var):

    if edge_var == 0:
        blur_img = pool.pool(x, scale_var)
        global_vars.progress_bar_check = True
        return blur_img
    else:
        blur_img = torch.torch_blur(x)
        global_vars.progress_bar_check = True
        return blur_img

