from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
from tkinter import filedialog


# Text für Punkt 'Über das Projekt' im Reiter Hilfe
def help_about():
    about_text = "\
Projekt: Medienverarbeitung Gruppe C (Universität Oldenburg)\n\
Authors: Jona Schrader, Roman Kammer, Malte Trauernicht\n\
Version: alpha 0.01"
    messagebox.showinfo(message=about_text, title="Über das Projekt")


# Bilder öffnen
def open_image():
    x = filedialog.askopenfilename(title='Bild öffnen')
    global img
    img = Image.open(x)
    img = img.resize((500, 500), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = Label(main_frame, image=img)
    panel.image = img
    panel.pack()


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

# Inner Fenster erstellen
main_frame = Frame(root, width=500, height=500, background="#a5a5a5")
main_frame.pack(side=LEFT, padx=1, pady=1, fill=BOTH)

tool_frame = Frame(root)  # width=200, height=500, background="#d4d4d4"
tool_frame.pack(side=LEFT, padx=1, pady=1, fill=BOTH)

# Buttons für Effekte erstellen
options_label = Label(tool_frame, text="Effekte")
options_label.pack(pady=10)

no_button = Button(tool_frame, text="Kein Effekt")
no_button.pack(padx=30, pady=30, fill=BOTH)

ring_button = Button(tool_frame, text="Ringe")
ring_button.pack(padx=30, pady=30, fill=BOTH)

star_button = Button(tool_frame, text="Sterne")
star_button.pack(padx=30, pady=30, fill=BOTH)

square_button = Button(tool_frame, text="Quadrate")
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
img = ImageTk.PhotoImage(Image.open("placeholder.png"))

# Schleife die auf Nutzerinput wartet
root.mainloop()
