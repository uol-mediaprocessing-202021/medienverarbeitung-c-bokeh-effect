from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
from tkinter import filedialog


# provides text for the 'About' window
def help_about():
    about_text = "\
Project: Media Processing Group C (University Oldenburg)\n\
Authors: Jona Schrader, Roman Kammer, Malte Trauernicht\n\
Version: alpha 0.01"
    messagebox.showinfo(message=about_text, title="About")


# open pictures
def open_image():
    x = filedialog.askopenfilename(title='Open Image')
    global img
    img = Image.open(x)
    img = img.resize((500, 500), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = Label(main_frame, image=img)
    panel.image = img
    panel.pack()


# save pictures
def save_image():
    y = filedialog.asksaveasfilename(title='Save Image As', defaultextension='.png')
    global img
    print(img.width())
    print(y)


# create root frame and format it
root = Tk()
root.title("Bokeh Effect")
root.config(background="#474747")

# create sub frames
main_frame = Frame(root, width=500, height=500, background="#a5a5a5")
main_frame.pack(side=LEFT, padx=1, pady=1, fill=BOTH)

tool_frame = Frame(root)  # width=200, height=500, background="#d4d4d4"
tool_frame.pack(side=LEFT, padx=1, pady=1, fill=BOTH)

# create effect controls
options_label = Label(tool_frame, text="Effects")
options_label.pack(pady=10)

no_button = Button(tool_frame, text="No Effect")
no_button.pack(padx=30, pady=30, fill=BOTH)

ring_button = Button(tool_frame, text="Ring")
ring_button.pack(padx=30, pady=30, fill=BOTH)

star_button = Button(tool_frame, text="Star")
star_button.pack(padx=30, pady=30, fill=BOTH)

square_button = Button(tool_frame, text="Square")
square_button.pack(padx=30, pady=30, fill=BOTH)

# create menu
menu = Menu(root)

# create menu items
file_menu = Menu(menu, tearoff=0)
help_menu = Menu(menu, tearoff=0)

# content of File
file_menu.add_command(label="Reset")
file_menu.add_command(label="Open Image", command=open_image)
file_menu.add_command(label="Save Image As", command=save_image)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=root.quit)

# content of Help
help_menu.add_command(label="About", command=help_about)

# add dropdown menus to menu items
menu.add_cascade(label="File", menu=file_menu)
menu.add_cascade(label="Help", menu=help_menu)
root.config(menu=menu)

img = ImageTk.PhotoImage(Image.open("placeholder.png"))

# loop that waits for user input
root.mainloop()
