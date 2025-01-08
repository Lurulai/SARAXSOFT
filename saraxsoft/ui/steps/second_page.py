# """Second page in the application."""

# from __future__ import annotations

# import tkinter as tk
# from tkinter import ttk
# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from saraxsoft.ui.main_window import MainWindow


# class SecondPage(tk.Frame):
#     """Second page of the application."""

#     def __init__(self, parent: tk.Frame, controller: MainWindow) -> None:
#         """
#         Initialize the SecondPage.

#         Parameters
#         ----------
#         parent : tk.Frame
#             The parent frame.
#         controller : MainWindow
#             The window/frame controller.
#         """
#         tk.Frame.__init__(self, parent)
#         self.controller = controller
#         self.root = controller.root
#         # self.ser = serial.Serial(
#         #     arduino_port, baud_rate, timeout=1
#         # )  # Open the serial port
#         # self.check_thread = threading.Thread(target=self.check_serial)
#         # self.check_thread.daemon = True  # Daemonize thread for automatic exit
#         # self.check_thread.start()  # Start the thread

#         label = ttk.Label(self, text="Drone Arm Configuration")
#         label.pack()

#         self.canvas = tk.Canvas(self, width=400, height=400)
#         self.canvas.pack()

#         self.circles = []
#         self.circle_ids: list[int] = []
#         self.count = 0
#         self.current_circle = 0
#         self.blinking_task = None

#         # self.root.bind("<space>", self.next_circle)

#         button = ttk.Button(
#             self,
#             text="Back to Main Page",
#             command=lambda: controller.show_frame("FirstPage"),
#         )
#         button.pack(pady=10)

#     def update_config(self):
#         self.canvas.delete("all")

#         config = self.controller.selected_config

#         if config == "4-Arms-X":
#             self.circles = [
#                 (120, 120, "lightblue", "1"),  # Top-left
#                 (280, 120, "lightgreen", "2"),  # Top-right
#                 (280, 280, "lightcoral", "3"),  # Bottom-right
#                 (120, 280, "lightyellow", "4"),  # Bottom-left
#             ]
#         if config == "4-Arms":
#             self.circles = [
#                 (200, 100, "lightblue", "1"),  # Top
#                 (300, 200, "lightgreen", "2"),  # Right
#                 (200, 300, "lightcoral", "3"),  # Bottom
#                 (100, 200, "lightyellow", "4"),  # Left
#             ]
#         elif config == "6-Arms":
#             self.circles = [
#                 (200, 80, "lightblue", "1"),  # Top
#                 (280, 140, "lightgreen", "2"),  # Top-right
#                 (280, 260, "lightcoral", "3"),  # Bottom-right
#                 (200, 320, "lightyellow", "4"),  # Bottom
#                 (120, 260, "lightpink", "5"),  # Bottom-left
#                 (120, 140, "lightcyan", "6"),  # Top-left
#             ]
#         elif config == "8-Arms":
#             self.circles = [
#                 (200, 80, "lightblue", "1"),  # Top
#                 (270, 120, "lightgreen", "2"),  # Top-right
#                 (300, 200, "lightcoral", "3"),  # Right
#                 (270, 280, "lightyellow", "4"),  # Bottom-right
#                 (200, 320, "lightpink", "5"),  # Bottom
#                 (130, 280, "lightcyan", "6"),  # Bottom-left
#                 (100, 200, "lightgray", "7"),  # Left
#                 (130, 120, "lightgoldenrod", "8"),  # Top-left
#             ]

#         self.draw_circles()

#     def draw_circles(self):
#         for x, y, color, label in self.circles:
#             circle_id = self.canvas.create_oval(
#                 x - 20, y - 20, x + 20, y + 20, fill=color
#             )
#             self.canvas.create_text(x, y, text=label, font=("Arial", 12))
#             self.circle_ids.append(circle_id)

#         if self.circle_ids:
#             self.current_circle = self.circle_ids[self.count]
#             self.blink()

#     def blink(self):
#         current_colour = self.canvas.itemcget(self.current_circle, "fill")
#         original_colour = self.get_original_color()

#         new_colour = "red" if current_colour != "red" else original_colour
#         self.canvas.itemconfig(self.current_circle, fill=new_colour)

#         self.blinking_task = self.root.after(500, self.blink)

#     # def check_serial(self):
#     #     while True:
#     #         try:
#     #             id_str = self.ser.readline().decode("utf-8").rstrip()
#     #             print(id_str)
#     #             if id_str.isdigit():
#     #                 id = int(id_str)
#     #                 if (id - 4) == self.count:
#     #                     self.next_circle()
#     #         except serial.SerialException as e:
#     #             print(f"Serial error: {e}")
#     #         time.sleep(1)

#     # def close_serial(self):
#     #     self.ser.close()

#     def next_circle(self):
#         if self.count == len(self.circle_ids) - 1:
#             # self.root.unbind("<space>")
#             # self.close_serial()
#             self.show_popup()

#         if self.blinking_task is not None:
#             self.root.after_cancel(self.blinking_task)
#             self.blinking_task = None

#         self.canvas.itemconfig(self.current_circle, fill=self.get_original_color())
#         self.count = (self.count + 1) % len(self.circle_ids)
#         self.current_circle = self.circle_ids[self.count]
#         self.blink()

#     def get_original_color(self):
#         return self.circles[self.count][2]

#     def show_popup(self):
#         popup = tk.Toplevel(self.root)
#         popup.title("Success!")

#         popup.geometry("300x200")

#         label = ttk.Label(popup, text="Arms good to go!")
#         label.pack(pady=20)

#         close_button = ttk.Button(popup, text="Close", command=self.root.destroy)
#         close_button.pack(pady=10)
