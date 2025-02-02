# import customtkinter as ctk
#
# class Titlebar(ctk.CTkToplevel):
#     def __init__(self,
#                  master,
#                  color,
#                  height):
#         super().__init__()
#
#         self.after(1)
#         self._master = master
#         self._master.minsize(200, 100)
#         self._master.title("")
#         self.overrideredirect(True)
#
#         self.title_bar_height = height
#         self.title_bar_color = color
#
#         self.transparent_color = self._apply_appearance_mode(self._fg_color)
#         self.attributes("-transparentcolor", self.transparent_color)
#         self.resizable(True, True)
#         self.config(background=self.transparent_color)
#         self.caption_color = self.title_bar_color
#
#         self._master.bind("<Configure>", lambda _: self.change_dimension())
#         self._master.bind("<FocusIn>", lambda _: self.deiconify())
#         self._master.bind("<FocusOut>", lambda _: self.withdraw() if self._master.state() == "iconic" else None)
#         # self.bind("<FocusIn>", lambda _: root.focus())
#
#     def change_dimension(self):
#         self.geometry(f"{self._master.winfo_width()-170}x{self.title_bar_height}+{self._master.winfo_x()+40}+{self._master.winfo_y()+1+(30-self.title_bar_height)}")
#         self.deiconify()

import customtkinter as ctk

class Titlebar(ctk.CTkToplevel):
    def __init__(self,
                 master,
                 color,
                 height):
        super().__init__()

        self.after(1)
        self._master = master
        self._master.minsize(200, 100)
        self._master.title("")
        self.overrideredirect(True)

        self.title_bar_height = height
        self.title_bar_color = color

        self.transparent_color = self._apply_appearance_mode(self._fg_color)
        self.attributes("-transparentcolor", self.transparent_color)
        self.resizable(True, True)
        self.config(background=self.transparent_color)
        self.caption_color = self.title_bar_color

        self._master.bind("<Configure>", lambda _: self.change_dimension())
        self._master.bind("<FocusIn>", lambda _: self.deiconify())
        self._master.bind("<FocusOut>", lambda _: self.withdraw() if self._master.state() == "iconic" else None)
        self.bind("<FocusIn>", lambda _: self._master.focus())

    def _show_children(self):
        for child in self.winfo_children():
            child.pack()

    def _hide_children(self):
        for child in self.winfo_children():
            child.pack_forget()
            child.place_forget()

    def change_dimension(self):
        self.geometry(f"{self._master.winfo_width()-170}x{self.title_bar_height}+{self._master.winfo_x()+40}+{self._master.winfo_y()+1+(30-self.title_bar_height)}")
        self.deiconify()

    def set_titlebar_height(self, height):
        self.title_bar_height = height
        self.change_dimension()