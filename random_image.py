import os
from io import BytesIO
import random
import threading
import dearpygui.dearpygui as dpg
import urllib.request
import numpy
import win32clipboard
import sys
import requests
from PIL import Image, ImageFont, ImageDraw
import dearpygui.dearpygui as dpg

filedir=os.path.dirname(os.path.abspath(__file__))

#root = tk.Tk()
#root.title("RandomImage")

# TODO: Store images to folders, save file nicknames, lists, etc.
link_list = []
image_list = []
image_pointer = 0

class RandomImage:
    def __init__(self, filepath=None, image_id=None, width=None, height=None, channels=None, data=None, texture_id=None, active=False):
        maxwidth = 1000
        maxheight = 1000
        self.active = active
        self.width = width
        self.height = height
        self.channels = channels
        self.data = data
        self.filepath = filepath
        self.image_id = image_id
        self.texture_id = texture_id

    def display(self):
        ...

    def get(self):
        return self.image
    
    def __repr__(self):
        return self.image_id

def send_to_clipboard():
    try:
        filepath = get_active_image().filepath
        image = Image.open(filepath)

        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
    except:
        ...

def get_active_image():
    for img in image_list:
        if img.active == True:
            return img
    return None

def set_active_image(image):
    try:
        get_active_image().active = False
    except:
        ...
    image.active = True

def rand_char():
    return random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')

def imgur_linkgen():
    imgur_id = ""
    for _ in range(5):
        imgur_id += "{}".format(rand_char())
    link = "https://i.imgur.com/{}.jpeg".format(imgur_id)
    link_list.append(link)
    return [link] + [imgur_id]

def delete_image():
    if image_pointer > 0:
        os.remove(get_active_image().filepath)
        image_list.remove(image_list[image_pointer-1])
        display_previous()

# TODO: Add loading timeout + animation
# TODO: Functionalize delete, image fetching, and replace repeated get() calls
def display_next():
    global image_list, image_pointer
    dpg.delete_item("display_window", children_only=True)
    if image_pointer == len(image_list):
        while(1):
            # TODO: Change how linkgen gets passed
            input_id = dpg.get_value("image_id_input")
            # TODO: Update how this works if link size needs to change
            if input_id != None and len(input_id) == 5:
                linkgen = ["https://i.imgur.com/{}.jpeg".format(input_id)] + [input_id]
                dpg.configure_item("image_id_input")
            else:
                linkgen = imgur_linkgen()
            link = linkgen[0]
            imgur_id = linkgen[1]
            img_data = requests.get(link).content
            img_path = os.getcwd()+"/images/{}.jpg".format(imgur_id)
            with open(img_path, 'wb') as writer:
                writer.write(img_data)
            width, height, channels, data = dpg.load_image(img_path)
            with dpg.texture_registry():
                texture_id = dpg.add_static_texture(width, height, data)
            if(width != 161 and height != 81):
                image = RandomImage(img_path, imgur_id, width, height, channels, data, texture_id, active=True)
                image_list.append(image)
                set_active_image(image)
                dpg.add_image(texture_id, tag=imgur_id, parent="display_window")
                dpg.configure_item("display_window", label="Image Display: {}".format(get_active_image().image_id))
                image_pointer += 1
                return None
            os.remove(img_path)
    else:
        set_active_image(image_list[image_pointer])
        image_pointer += 1
        dpg.add_image(get_active_image().texture_id, tag=get_active_image().image_id, parent="display_window")
        dpg.configure_item("display_window", label="Image Display: {}".format(get_active_image().image_id))

def display_previous():
        global image_pointer
        if image_pointer > 1:
            dpg.delete_item("display_window", children_only=True)
            image_pointer -= 1
            set_active_image(image_list[image_pointer-1])
            with dpg.texture_registry():
                texture_id = dpg.add_static_texture(get_active_image().width, get_active_image().height, get_active_image().data)
            dpg.add_image(texture_id, tag=get_active_image().image_id, parent="display_window")
            dpg.configure_item("display_window", label="Image Display: {}".format(get_active_image().image_id))
        else:
            dpg.delete_item("display_window", children_only=True)

def dpg_thread():
    gui_width = 1000
    gui_height = 800
    cmd_window_height = 25
    dpg.create_context()
    dpg.create_viewport(title='Random Image Tool', width=gui_width, height=gui_height)
    with dpg.window(tag="display_window", label="Image Display", width=gui_width, height=gui_height-cmd_window_height):
        ...
    with dpg.window(tag="command_window", label="Image Command Panel", height=cmd_window_height, width=gui_width):
        with dpg.group(horizontal=False):
            with dpg.group(horizontal=True):
                dpg.add_button(tag="back_button", label="< BACK", callback=display_previous)
                dpg.add_button(tag="copy_button", label="COPY", callback=send_to_clipboard)
                dpg.add_button(tag="delete_button", label="DELETE", callback=delete_image)
                dpg.add_button(tag="next_button", label="NEXT >", callback=display_next)
            dpg.add_text("Custom Imgur ID: ")
            dpg.add_input_text(tag="image_id_input", default_value="", width=100)
    dpg.set_item_pos("display_window", (0, cmd_window_height+75))
    dpg.set_item_pos("command_window", (0, 0))
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    # TODO: Use threading and DearPyGUI for the interface
    # TODO: Add funcs for accessing other websites (spotify, yt, etc.), different filetypes, and more!
    # TODO: Add queue that caches a certain amount of items ahead of time for smooth loading of next file.
    gui_thread = threading.Thread(name="gui_thread", target=dpg_thread)
    gui_thread.start()
    while(1):
        ...