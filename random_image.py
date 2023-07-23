import os
import io
import random
import tkinter as tk
import urllib.request
from PIL import ImageTk, Image, ImageFont, ImageDraw
import dearpygui.dearpygui as dpg

filedir=os.path.dirname(os.path.abspath(__file__))

root = tk.Tk()
root.title("RandomImage")

# TODO: Store images to folders, save file nicknames, lists, etc.
link_list = []

class WebImage:
    def __init__(self, url):
        global image
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        maxwidth = 1000
        maxheight = 1000
        if(image.width > maxwidth or image.height > maxheight):
            image = image.resize(size=(round(image.width/2), round(image.height/2)))
            print("resized")
        self.image = ImageTk.PhotoImage(image)

    def get(self):
        return self.image

def rand_char():
    return random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')

def imgur_linkgen():
    imgur_id = ""
    for _ in range(5):
        imgur_id += "{}".format(rand_char())
    print(imgur_id)
    link = "https://i.imgur.com/{}.jpg".format(imgur_id)
    link_list.append(link)
    return link

def save_image():
    img.save()

def display_next():
    image_display.configure(image=get_random_image())

def get_random_image():
    global img
    attempts = 50
    for _ in range(attempts):
        img = WebImage(imgur_linkgen()).get()
        if(image.width != 161 and image.height != 81):
            break
    return img

get_random_image()
image_display = tk.Label(root, image=img)
image_display.pack(side="bottom")
next_button = tk.Button(root, text="SHOW NEXT RANDOM IMAGE", command=display_next)
next_button.pack(side="bottom", anchor="nw")
save_button = tk.Button(root, text="SAVE IMAGE", command=save_image)
save_button.pack(side="bottom", anchor="nw")

if __name__ == "__main__":
    # TODO: Use threading and DearPyGUI for the interface
    # TODO: Add funcs for accessing other websites (spotify, yt, etc.), different filetypes, and more!
    # TODO: Add queue that caches a certain amount of items ahead of time for smooth loading of next file.
    root.mainloop()