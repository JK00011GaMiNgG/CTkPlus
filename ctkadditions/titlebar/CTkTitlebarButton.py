import customtkinter as ctk
import inspect
from customtkinter import CTkFont, CTkImage

from ctkadditions.utils.utils import generate_hover_color
from typing import *

class CTkTitlebarButton(ctk.CTkButton):
    def __init__(self,
                 master,
                 text: str = "Button",
                 width: int = 50,
                 align: Optional[Union[Literal["right"], Literal["left"], Literal["center"]]] = "right",
                 command: Union[Callable[[], Any], None] = None):
        self._master = master
        self._width = width
        self._height = master.title_bar_height
        self._text = text
        self._fg_color = master.title_bar_color
        self._command = command
        self._align = align

        super().__init__(master, text=self._text, width=self._width, height=self._height, fg_color=self._fg_color, hover_color=generate_hover_color(self._fg_color), corner_radius=0, command=self._command)

    def pack(self, align="right"):
        super().pack(side=align, padx=0)
        self._align = align

    def pack_forget(self):
        super().pack_forget()

    def place(self, **kwargs):
        raise AttributeError("This method is disabled in this class. Instead, use \"pack\".")

    def grid(self, **kwargs):
        raise AttributeError("This method is disabled in this class. Instead, use \"pack\".")

    def config(self, *args, **kwargs):
        raise AttributeError("This method is disabled in this class.")

    def configure(self, require_redraw=False, **kwargs):
        if not inspect.stack()[1].frame.f_locals.get('self', None) or not isinstance(inspect.stack()[1].frame.f_locals.get('self', None), CTkTitlebarButton):
            raise AttributeError("This method is disabled in this class.")

        for key, value in kwargs.items():
            if key in {"corner_radius", "border_width", "border_spacing", "background_corner_colors", "compound", "anchor"}:
                setattr(self, f"_{key}", value)
                self._create_grid()
                require_redraw = True
            elif key in {"fg_color", "hover_color", "border_color", "text_color", "text_color_disabled"}:
                setattr(self, f"_{key}", self._check_color_type(value, transparency=(key == "fg_color")))
                require_redraw = True
            elif key == "text":
                self._text = value
                if self._text_label is None:
                    require_redraw = True
                else:
                    self._text_label.configure(text=self._text)
            elif key == "font":
                if isinstance(self._font, CTkFont):
                    self._font.remove_size_configure_callback(self._update_font)
                self._font = self._check_font_type(value)
                if isinstance(self._font, CTkFont):
                    self._font.add_size_configure_callback(self._update_font)
                self._update_font()
            elif key == "textvariable":
                self._textvariable = value
                if self._text_label is not None:
                    self._text_label.configure(textvariable=self._textvariable)
            elif key == "image":
                if isinstance(self._image, CTkImage):
                    self._image.remove_configure_callback(self._update_image)
                self._image = self._check_image_type(value)
                if isinstance(self._image, CTkImage):
                    self._image.add_configure_callback(self._update_image)
                self._update_image()
            elif key == "state":
                self._state = value
                self._set_cursor()
                require_redraw = True
            elif key == "hover":
                self._hover = value
            elif key == "command":
                self._command = value
                self._set_cursor()

        super().configure(require_redraw=require_redraw, **kwargs)