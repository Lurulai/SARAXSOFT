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


# Define the first page (StartPage)
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
            img = Image.open(image_path)  # Open the image from the provided path
            img = img.resize((100, 100))  # Resize image if necessary
            img_tk = ImageTk.PhotoImage(img)  # Convert to ImageTk for Tkinter
        except Exception as e:
            print(f"Error loading image: {e}")
            img_tk = None

        # Add the image
        if img_tk:
            image_label = ttk.Label(frame, image=img_tk)
            image_label.image = img_tk  # Keep a reference to avoid garbage collection
        else:
            image_label = ttk.Label(frame, text="[Image Not Found]")

        image_label.pack(pady=10)

        if label_text == "Four":
            next_page = "SecondPage"
        else:
            next_page = "ThirdPage"

        # Add the button
        button = ttk.Button(frame, text=f"Select {label_text}", command=lambda: self.controller.show_frame(next_page))
        button.pack(pady=10)


# Define the second page (SecondPage)
class SecondPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="This is the Second Page")
        label.pack()

        label = ttk.Label(self, text="This is another text")
        label.pack()

        label = ttk.Label(self, text="This is something else")
        label.pack()

        # Create a container for the three boxes
        container = ttk.Frame(self)
        container.pack(pady=20)

        # Create three frames for the boxes, passing different image paths
        self.create_box(container, "Plus", "images/four.png")
        self.create_box(container, "X", "images/four_x.png")

        button = ttk.Button(self, text="Back to Main Page", command=lambda: controller.show_frame("StartPage"))
        button.pack(pady=10)

    def create_box(self, container, label_text, image_path):
        frame = ttk.Frame(container, relief="solid", borderwidth=60)
        frame.pack(side="left", padx=21, pady=53)

        # Load the image
        try:
            img = Image.open(image_path)  # Open the image from the provided path
            img = img.resize((100, 100))  # Resize image if necessary
            img_tk = ImageTk.PhotoImage(img)  # Convert to ImageTk for Tkinter
        except Exception as e:
            print(f"Error loading image: {e}")
            img_tk = None

        # Add the image
        if img_tk:
            image_label = ttk.Label(frame, image=img_tk)
            image_label.image = img_tk  # Keep a reference to avoid garbage collection
        else:
            image_label = ttk.Label(frame, text="[Image Not Found]")

        image_label.pack(pady=10)

        # Add the button
        button = ttk.Button(frame, text=f"Select {label_text}", command=lambda: self.controller.show_frame("ThirdPage"))
        button.pack(pady=10)

# Define the second page (SecondPage)
class ThirdPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="This is the Third Page")
        label.pack()

        label = ttk.Label(self, text="This is another text")
        label.pack()

        label = ttk.Label(self, text="This is something else")
        label.pack()

        button = ttk.Button(self, text="Back to Main Page", command=lambda: controller.show_frame("StartPage"))
        button.pack(pady=10)


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
