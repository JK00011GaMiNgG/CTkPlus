# CTkPlus
CTkPlus is a windows 11 extension for the customtkinter module. It allows you to modify things that normally couldnt be modified.

## Installation
```
python -m pip install ctkplus
```
or
```
pip install ctkplus
```

## Title bar color
In normal customtkinter there are two titlebar colors to choose from. Either light (#ebebeb) or dark (#242424). But with this, you can change that to whatever you want. Heres an example:
```
import ctkplus as ctkp

window = ctkp.CTkPlus(
    title_bar_color='#ff0000' #red
)

window.mainloop()
```
![Screenshot_2](https://raw.githubusercontent.com/JK00011GaMiNgG/CTkPlus/refs/heads/main/rdms/images/title_bar_color.png")
