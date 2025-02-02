import ctypes

import customtkinter as ctk

from PIL import Image
from utils.utils import generate_hover_color

def titlebar(master, maximized, x=None, y=None, width=None, height=None):
    def close():
        master.overrideredirect(False)
        master.destroy()
    def maximize():
        if maximized:
            titlebar.destroy()
            master.overrideredirect(False)
            master.state("zoomed")
        else:
            titlebar.destroy()
            master.overrideredirect(False)
            master.geometry(f"{width}x{height}+{x}+{y}")
    def minimize():
        master.overrideredirect(False)
        master.iconify()
        titlebar.destroy()
    if master.overrideredirect():
        tbheight = 30
        tbcolor = "#131313"
        hvcolor = generate_hover_color(tbcolor)
        titlebar = ctk.CTkFrame(master, height=tbheight+1, fg_color=tbcolor, corner_radius=0)
        titlebar.pack(fill="x")
        titlebar.lift()

        closeimg = Image.open("test/close.png")
        maximizeimg = Image.open("test/maximize.png")
        minimizeimg = Image.open("test/minimize.png")

        closeimage = ctk.CTkImage(light_image=closeimg, dark_image=closeimg, size=(10, 10))
        closebutton = ctk.CTkButton(titlebar, text="", image=closeimage, width=50, height=tbheight, corner_radius=0, fg_color=tbcolor, hover_color="#e81123", command=close)
        closebutton.pack(side="right")

        maximizeimage = ctk.CTkImage(light_image=maximizeimg, dark_image=maximizeimg, size=(10, 10))
        minimizebutton = ctk.CTkButton(titlebar, text="", image=maximizeimage, width=50, height=tbheight, corner_radius=0, fg_color=tbcolor, hover_color=hvcolor, command=maximize)
        minimizebutton.pack(side="right")

        minimizeimage = ctk.CTkImage(light_image=minimizeimg, dark_image=minimizeimg, size=(10, 1))
        minimizebutton = ctk.CTkButton(titlebar, text="", image=minimizeimage, width=50, height=tbheight, corner_radius=0, fg_color=tbcolor, hover_color=hvcolor, command=minimize)
        minimizebutton.pack(side="right")

        titlelabel = ctk.CTkLabel(titlebar, text="Hello")
        titlelabel.pack(side="left", padx=10)
root = ctk.CTk()
root.update()
# root.state("zoomed")
root.overrideredirect(True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+{0}+{0}")

maximized = True if root.state() == "zoomed" else False

b = ctk.CTkButton(root, command=lambda:titlebar(root, maximized, root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height()))
b.place(x=100, y=300)

root.mainloop()