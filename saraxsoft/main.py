import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # For loading images
import serial
import time
import threading

import ttkbootstrap as ttk
import customtkinter as ctk


arduino_port = 'COM5'  
baud_rate = 9600

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Raspberry Pi UI")
        self.root.geometry("800x480")



        # Create a container for multiple pages
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # Initialize frames (pages)
        self.frames = {}
        self.selected_config = None  

        for F in (StartPage, SecondPage, ThirdPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]

        if page_name == "ThirdPage":
            frame.update_config()

        frame.tkraise()

    def set_config(self, config):
        self.selected_config = config


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

         # Title/Heading
        self.title_label = ctk.CTkLabel(self, text="Select a configuration", font=("Arial", 30, "bold"))
        self.title_label.pack(pady=20)


        # Customized style for the button
        style = ttk.Style()
        style.configure("My.TButton", font=("Helvetica", 14, "bold"), foreground="#FFFFFF", background="#4CAF50")
        
        # Box Container
        container = ttk.Frame(self, padding=20, style="TFrame", relief="flat")
        container.pack(pady=10)

        # Create three frames for the boxes, passing different image paths
        self.create_box(container, "Four", "images/four.png", "4-Arms")
        self.create_box(container, "Six", "images/six.png", "6-Arms")
        self.create_box(container, "Eight", "images/eight.png", "8-Arms")

    def create_box(self, container, label_text, image_path, config):
        # frame = ttk.Frame(container, relief="solid", borderwidth=60)
        frame = ttk.Frame(container, relief="flat", borderwidth=0)
        # frame.pack(side="left", padx=21, pady=53)

        frame.pack(side="left", padx=50, pady=53)


        # Load the image
        try:
            img = Image.open(image_path)
            img = img.resize((200, 200))
            img_tk = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image: {e}")
            img_tk = None

        if img_tk:
            image_label = ttk.Label(frame, image=img_tk)
            image_label.image = img_tk
        else:
            image_label = ttk.Label(frame, text="[Image Not Found]")

        image_label.pack(pady=10)

        # Use place to set the button within the frame, avoiding overlap with the other boxes
        button = ctk.CTkButton(
            master=frame,
            text=f"Select {label_text}",
            command=lambda: self.select_config(config, label_text)
        )
        button.pack(pady=10)  # Adds some vertical spacing between the image and button

        #button.place(relx=0.5, rely=1, anchor="s", y=-10)  # Centered at the bottom within each frame

    def select_config(self, config,label):
        self.controller.set_config(config)
        if label == "Four":
            self.controller.show_frame("SecondPage")
        else: 
            self.controller.show_frame("ThirdPage")


class SecondPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


        # Customized style for the button
        style = ttk.Style()
        style.configure("My.TButton", font=("Helvetica", 14, "bold"), foreground="#FFFFFF", background="#4CAF50")
        
        # Box Container
        container = ttk.Frame(self, padding=20, style="TFrame", relief="flat")
        container.pack(pady=20)

        self.create_box(container, "Plus", "images/four.png", "4-Arms")
        self.create_box(container, "X", "images/four_x.png", "4-Arms-X")

        # Load the icon image (adjust the path and size as needed)
        self.icon_image = ctk.CTkImage(Image.open("images/back.png"), size=(30, 30))  # Adjust size
        self.back_button_icon = ctk.CTkButton(
            self,
            image=self.icon_image,
            text="",
            text_color="Black",
            command=lambda: controller.show_frame("StartPage"),
            fg_color="green",
            hover_color="lightgreen",
            width=120,
            height=50,
            corner_radius=10  # Rounded corners
        )
        self.back_button_icon.pack(pady=10)  # Icon button without text

        # button = ttk.Button(self, text="Back to Main Page", command=lambda: controller.show_frame("StartPage"))
        # button.pack(pady=10)

    def create_box(self, container, label_text, image_path, config):
        frame = ttk.Frame(container, relief="flat", borderwidth=0)
        frame.pack(side="left", padx=50, pady=53)

        try:
            img = Image.open(image_path)
            img = img.resize((200, 200))
            img_tk = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image: {e}")
            img_tk = None

        if img_tk:
            image_label = ttk.Label(frame, image=img_tk)
            image_label.image = img_tk
        else:
            image_label = ttk.Label(frame, text="[Image Not Found]")

        image_label.pack(pady=10)

        # button = ttk.Button(frame, text=f"Select {label_text}", command=lambda: self.select_config(config))
        # button.pack(pady=10)

        # Use place to set the button within the frame, avoiding overlap with the other boxes
        button = ctk.CTkButton(
            master=frame,
            text=f"Select {label_text}",
            command=lambda: self.select_config(config)
        )
        button.pack(pady=10)  # Adds some vertical spacing between the image and button

    def select_config(self, config):
        '''Save the selected configuration and go to the ThirdPage'''
        self.controller.set_config(config)
        self.controller.show_frame("ThirdPage")


class ThirdPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller
        self.root = controller.root
        # Set the background color of the frame to white using customtkinter's fg_color
        self.configure(fg_color="white")  # Use fg_color for customtkinter widgets

        # Set up the serial connection
        self.ser = serial.Serial(arduino_port, baud_rate, timeout=1)  # Open the serial port
        self.check_thread = threading.Thread(target=self.check_serial)
        self.check_thread.daemon = True  # Daemonize thread for automatic exit
        self.check_thread.start()  # Start the thread

        # Title/Heading
        self.title_label = ctk.CTkLabel(self, text="Robotic Arms Configuration", font=("Arial", 30, "bold"))
        self.title_label.pack(pady=20)

        # Canvas to hold the circles
        self.canvas = ctk.CTkCanvas(self, width=400, height=400, bg="white", highlightthickness=0)
        self.canvas.pack(pady=10)


        # Set up circles
        self.circles = []
        self.count = 0
        self.current_circle = None
        self.blinking_task = None

        # # Back Button
        # self.back_button = ctk.CTkButton(self, text="Back to Main Page", command=lambda: controller.show_frame("StartPage"))
        # self.back_button.pack(pady=10)

        # # Load the icon image (adjust the path and size as needed)
        # self.icon_image = ctk.CTkImage(Image.open("images/back.png"), size=(40, 40))  # Adjust size
        # self.back_button_icon = ctk.CTkButton(self, image=self.icon_image, command=lambda: controller.show_frame("StartPage"))
        # self.back_button_icon.pack(pady=10)  # Icon button instead of text button

        # Load the icon image (adjust the path and size as needed)
        self.icon_image = ctk.CTkImage(Image.open("images/back.png"), size=(30, 30))  # Adjust size
        self.back_button_icon = ctk.CTkButton(
            self,
            image=self.icon_image,
            text="",
            text_color="Black",
            command=lambda: controller.show_frame("StartPage"),
            fg_color="green",
            hover_color="lightgreen",
            width=120,
            height=50,
            corner_radius=10  # Rounded corners
        )
        self.back_button_icon.pack(pady=10)  # Icon button without text

    def update_config(self):
        self.canvas.delete("all")

        config = self.controller.selected_config

        # Define positions, colors, and labels for different configurations
        if config == "4-Arms-X":
            self.circles = [
                (120, 120, "lightblue", "1"),   # Top-left
                (280, 120, "lightgreen", "2"),  # Top-right
                (280, 280, "lightcoral", "3"),  # Bottom-right
                (120, 280, "lightyellow", "4")  # Bottom-left
            ]
        elif config == "4-Arms":
            self.circles = [
                (200, 100, "lightblue", "1"),  # Top
                (300, 200, "lightgreen", "2"), # Right
                (200, 300, "lightcoral", "3"), # Bottom
                (100, 200, "lightyellow", "4") # Left
            ]
        elif config == "6-Arms":
            self.circles = [
                (200, 80, "lightblue", "1"),   # Top
                (280, 140, "lightgreen", "2"), # Top-right
                (280, 260, "lightcoral", "3"), # Bottom-right
                (200, 320, "lightyellow", "4"),# Bottom
                (120, 260, "lightpink", "5"),  # Bottom-left
                (120, 140, "lightcyan", "6")   # Top-left
            ]
        elif config == "8-Arms":
            self.circles = [
                (200, 80, "lightblue", "1"),   # Top
                (270, 120, "lightgreen", "2"), # Top-right
                (300, 200, "lightcoral", "3"), # Right
                (270, 280, "lightyellow", "4"),# Bottom-right
                (200, 320, "lightpink", "5"),  # Bottom
                (130, 280, "lightcyan", "6"),  # Bottom-left
                (100, 200, "lightgray", "7"),  # Left
                (130, 120, "lightgoldenrod", "8") # Top-left
            ]

        # Draw the circles with updated positions and colors
        self.draw_circles()

    def draw_circles(self):
        self.circle_ids = []
        for x, y, color, label in self.circles:
            circle_id = self.canvas.create_oval(x-30, y-30, x+30, y+30, fill=color, outline="black", width=2)
            self.canvas.create_text(x, y, text=label, font=("Arial", 14, "bold"), fill="black")
            self.circle_ids.append(circle_id)

        # Set the first circle as the current circle to be highlighted
        if self.circle_ids:
            self.current_circle = self.circle_ids[self.count]
            self.blink()

    def blink(self):
        current_colour = self.canvas.itemcget(self.current_circle, "fill")
        original_colour = self.get_original_color()
        
        # Toggle between red and original color for blink effect
        new_colour = "red" if current_colour != "red" else original_colour
        self.canvas.itemconfig(self.current_circle, fill=new_colour)
        
        self.blinking_task = self.root.after(500, self.blink)

    def get_original_color(self):
        # Returns the original color based on the current selected circle index
        return self.circles[self.count][2]

    def check_serial(self):
        while True:
            try:
                id_str = self.ser.readline().decode('utf-8').rstrip()
                print(id_str)
                if id_str.isdigit():
                    id = int(id_str)
                    if(id-4) == self.count:
                        self.next_circle()
            except serial.SerialException as e:
                print(f"Serial error: {e}")
            time.sleep(1)

    def close_serial(self):
        self.ser.close()

    def next_circle(self):
        if self.count == len(self.circle_ids)-1:
            self.close_serial()
            self.show_popup()

        if self.blinking_task is not None:
            self.root.after_cancel(self.blinking_task)
            self.blinking_task = None

        self.canvas.itemconfig(self.current_circle, fill=self.get_original_color())
        self.count = (self.count+1) % len(self.circle_ids)
        self.current_circle = self.circle_ids[self.count]
        self.blink()

    def show_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Success")
        popup.geometry("300x200")
        popup.config(bg="white")  # Set background color of the popup window to white

        # Label Styling with CTkLabel
        label = ctk.CTkLabel(popup, text="All arms are correctly mounted.", font=("Arial", 14, "bold"), width=250, height=30, anchor="center")
        label.pack(pady=30)  # Add some vertical padding for a neat look

        # Customize the Close Button
        close_button = ctk.CTkButton(popup, text="Close", command=popup.destroy, font=("Arial", 12), width=120)
        close_button.pack(pady=10)  # Add some padding for spacing


def main():
    #root = tk.Tk()
    
    # create CTk window
    root = ctk.CTk()
    app = MainWindow(root)

    # button = customtkinter.CTkButton(master=root, text="Hello world!")
    # button.place(x=400,y=240)

    root.mainloop()


if __name__ == "__main__":
    main()