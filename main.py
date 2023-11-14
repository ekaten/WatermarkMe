from tkinter import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from tkinter.messagebox import showerror, askyesno
from PIL import Image, ImageTk, ImageDraw, ImageFont


## GLOBAL VARIABLES ##

root_width = 300
root_height = 1
default_position_x = 10
new_position_x = default_position_x
default_position_y = 10
new_position_y = default_position_y
file_path = ""
font_size = 100
new_font_size = font_size
editor_started = False
result_image = None
watermark = ""
hold_original_image = None


###### FUNCTION DECLARATIONS #######


def open_file():
    global file_path, main_canvas, root_width, root_height, editor_started, image, root
    cancel_watermark()
    resize_window(root, 300, 10)
    main_canvas.destroy()
    file_path = filedialog.askopenfilename(title="Open Image File",)
    if file_path:
        image = resize_image_for_display(file_path)
        main_canvas = ttk.Canvas(root, width=root_width, height=root_height)
        main_canvas.pack(pady=10)
        show_image(image, main_canvas, root_width, root_height)


def resize_image_for_display(path):
    global root_width, root_height
    global image
    image = Image.open(file_path).convert("RGBA")
    root_width = image.width
    root_height = image.height
    while image.width > 800 or image.height > 600:
        root_height = int((image.height / 1.5))
        root_width = int((image.width / 1.5))
        image = image.resize((root_width, root_height), Image.LANCZOS)
        resize_window(root, root_width, root_height)

    return ImageTk.PhotoImage(image)


def resize_window(window, new_width, new_height):
    window.geometry(f"{new_width + 100}x{new_height + 80}+800+0")


def get_entry_text(event):
    global entry, watermark
    watermark = entry.get()
    if event.keysym:
        if event.keysym == "BackSpace":
            watermark = watermark[:-1]
        elif len(event.keysym) < 2:
            watermark = f"{watermark}{event.keysym}"
    else:
        watermark = ""
    apply_watermark()


def change_font_size():
    global new_font_size, var
    new_font_size = var.get()
    apply_watermark()


def open_watermark_editor():
    global editor_started
    if not editor_started:
        global file_path, root_width, root_height, image, root, size
        if file_path:
            global controls, entry, size, var, editor_display, editor_canvas
        # TOOLS FOR ADDING A WATERMARK

            # Container that will hold all controls
            controls = ttk.Frame(root, width=800, height=100)
            controls.pack(side=BOTTOM, fill="x")
            resize_window(root, root_width, root_height + 300)
            # Text entry field
            entry_label = ttk.Label(controls, text="Watermark Text:", background="white")
            entry_label.pack()
            entry = Entry(controls, width=30)
            entry.pack(side=TOP, padx=5, pady=10)
            entry.focus_set()
            entry.bind("<Key>", get_entry_text)



            # Container inside controls that holds all editing tools
            font_position_container = ttk.Frame(controls)
            font_position_container.pack()

            font_container = ttk.Frame(font_position_container, width=500, height=50)
            font_container.pack(side=LEFT, padx=10, pady=10)

            # Font Size Field
            font_label = ttk.Label(font_container, text="Font Size:", background="white",)
            font_label.pack(side=LEFT)
            var = IntVar(font_container)
            var.set(font_size)
            size = ttk.Spinbox(font_container, from_=1, to=500, increment=20, width=3, command=change_font_size, textvariable=var)
            size.pack(side=LEFT, padx=10)

            # Position Buttons
            position_container = ttk.Frame(font_position_container, width=500, height=50)
            position_container.pack(side=LEFT, padx=10)

            position_label = ttk.Label(position_container, text="Text Position:", background="white")
            position_label.pack(side=TOP, pady=0)

            b_left = ttk.Button(position_container, text='⇦', bootstyle=SUCCESS, width=2, command=lambda: move_watermark("left"))
            b_left.pack(side=LEFT, pady=10, padx=0)
            # Container that holds text position buttons
            up_down_container = ttk.Frame(position_container, width=20, height=50)
            up_down_container.pack(side=LEFT)

            b_down = ttk.Button(up_down_container, text='⇧', bootstyle=SUCCESS, width=2, command=lambda: move_watermark("down"))
            b_down.pack(side=TOP, padx=0, pady=15)

            b_up = ttk.Button(up_down_container, text='⇩', bootstyle=SUCCESS, width=2, command=lambda: move_watermark("up"))
            b_up.pack(side=TOP, pady=15, padx=5)

            b_right = ttk.Button(position_container, text='⇨', bootstyle=SUCCESS, width=2, command=lambda: move_watermark("right"))
            b_right.pack(side=RIGHT, padx=0)


            # A container that will hold buttons
            buttons = ttk.Frame(controls, width=300, height=50)
            buttons.pack(side=BOTTOM, fill="y", pady=10)
            # Buttons:
            b_add = ttk.Button(buttons, text='Add Watermark', bootstyle=SUCCESS, command=save_watermark_on_image)
            b_add.pack(side=LEFT, padx=5, pady=5)
            b_cancel = ttk.Button(buttons, text='Cancel', bootstyle=SECONDARY, command=cancel_watermark)
            b_cancel.pack(side=LEFT, padx=5, pady=5)
            editor_started = True
        else:
            showerror(title='Edit Image Error', message="Please, select image file")
    else:
        pass


def move_watermark(direction):
    global new_position_x, new_position_y, watermark
    if watermark != "":
        if direction == "right":
            new_position_x += 50
        if direction == "left":
            new_position_x -= 50
        if direction == "up":
            new_position_y += 50
        if direction == "down":
            new_position_y -= 50
        apply_watermark()
    else:
        showerror(title='Editor Error', message="No Text Added")


def apply_watermark():
    global entry, controls, root_width, root_height, main_canvas, file_path, new_position_x, new_position_y, new_font_size, editor_started, watermark, image, hold_original_image
    global result_image
    if watermark != "":
        with Image.open(file_path).convert("RGBA") as base:
            new_font_size = var.get()
            fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', new_font_size)

            # make a blank image for the text, initialized to transparent text color
            txt = Image.new("RGBA", base.size, (255, 255, 255, 0))

            # get a drawing context
            d = ImageDraw.Draw(txt)

            # draw text, half opacity
            d.text((new_position_x, new_position_y), watermark, font=fnt, fill=(255, 255, 255, 50))
            result_image = Image.alpha_composite(base, txt).convert("RGB")
            display_image = result_image.convert("RGBA").resize((root_width, root_height))
            hold_original_image = image
            image = ImageTk.PhotoImage(display_image)
            show_image(image, main_canvas, root_width, root_height)
    else:
        showerror(title='Editor Error', message="Add Watermark Text")


def save_watermark_on_image():
    global controls, image, main_canvas, root_width, root_height, root, editor_started, editor_canvas, old_image, file_path, watermark
    if watermark != "":
        controls.destroy()
        show_image(image, main_canvas, root_width, root_height)
        resize_window(root, root_width, root_height)
        editor_started = False
    else:
        showerror(title='Watermark Image Error', message="Enter Watermark Text")


def reset_watermark_position():
    global default_position_y, default_position_x, new_position_y, new_position_x
    new_position_x = default_position_x
    new_position_y = default_position_y


def cancel_watermark():
    global controls, image, main_canvas, root_width, root_height, root, editor_started, editor_canvas, old_image, file_path, result_image
    if editor_started:
        reset_watermark_position()
        controls.destroy()
        image = resize_image_for_display(file_path)
        show_image(image, main_canvas, root_width, root_height)
        resize_window(root, root_width, root_height)
        editor_started = False
        result_image = None
    else:
        editor_started = False


def show_image(file, canvas_name, window_width, window_height):
    display = canvas_name.create_image(0, 0, anchor="nw", image=None, tags='image')
    canvas_name.config(width=window_width, height=window_height)
    canvas_name.itemconfig(display, image=file)


def save():
    global file_path, result_image
    hold_path = file_path
    if result_image and not editor_started:
        print(hold_path)
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg")
        if file_path:
            if askyesno(title='Save Image', message='Do you want to save the image?'):
                # save the image to a file
                result_image.save(file_path)
                file_path = hold_path
                print(file_path)
    else:
        showerror(title='Save Image Error', message="You haven't edited a picture yet")
    file_path = hold_path


############## MAIN PROGRAM ##################
root = ttk.Window(themename="journal")
root.title("WaterMarkMe")
root.geometry(f"{root_width + 100}x{root_height + 80}+800+10")
# root.resizable(0, 0)
icon = ttk.PhotoImage(file='images/color-splash-projects.png')
root.iconphoto(False, icon)

toolbar = ttk.Frame(root, width=500, height=50)
toolbar.pack(side=TOP, fill="y")

image_icon = ttk.PhotoImage(file='images/add.png').subsample(1, 1)
text_icon = ttk.PhotoImage(file='images/text.png').subsample(1, 1)
save_icon = ttk.PhotoImage(file='images/save.png').subsample(1, 1)
draw_icon = ttk.PhotoImage(file='images/draw.png').subsample(1, 1)


image_button = ttk.Button(toolbar, image=image_icon, bootstyle=SECONDARY, command=open_file)
image_button.pack(side=LEFT, padx=5, pady=10)
text_button = ttk.Button(toolbar, image=text_icon, bootstyle=SECONDARY, command=open_watermark_editor)
text_button.pack(side=LEFT, padx=5, pady=10)
save_button = ttk.Button(toolbar, image=save_icon, bootstyle=SECONDARY, command=save)
save_button.pack(side=LEFT, padx=5, pady=10)

main_canvas = ttk.Canvas(root, width=root_width, height=root_height)
main_canvas.pack(pady=10)

root.mainloop()
