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
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Create a container for the three boxes
        container = ttk.Frame(self)
        container.pack(pady=20)

        # Create three frames for the boxes, passing different image paths
        self.create_box(container, "Four", "images/four.png")
        self.create_box(container, "Six", "images/six.png")
        self.create_box(container, "Eight", "images/eight.png")

    def create_box(self, container, label_text, image_path):
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

        if label_text == "Four":
            next_page = "SecondPage"
        else:
            next_page = "ThirdPage"

        button = ttk.Button(frame, text=f"Select {label_text}", command=lambda: self.controller.show_frame(next_page))
        button.pack(pady=10)


class SecondPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="This is the Second Page")
        label.pack()

        container = ttk.Frame(self)
        container.pack(pady=20)

        self.create_box(container, "Plus", "images/four.png")
        self.create_box(container, "X", "images/four_x.png")

        button = ttk.Button(self, text="Back to Main Page", command=lambda: controller.show_frame("StartPage"))
        button.pack(pady=10)

    def create_box(self, container, label_text, image_path):
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

        button = ttk.Button(frame, text=f"Select {label_text}", command=lambda: self.controller.show_frame("ThirdPage"))
        button.pack(pady=10)


class ThirdPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.root = controller.root

        label = ttk.Label(self, text="This is the Third Page")
        label.pack()

        # Create the canvas for the circles
        self.canvas = tk.Canvas(self, width=400, height=400)
        self.canvas.pack()

        # Create individual circles as objects
        self.circle1 = self.canvas.create_oval(180, 80, 220, 120, fill="lightblue")
        self.canvas.create_text(200, 100, text="1", font=("Arial", 12))
        
        self.circle2 = self.canvas.create_oval(280, 180, 320, 220, fill="lightgreen")
        self.canvas.create_text(300, 200, text="2", font=("Arial", 12))
        
        self.circle3 = self.canvas.create_oval(180, 280, 220, 320, fill="lightcoral")
        self.canvas.create_text(200, 300, text="3", font=("Arial", 12))
        
        self.circle4 = self.canvas.create_oval(80, 180, 120, 220, fill="lightyellow")
        self.canvas.create_text(100, 200, text="4", font=("Arial", 12))

        # Track blinking circle
        self.current_circle = self.circle1
        self.blinking_task = None  # To track the after() call ID

        # Start the blinking
        self.blink()

        # Bind space key to change circle
        self.root.bind("<space>", self.next_circle)

        # Back button
        button = ttk.Button(self, text="Back to Main Page", command=lambda: controller.show_frame("StartPage"))
        button.pack(pady=10)

    def blink(self):
        current_colour = self.canvas.itemcget(self.current_circle, "fill")
        original_colour = {
            self.circle1: "lightblue",
            self.circle2: "lightgreen",
            self.circle3: "lightcoral",
            self.circle4: "lightyellow"
        }[self.current_circle]
        
        new_colour = "red" if current_colour != "red" else original_colour
        self.canvas.itemconfig(self.current_circle, fill=new_colour)
        
        self.blinking_task = self.root.after(500, self.blink)

    def next_circle(self, event):
        if self.blinking_task is not None:
            self.root.after_cancel(self.blinking_task)
            self.blinking_task = None
        
        original_colour = {
            self.circle1: "lightblue",
            self.circle2: "lightgreen",
            self.circle3: "lightcoral",
            self.circle4: "lightyellow"
        }[self.current_circle]
        self.canvas.itemconfig(self.current_circle, fill=original_colour)
        
        next_circle = {
            self.circle1: self.circle2,
            self.circle2: self.circle3,
            self.circle3: self.circle4,
            self.circle4: self.circle1
        }[self.current_circle]
        
        self.current_circle = next_circle
        self.blink()


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()



if __name__ == "__main__":
    main()

