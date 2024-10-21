import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # For loading images

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
        self.selected_config = None  # To store the selected configuration

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

        # Create a container for the three boxes
        container = ttk.Frame(self)
        container.pack(pady=20)

        # Create three frames for the boxes, passing different image paths
        self.create_box(container, "Four", "images/four.png", "4-Arms")
        self.create_box(container, "Six", "images/six.png", "6-Arms")
        self.create_box(container, "Eight", "images/eight.png", "8-Arms")

    def create_box(self, container, label_text, image_path, config):
        frame = ttk.Frame(container, relief="solid", borderwidth=60)
        frame.pack(side="left", padx=21, pady=53)

        # Load the image
        try:
            img = Image.open(image_path)
            img = img.resize((100, 100))
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

        button = ttk.Button(frame, text=f"Select {label_text}", 
                            command=lambda: self.select_config(config,label_text))
        button.pack(pady=10)

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

        label = ttk.Label(self, text="This is the Second Page")
        label.pack()

        container = ttk.Frame(self)
        container.pack(pady=20)

        self.create_box(container, "Plus", "images/four.png", "4-Arms")
        self.create_box(container, "X", "images/four_x.png", "4-Arms-X")

        button = ttk.Button(self, text="Back to Main Page", command=lambda: controller.show_frame("StartPage"))
        button.pack(pady=10)

    def create_box(self, container, label_text, image_path, config):
        frame = ttk.Frame(container, relief="solid", borderwidth=60)
        frame.pack(side="left", padx=21, pady=53)

        try:
            img = Image.open(image_path)
            img = img.resize((100, 100))
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

        button = ttk.Button(frame, text=f"Select {label_text}", command=lambda: self.select_config(config))
        button.pack(pady=10)

    def select_config(self, config):
        '''Save the selected configuration and go to the ThirdPage'''
        self.controller.set_config(config)
        self.controller.show_frame("ThirdPage")


class ThirdPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.root = controller.root

        label = ttk.Label(self, text="Drone Arm Configuration")
        label.pack()

        self.canvas = tk.Canvas(self, width=400, height=400)
        self.canvas.pack()

        self.circles = []
        self.current_circle = None
        self.blinking_task = None

        self.root.bind("<space>", self.next_circle)

        button = ttk.Button(self, text="Back to Main Page", command=lambda: controller.show_frame("StartPage"))
        button.pack(pady=10)

    def update_config(self):
        self.canvas.delete("all")

        config = self.controller.selected_config

        if config == "4-Arms-X":
            self.circles = [
                (120, 120, "lightblue", "1"),   # Top-left
                (280, 120, "lightgreen", "2"),  # Top-right
                (280, 280, "lightcoral", "3"),  # Bottom-right
                (120, 280, "lightyellow", "4")  # Bottom-left
            ]
        if config == "4-Arms":
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

        self.draw_circles()

    def draw_circles(self):
        self.circle_ids = []
        for x, y, color, label in self.circles:
            circle_id = self.canvas.create_oval(x-20, y-20, x+20, y+20, fill=color)
            self.canvas.create_text(x, y, text=label, font=("Arial", 12))
            self.circle_ids.append(circle_id)

        if self.circle_ids:
            self.current_circle = self.circle_ids[0]
            self.blink()

    def blink(self):
        current_colour = self.canvas.itemcget(self.current_circle, "fill")
        original_colour = self.get_original_color(self.current_circle)
        
        new_colour = "red" if current_colour != "red" else original_colour
        self.canvas.itemconfig(self.current_circle, fill=new_colour)
        
        self.blinking_task = self.root.after(500, self.blink)

    def next_circle(self, event):
        if self.blinking_task is not None:
            self.root.after_cancel(self.blinking_task)
            self.blinking_task = None

        current_index = self.circle_ids.index(self.current_circle)
        self.canvas.itemconfig(self.current_circle, fill=self.get_original_color(self.current_circle))

        self.current_circle = self.circle_ids[(current_index+1) % len(self.circle_ids)]
        self.blinking_task = self.root.after(500, self.blink)

    def get_original_color(self, circle_id):
        index = self.circle_ids.index(circle_id)
        return self.circles[index][2]
        


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
