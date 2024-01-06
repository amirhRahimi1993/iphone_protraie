"""
    Author: Israel Dryer
    Modified: 2021-12-11
    Adapted from: https://github.com/israel-dryer/Mini-VLC-Player
"""
from tkinter import filedialog

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Emoji
from tkinter import messagebox

from PIL import Image, ImageTk
from SAM import SAM

class MediaPlayer(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.image_path= ""
        self.x=-1
        self.y=-1
        self.coordination = []
        self.pack(fill=BOTH, expand=YES)
        self.hdr_var = ttk.StringVar()
        self.elapsed_var = ttk.DoubleVar(value=0)
        self.remain_var = ttk.DoubleVar(value=190)
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
        img_path = 'SAME_100000566__tbo_11___100000566__hb_35.png'
        self.demo_media = ttk.PhotoImage(file=img_path)
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

        btn_open_file = ttk.Button(
            master=container,
            text=Emoji.get('open file folder'),
            bootstyle=SECONDARY,
            padding=10,
            command=self.change_image
        )
        btn_open_file.pack(side=LEFT, fill=X, expand=YES)

        btn_savepoints_img = ttk.Button(
            master=container,
            text=Emoji.get('MEMO'),
            padding=10,
            command = self.__store_point
        )
        btn_savepoints_img.pack(side=LEFT, fill=X, expand=YES)

        btn_process_the_image = ttk.Button(
            master=container,
            text= "apply processing",
            padding=10,
            style='success.TButton',
            command=self.call_uncle_SAM()
        )
        btn_process_the_image.pack(side=LEFT, fill=X, expand=YES)

        btn_previous = ttk.Button(
            master=container,
            text=Emoji.get('BLACK LEFT-POINTING TRIANGLE'),
            padding=10,
        )
        btn_previous.pack(side=LEFT, fill=X, expand=YES)

        btn_next = ttk.Button(
            master=container,
            text=Emoji.get('BLACK RIGHT-POINTING TRIANGLE'),
            padding=10,
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
        )
        btn_extract_img.pack(side=LEFT, fill=X, expand=YES)

        btn_save_result = ttk.Button(
            master=container,
            text=Emoji.get('FLOPPY DISK'),
            padding=10,
        )
        btn_save_result.pack(side=LEFT, fill=X, expand=YES)

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
        """Create frame with progress meter with lables"""
        self.container = ttk.Frame(self)
        self.container.pack(fill=X, expand=YES, pady=10)

        self.elapse = ttk.Label(self.container, text='00:00')
        self.elapse.pack(side=LEFT, padx=10)

        self.scale = ttk.Scale(
            master=self.container,
            command=self.on_progress,
            bootstyle=SECONDARY
        )
        self.scale.pack(side=LEFT, fill=X, expand=YES)

        self.remain = ttk.Label(self.container, text='03:10')
        self.remain.pack(side=LEFT, fill=X, padx=10)

    def call_uncle_SAM(self):
        s = SAM(self.image_path,"vit_h","sam_vit_h_4b8939.pth","cpu")
        return s.process_data(self.coordination)

    def on_progress(self, val: float):
        """Update progress labels when the scale is updated."""
        elapsed = self.elapsed_var.get()
        remaining = self.remain_var.get()
        total = int(elapsed + remaining)

        elapse = int(float(val) * total)
        elapse_min = elapse // 60
        elapse_sec = elapse % 60

        remain_tot = total - elapse
        remain_min = remain_tot // 60
        remain_sec = remain_tot % 60

        self.elapsed_var.set(elapse)
        self.remain_var.set(remain_tot)

        self.elapse.configure(text=f'{elapse_min:02d}:{elapse_sec:02d}')
        self.remain.configure(text=f'{remain_min:02d}:{remain_sec:02d}')

    def change_image(self):
        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*"))
        )
        if file_path:
            # Load the image using PIL
            image = Image.open(file_path)
            # Resize the image to 1024x768
            image = image.resize((1024, 768))
            # Convert the image for Tkinter
            new_media = ImageTk.PhotoImage(image)
            # Display the resized image
            self.media.configure(image=new_media)
            self.media.image = new_media  # Keep a reference to avoid garbage collection
            self.image_path = file_path



if __name__ == '__main__':

    app = ttk.Window("Media Player", "yeti")
    mp = MediaPlayer(app)
    #mp.scale.set(0.35)  # set default
    app.mainloop()