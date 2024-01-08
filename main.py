"""
    Author: Israel Dryer
    Modified: 2021-12-11
    Adapted from: https://github.com/israel-dryer/Mini-VLC-Player
"""
import copy
import math
from tkinter import filedialog

import torch
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Emoji
from tkinter import messagebox

from PIL import Image, ImageTk, ImageFilter
from SAM import SAM
import numpy as np
import os
from datetime import datetime

class Filter_image(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.mask_number_var = None
        self.scroll_bar_value = 0
        self.one_d_twod = None
        self.media = None
        self.demo_media = None
        self.processed_image = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "vit_h"
        self.model_path = "sam_vit_h_4b8939.pth"
        self.SIZE= (1024, 768)
        self.counter = 0
        self.mask_number =2
        self.image_path= ""
        self.x=-1
        self.y=-1
        self.coordination = []
        self.pack(fill=BOTH, expand=YES)
        self.hdr_var = ttk.StringVar()
        self.elapsed_var = ttk.DoubleVar(value=50)
        self.remain_var = ttk.DoubleVar(value=100)
        self.show_unshow = 0
        self.create_header()
        self.create_media_window()
        self.create_buttonbox()

    def create_header(self):
        """The application header to display user messages"""
        self.hdr_var.set("Open a file to begin playback")
        lbl = ttk.Label(
            master=self,
            textvariable=self.hdr_var,
            bootstyle=(LIGHT, INVERSE),
            padding=10
        )
        lbl.pack(fill=X, expand=True)

    def create_media_window(self):
        """Create frame to contain media"""

        img_path = 'background.jpg'
        image = Image.open(img_path).resize(self.SIZE)
        self.demo_media = ImageTk.PhotoImage(image)
        self.media = ttk.Label(self, image=self.demo_media)
        self.media.pack(fill=BOTH, expand=YES)

        # Bind the click event
        self.media.bind("<Button-1>", self.on_image_click)

    def on_image_click(self, event):
        # Get the x and y coordinates of the click relative to the image widget
        self.x, self.y = event.x, event.y
        self.hdr_var.set(f"Coordination you have clicked is {self.x} and {self.y}")
        print(f"Clicked at x={self.x}, y={self.y}")

    def create_buttonbox(self):
        """Create buttonbox with media controls"""
        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES)
        ttk.Style().configure('TButton', font="-size 14")

        # First row
        row1 = ttk.Frame(container)
        row1.pack(fill=X, expand=YES)

        btn_open_file = ttk.Button(row1, text="Open File", padding=10, command=self.change_image)
        btn_open_file.pack(side=LEFT, fill=X, expand=YES)

        btn_savepoints_img = ttk.Button(row1, text="Save Point", padding=10, command=self.__store_point)
        btn_savepoints_img.pack(side=LEFT, fill=X, expand=YES)

        # Second row
        row2 = ttk.Frame(container)
        row2.pack(fill=X, expand=YES)

        btn_process_the_image = ttk.Button(row2, text="Process Image", padding=10, style='success.TButton', command=self.call_uncle_SAM)
        btn_process_the_image.pack(fill=X, expand=YES)

        # Third row (initially hidden)
        self.row3 = ttk.Frame(container)
        self.row3.pack(fill=X, expand=YES)
        self.row3.pack_forget()  # Hide this row initially

        # Add other buttons and dropdown to the third row
        self.create_third_row_buttons(self.row3)

    def reveal_third_row(self):
        """Reveal the third row with a fade-in effect"""
        self.row3.pack(fill=X, expand=YES)
        # Add fade-in effect if needed

    def create_third_row_buttons(self, parent):

        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES)
        ttk.Style().configure('TButton', font="-size 14")

        btn_previous = ttk.Button(
            master=container,
            text=Emoji.get('BLACK LEFT-POINTING TRIANGLE'),
            padding=10,
            command= lambda: self.__create_image(-1)
        )
        btn_previous.pack(side=LEFT, fill=X, expand=YES)

        btn_next = ttk.Button(
            master=container,
            text=Emoji.get('BLACK RIGHT-POINTING TRIANGLE'),
            padding=10,
            command=lambda: self.__create_image(1)
        )
        btn_next.pack(side=LEFT, fill=X, expand=YES)

        btn_blur_img = ttk.Button(
            master=container,
            text=Emoji.get('YIN YANG'),
            padding=10,
            command=self.__average_filter_apply
        )
        btn_blur_img.pack(side=LEFT, fill=X, expand=YES)

        btn_extract_img = ttk.Button(
            master=container,
            text=Emoji.get('MAGNET'),
            padding=10,
            command=self.__eliminate_the_background
        )
        btn_extract_img.pack(side=LEFT, fill=X, expand=YES)

        btn_save_result = ttk.Button(
            master=container,
            text=Emoji.get('FLOPPY DISK'),
            padding=10,
            command=self.__save_img
        )
        btn_save_result.pack(side=LEFT, fill=X, expand=YES)
        self.mask_number_var = ttk.StringVar(value='3')  # Default value set to '3'
        mask_dropdown = ttk.Combobox(
            master=container,
            textvariable=self.mask_number_var,
            values=('1', '2', '3'),
            state='readonly'
        )
        mask_dropdown.pack(side=RIGHT, fill=X, expand=YES)
        mask_dropdown.bind("<<ComboboxSelected>>", self.on_mask_selection)

    def on_mask_selection(self, event):
        """Handle mask number selection from dropdown"""
        selection = self.mask_number_var.get()
        if selection == '1':
            self.mask_number = 0
        elif selection == '2':
            self.mask_number = 1
        else:  # Default case for '3'
            self.mask_number = 2

    def __store_point(self):
        if self.x == -1:
            messagebox.showinfo("Error", "Cant find new point")
            return
        self.coordination.append([self.x,self.y])
        self.x , self.y = -1,-1
    def __average_filter_apply(self):
        if self.show_unshow == 0:
            self.create_progress_meter()
            self.scale.pack()  # Show the progress bar
        else:
            self.scale.pack_forget()  # Hide the progress bar
            self.container.pack_forget()
        self.show_unshow = 1 - self.show_unshow  # Toggle the state

    def create_progress_meter(self):
        """Create frame with progress meter with labels"""
        self.container = ttk.Frame(self)
        self.container.pack(fill=X, expand=YES, pady=10)

        self.elapse = ttk.Label(self.container, text='-50')
        self.elapse.pack(side=LEFT, padx=10)

        self.scale = ttk.Scale(
            master=self.container,
            from_=-50, to=50,  # Set the range from -50 to 50
            command=self.on_progress,
            bootstyle=SECONDARY
        )
        self.scale.pack(side=LEFT, fill=X, expand=YES)

        self.remain = ttk.Label(self.container, text='50')
        self.remain.pack(side=LEFT, fill=X, padx=10)

    def on_progress(self, val: int):
        """Update progress labels when the scale is updated."""
        # Convert the scale value to an elapsed and remaining value
        val = int(float(val))
        elapsed = val + 50  # Shift the scale to start from 0
        remaining = 100 - elapsed  # Calculate the remaining value
        self.elapsed_var.set(elapsed)
        self.remain_var.set(remaining)

        # Update the labels
        self.elapse.configure(text=f'{elapsed}')
        self.remain.configure(text=f'{remaining}')
        if val != self.scroll_bar_value:
            self.scroll_bar_value = val
            self.__start_blurring()

    def __blurring(self,img1,img2):
        intention_image = np.zeros(img1.shape, dtype=np.uint8)
        true_mask = np.where(self.processed_image["mask"][self.mask_number] == True)
        false_mask = np.where(self.processed_image["mask"][self.mask_number] == False)
        intention_image[true_mask] = img1[true_mask]
        intention_image[false_mask] = img2[false_mask]
        intention_image = Image.fromarray(intention_image)
        return intention_image

    def __eliminate_the_background(self):
        img1 = self.processed_image["rgb"]
        print(img1.shape)
        intention_image = np.zeros(img1.shape, dtype=np.uint8)
        true_mask = np.where(self.processed_image["mask"][self.mask_number] == True)
        intention_image[true_mask] = img1[true_mask]
        intention_image = Image.fromarray(intention_image)
        self.__set_image(intention_image)
    def __start_blurring(self):
        rgb_img1 = np.array(Image.fromarray(copy.deepcopy(self.processed_image["rgb"])).filter(ImageFilter.GaussianBlur(math.fabs(int(self.scroll_bar_value/5)))))
        rgb_img2 = copy.deepcopy(self.processed_image["rgb"])
        if self.scroll_bar_value < 0:
            intent_img=self.__blurring(rgb_img1,rgb_img2)
        elif self.scroll_bar_value == 0:
            intent_img= Image.fromarray(rgb_img1)
        else:
            intent_img= self.__blurring(rgb_img2, rgb_img1)
        self.__set_image(intent_img)
    def call_uncle_SAM(self)->dict:

        print("process started")
        s = SAM(self.image_path,self.model_name,self.model_path,self.device,self.SIZE)
        self.processed_image = s.process_data(self.coordination)
        self.one_d_twod = []
        for k in self.processed_image.keys():
            if k == 'mask':
                continue
            for k1 in self.processed_image.keys():
                if k1 == k or k1=='mask':
                    continue
                self.one_d_twod.append(f"{k}^^{k1}")
        print("process finished")
        return self.processed_image
    def __putpixel(self,mask_true,key):

        print(f"len of the mask {len(self.processed_image['mask'])}")
        self.img[np.where(self.processed_image['mask'][self.mask_number] == mask_true)] = self.processed_image[key][
            np.where(self.processed_image['mask'][self.mask_number] == mask_true)]
    def __create_image(self,move):
        self.counter += move
        self.counter = self.counter % len(self.one_d_twod)
        key_a,key_b = self.one_d_twod[self.counter].split("^^")
        self.img= np.zeros(self.processed_image[key_a].shape)
        self.__putpixel(True,key_a)
        self.__putpixel(False, key_b,)
        img = Image.fromarray(np.uint8(self.img))
        self.__set_image(img)


    def change_image(self):
        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*"))
        )
        if file_path:
            # Load the image using PIL
            image = Image.open(file_path)
            self.__set_image(image)
            self.image_path = file_path
    def __set_image(self,image):
        image = image.resize(self.SIZE)
        # Convert the image for Tkinter
        new_media = ImageTk.PhotoImage(image)
        # Display the resized image
        self.media.configure(image=new_media)
        self.media.image = new_media
        self.save_img = image# Keep a reference to avoid garbage collection

    def __save_img(self):
        dt = datetime.now()
        # epoch time
        epoch_time = datetime(2023, 12, 1)

        # subtract Datetime from epoch datetime
        delta = (dt - epoch_time)
        if os.path.exists("save_img") == False:
            os.mkdir("save_img")
        self.save_img.save(f"save_img/{int(delta.total_seconds())}.jpeg")



if __name__ == '__main__':

    app = ttk.Window("Filter Image by SAM", "yeti")
    mp = Filter_image(app)
    #mp.scale.set(0.35)  # set default
    app.mainloop()