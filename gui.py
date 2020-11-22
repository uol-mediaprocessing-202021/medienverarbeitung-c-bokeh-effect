from tkinter import *
from tkinter import messagebox


def help_about():
    m_text = "\
Project: Media Processing Group C (University Oldenburg)\n\
Authors: Jona Schrader, Roman Kammer, Malte Trauernicht\n\
Date: 22.11.20\n\
Version: alpha 0.01"
    messagebox.showinfo(message=m_text, title="About")


# Create root frame and format it
root = Tk()
root.title("Bokeh Effect")

main_frame = Frame(root, width=500, height=500, background="#f6f6f6")
main_frame.pack(side=LEFT)

tool_frame = Frame(root, width=200, height=500, background="#d4d4d4")
tool_frame.pack(side=LEFT)

# create menu
menu = Menu(root)

# create menu items
file_menu = Menu(menu, tearoff=0)
help_menu = Menu(menu, tearoff=0)

# content of File
file_menu.add_command(label="Reset")
file_menu.add_command(label="Open Image")
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
