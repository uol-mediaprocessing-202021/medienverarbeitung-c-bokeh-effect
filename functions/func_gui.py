from tkinter import messagebox
from PIL import Image
import numpy as np


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
