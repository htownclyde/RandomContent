import os
import time
import random
import requests
import threading
import win32clipboard
from io import BytesIO
import dearpygui.dearpygui as dpg
from PIL import Image

filedir=os.path.dirname(os.path.abspath(__file__))

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
    
active_image = RandomImage(None, None, None, None, None, None, None, False)

def send_to_clipboard():
    try:
        filepath = active_image.filepath
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

def rand_char(nums=True):
   if nums == True: return random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
   else: return random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

def imgur_linkgen():
    imgur_id = ""
    for _ in range(5):
        imgur_id += "{}".format(rand_char(True))
    link = "https://i.imgur.com/{}.jpeg".format(imgur_id)
    link_list.append(link)
    return [link] + [imgur_id]

def imgbb_linkgen():
    imgbb_id = ""
    for _ in range(7):
        imgbb_id += "{}".format(rand_char(True))
    link = "https://ibb.co/{}".format(imgbb_id)
    link_list.append(link)
    return [link] + [imgbb_id]

def delete_image():
    global image_list, active_image, image_pointer
    if image_pointer > 0 and active_image != None:
        try: 
            os.remove(active_image.filepath)
            image_list.remove(image_list[image_pointer-1])
        except:
            ...
        if image_pointer > 1:
            display_previous()
        else:
            image_pointer -= 1
            dpg.delete_item("display_window", children_only=True)

# TODO: Add loading timeout + animation
# TODO: Functionalize delete, image fetching, and replace repeated get() calls
# TODO: Use threading to get 5+ images at once and throw out filtered/broken images, append good ones
def display_next():
    global image_list, active_image, image_pointer
    generate_threads = []
    try: gen_count = int(dpg.get_value("batch_input"))
    except: gen_count = 1
    if gen_count > 1 and image_pointer == len(image_list):
        #start_index = image_pointer
        for i in range(gen_count):
            generate_threads.append(threading.Thread(name="generate_thread_{}".format(i), target=generate))
        for thread in generate_threads:
            thread.start()
        #for thread in generate_threads:
        #    thread.join() 
        #image_pointer = start_index
        #active_image = image_list[image_pointer]
        #display_previous()
    else:
        generate(update=True)

def display_first():
    global image_list, active_image, image_pointer
    if image_pointer > 1:
        image_pointer = 1
        active_image = image_list[image_pointer-1]
        display()

def display_previous():
        global image_list, active_image, image_pointer
        if image_pointer > 1:
            image_pointer -= 1
            active_image = image_list[image_pointer-1]
            display()

def display_last():
    global image_list, active_image, image_pointer
    if image_pointer != len(image_list) and image_pointer >= 1:
        image_pointer = len(image_list)
        active_image = image_list[image_pointer-1]
        display()

def display(texture_id=active_image.texture_id, tag=active_image.image_id, width=active_image.width, height=active_image.height):
    global image_list, active_image, image_pointer
    while active_image.texture_id == None: ...
    dpg.delete_item("display_window", children_only=True)
    if active_image.width < gui_width*0.95 and active_image.height < gui_height*0.75:
        dpg.add_image(active_image.texture_id, tag=active_image.image_id, parent="display_window")
        dpg.configure_item("display_window", label="[{}/{}] Image Display: {} ({}x{}) (Original)"
                        .format(image_pointer, len(image_list), active_image.image_id,
                                active_image.width, active_image.height))
    else:
        new_height = gui_height*0.75
        new_width = new_height*active_image.width/active_image.height
        if new_width > gui_width*0.95:
            new_width = gui_width*0.95
            new_height = new_width*active_image.height/active_image.width
        dpg.add_image(active_image.texture_id, tag=active_image.image_id, width=new_width, height=new_height, parent="display_window")
        dpg.configure_item("display_window", label="[{}/{}] Image Display: {} ({}x{}) (Resized)"
                        .format(image_pointer, len(image_list), active_image.image_id,
                                active_image.width, active_image.height))

def generate(update=False):
    global image_list, active_image, image_pointer
    if image_pointer == len(image_list):
        while(1):
            # TODO: Change how linkgen gets passed
            input_id = dpg.get_value("image_id_input")
            # TODO: Update how this works if link size needs to change
            if input_id != None and len(input_id) == 5:
                linkgen = ["https://i.imgur.com/{}.jpeg".format(input_id)] + [input_id]
                dpg.configure_item("image_id_input")
            else:
                #linkgen = imgbb_linkgen()
                linkgen = imgur_linkgen()
            link = linkgen[0]
            imgur_id = linkgen[1]
            while(1):
                try:
                    dpg.configure_item("display_window", label="[{}/{}] Image Display: Getting next image...".format(image_pointer, len(image_list)))
                    img_data = requests.get(link).content
                    img_path = os.getcwd()+"/images/{}.jpg".format(imgur_id)
                    break
                except:
                    ...
            # TODO: Change how images folder is handled, how missing images are handled to save time
            while(1):
                try: os.mkdir("images")
                except: ...
                try:
                    with open(img_path, 'wb') as writer:
                        #print(pybase64.b64decode(img_data))
                        writer.write(img_data)
                        break
                except:
                    dpg.configure_item("display_window", label="[{}/{}] Image Display: Problem getting content. Retrying...".format(image_pointer, len(image_list)))

            try: width, height, channels, data = dpg.load_image(img_path)
            except: ...
            with dpg.texture_registry():
                texture_id = dpg.add_static_texture(width, height, data)
            if width != 161 and height != 81:
                image = RandomImage(img_path, imgur_id, width, height, channels, data, texture_id, active=True)
                image_list.append(image)
                active_image = image
                if update == True:
                    image_pointer += 1
                    display(texture_id, imgur_id, width, height)
                return None
            os.remove(img_path) 
    else:
        image_pointer += 1
        active_image = image_list[image_pointer-1]
        display()

def dpg_thread():
    global gui_width, gui_height
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
                dpg.add_button(tag="start_button", label="<<", callback=display_first)
                dpg.add_button(tag="back_button", label="< BACK", callback=display_previous)
                dpg.add_button(tag="copy_button", label="COPY", callback=send_to_clipboard)
                dpg.add_button(tag="delete_button", label="DELETE", callback=delete_image)
                dpg.add_button(tag="next_button", label="NEXT >", callback=display_next)
                dpg.add_button(tag="end_button", label=">>", callback=display_last)
            with dpg.group(horizontal=True):
                dpg.add_text("Custom Imgur ID:  ")
                dpg.add_input_text(tag="image_id_input", default_value="", width=75)
            with dpg.group(horizontal=True):
                dpg.add_text("Images per click: ")
                dpg.add_input_text(tag="batch_input", default_value="1", width=50)

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