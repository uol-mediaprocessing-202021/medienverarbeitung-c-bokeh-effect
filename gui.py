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
def openfn():
    filename = filedialog.askopenfilename(title='open')
    return filename


# display opened picture
def open_image():
    x = openfn()
    img = Image.open(x)
    img = img.resize((500, 500), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = Label(main_frame, image=img)
    panel.image = img
    panel.pack()


# list of all effects
EFFECTS = ["No Effect", "Gauß", "Ring", "Star"]

# Create root frame and format it
root = Tk()
root.title("Bokeh Effect")
root.config(background="#474747")

# create sub frames
main_frame = Frame(root, width=500, height=500, background="#a5a5a5")
main_frame.pack(side=LEFT, padx=1, pady=1, fill=BOTH)

tool_frame = Frame(root)  # width=200, height=500, background="#d4d4d4"
tool_frame.pack(side=LEFT, padx=1, pady=1, fill=BOTH)

# create controls
options_label = Label(tool_frame, text="Effects")
options_label.pack(pady=10)

var = StringVar(tool_frame)
var.set(EFFECTS[0])
options = OptionMenu(tool_frame, var, *EFFECTS)
options.pack(pady=20, fill=BOTH)

slider1_label = Label(tool_frame, text="Slider 1")
slider1_label.pack()

first_slider = Scale(tool_frame, from_=0, to=100, orient=HORIZONTAL)
first_slider.pack(pady=20, fill=BOTH)

slider2_label = Label(tool_frame, text="Slider 2")
slider2_label.pack()

sec_slider = Scale(tool_frame, from_=0, to=100, orient=HORIZONTAL)
sec_slider.pack(pady=20, fill=BOTH)

change_button = Button(tool_frame, text="Apply")
change_button.pack(padx=50, pady=50, fill=BOTH)

# create menu
menu = Menu(root)

# create menu items
file_menu = Menu(menu, tearoff=0)
help_menu = Menu(menu, tearoff=0)

# content of File
file_menu.add_command(label="Reset")
file_menu.add_command(label="Open Image", command=open_image)
file_menu.add_command(label="Save Image to")
file_menu.add_separator()
file_menu.add_command(label="Quit", command=root.quit)

# content of Help
help_menu.add_command(label="About", command=help_about)

# add dropdown menus to menu items
menu.add_cascade(label="File", menu=file_menu)
menu.add_cascade(label="Help", menu=help_menu)
root.config(menu=menu)

# loop that waits for user input
root.mainloop()
