import tkinter as tk
from ui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.title("Raspberry Pi UI")
    root.geometry("800x480")  # Set screen size to match Raspberry Pi screen resolution
    
    app = MainWindow(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()