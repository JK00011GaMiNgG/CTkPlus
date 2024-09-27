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
After that you will need to import it:
```
import ctkplus
```
or
```
import ctkplus
```

## Title Bar Color
In normal customtkinter there are two titlebar colors to choose from. Either light (#ebebeb) or dark (#242424). But with this, you can change that to whatever you want. Heres an example:
```
window = ctkp.CTkPlus(
    title_bar_color='#ff0000' # red
)

window.mainloop()
```
The output will look like:
![alt text](https://github.com/JK00011GaMiNgG/CTkPlus/blob/cca0fb92e32f22865e3f85a51a86db55fe35e352/rdms/images/title_bar_color.png?raw=true)

## Title Color
Title color will affect the color of the actual title itself. By default this is either fully white, or fully black depending on if your windows theme is light or dark. Here is how you could change this:
```
window = ctkp.CTkPlus(
    title_color='#0000ff' # blue
)

window.mainloop()
```
The result will look like:
![alt text](https://github.com/JK00011GaMiNgG/CTkPlus/blob/cca0fb92e32f22865e3f85a51a86db55fe35e352/rdms/images/title_color.png?raw=true)

## Border Color
Border color isnt normally used and isnt really found in any production apps, but its here anyway. It is just what it sounds like, border color. Here is an example on how to use it:
```
window = ctkp.CTkPlus(
    border_color='#00ff00' # green
)

window.mainloop()
```
And the output for this would look like:
![alt text](https://github.com/JK00011GaMiNgG/CTkPlus/blob/2d2f3602de9b06359cdde3894a49460138f7da82/rdms/images/border_color.png?raw=true)

## Corner Type
Corner type is basically how the corners of the window look. There are 4 states that this can be. Flat, Round, Round Small, and Default. Default is the default corner type of windows. PS: The border color adapts to the corner type automatically. Here is an example for all 4:
### Flat
```
window = CTkPlus(
	corner_type='flat'
)

window.mainloop()
```
Output:
IMAGE LOGIC

### Round
```
window = CTkPlus(
	corner_type='round'
)

window.mainloop()
```
Output:
IMAGE LOGIC

### Round Small
```
window = CTkPlus(
	corner_type='round_small'
)

window.mainloop()
```
Output:
IMAGE LOGIC

### Default
```
window = CTkPlus(
	corner_type='default'
)

window.mainloop()
```
Output:
IMAGE LOGIC
