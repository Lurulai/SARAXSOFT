# """Contains the MountingFrame class, which is a custom tkinter frame that contains the mounting page."""

# from __future__ import annotations

# import customtkinter
# from PIL import Image  # type: ignore
# from saraxsoft.settings import AppConfig # type: ignore
# from saraxsoft.ui.common.label_separator import LabelSeparator # type: ignore
# import threading
# import time
# import serial
# from typing import List

# # Constants for Arduino connection
# arduino_port = 'COM8'  
# baud_rate = 9600

# class MountingFrame(customtkinter.CTkFrame):
#     """A custom tkinter frame for the Mounting page."""
#     def __init__(self, parent: customtkinter.CTk) -> None:

#         """
#         Initialize the MountingFrame.

#         Parameters
#         ----------
#         parent : customtkinter.CTk
#             The parent of the frame.
#         """
#         super().__init__(parent, corner_radius=0, fg_color="white")
#         self.parent = parent
#         self.stop_thread = threading.Event()
#         self.circle_ids: List[int] = []
#         self.circles = []
#         self.count = 0
#         self.current_circle = None
#         self.blinking_task = None

#         try:
#             self.ser = serial.Serial(arduino_port, baud_rate, timeout=1)
#             print(f"Serial object: {self.ser}")
#             time.sleep(2)  # Allow Arduino to reset
#         except serial.SerialException as e:
#             print(f"Failed to initialize serial connection: {e}")
#             self.ser = None

#         self._create_ui()
#         self.check_thread = threading.Thread(target=self.check_serial)
#         self.check_thread.daemon = True
#         self.check_thread.start()

#         self.grid_rowconfigure(0, weight=0)
#         self.grid_rowconfigure(1, weight=1)
#         self.grid_columnconfigure(0, weight=1)
        

#     def _create_ui(self) -> None:
#         """Create the UI components for the Mounting page."""
#         # Top-level title
#         self.title_label = customtkinter.CTkLabel(
#             self, text="Robotic Arms Configuration", font=("Arial", 30, "bold"), fg_color="white"
#         )
#         self.title_label.grid(row=0, column=0, pady=10, sticky="n")

#         # Canvas for mounting positions
#         self.canvas = customtkinter.CTkCanvas(self, width=400, height=400, bg="white", highlightthickness=0)
#         self.canvas.grid(row=1, column=0, padx=200, pady=0, sticky="n")

#     def _populate_circles(self, config: str) -> None:
#         """
#         Populate the circle data based on the configuration.

#         Parameters
#         ----------
#         config : str
#             The selected configuration (e.g., "4-Arms", "4-Arms-X", "6-Arms", "8-Arms").
#         """
#         if config == "FOUR_ARMS":
#             self.circles = [(200, 100, "red", "1"), (300, 200, "red", "2"), (200, 300, "red", "3"), (100, 200, "red", "4")]
#         elif config == "FOUR_ARMS_X":
#             self.circles = [(120, 120, "red", "1"), (280, 120, "red", "2"), (280, 280, "red", "3"), (120, 280, "red", "4")]
#         elif config == "SIX_ARMS":
#             self.circles = [
#                 (200, 80, "red", "1"),
#                 (280, 140, "red", "2"),
#                 (280, 260, "red", "3"),
#                 (200, 320, "red", "4"),
#                 (120, 260, "red", "5"),
#                 (120, 140, "red", "6"),
#             ]
#         elif config == "EIGHT_ARMS":
#             self.circles = [
#                 (200, 80, "red", "1"),
#                 (270, 120, "red", "2"),
#                 (300, 200, "red", "3"),
#                 (270, 280, "red", "4"),
#                 (200, 320, "red", "5"),
#                 (130, 280, "red", "6"),
#                 (100, 200, "red", "7"),
#                 (130, 120, "red", "8"),
#             ]
#         else:
#             self.circles = []  # Default to an empty list if the configuration is unknown
#         self._draw_circles()

#     def _draw_circles(self) -> None:
#         """Draw the circles on the canvas."""
#         self.circle_ids = []

        
#         for x, y, color, label in self.circles:
            
#             circle_id = self.canvas.create_oval(x - 30, y - 30, x + 30, y + 30, fill=color, outline="black", width=2)
#             self.canvas.create_text(x, y, text=label, font=("Arial", 14, "bold"), fill="black")
#             self.circle_ids.append(circle_id)

#         print(f"Circle IDs: {self.circle_ids}")  # Debugging output

#         if self.circle_ids:
#             self.current_circle = self.circle_ids[self.count]
#             self._blink()

#     def _blink(self) -> None:
#         """Create a blinking effect for the current circle."""
#         current_color = self.canvas.itemcget(self.current_circle, "fill")
#         new_color = "yellow" if current_color != "yellow" else self.circles[self.count][2]
#         self.canvas.itemconfig(self.current_circle, fill=new_color)
#         self.blinking_task = self.parent.after(500, self._blink)

#     def _go_back(self) -> None:
#         """Navigate back to the ConfigurationFrame."""
#         # self.parent.navigate_to_configuration()  # Ensure this method exists in the parent

#     def get_original_color(self) -> str:
#         """Return the original color of the current selected circle."""
#         return self.circles[self.count][2]

#     def check_serial(self):
#         if self.ser is None:
#             print("Serial connection not initialized.")
#             return

#         while not self.stop_thread.is_set():
#             try:
#                 id_str = self.ser.readline().decode("utf-8").rstrip()
#                 if id_str:
#                     print(f"Received: {id_str}")
#                 else:
#                     print("No data received. Waiting...")
#                 if id_str.isdigit():
#                     id = int(id_str)
#                     if (id - 4) == self.count:
#                         self.next_circle()
#             except (serial.SerialException, AttributeError) as e:
#                 print(f"Serial connection lost: {e}")
#                 break
#             time.sleep(1)

#     def close_serial(self) -> None:
#         """Close the serial connection."""
#         if self.ser:
#             self.ser.close()

#     def next_circle(self) -> None:
#         """Transition to the next circle."""
#         if not self.circle_ids:
#             print("No circles to transition.")
#             return

#         if self.current_circle not in self.circle_ids:
#             print("Current circle is invalid.")
#             return

#         if self.count == len(self.circle_ids) - 1:
#             self.close_serial()
#             self.show_popup()

#         if self.blinking_task is not None:
#             self.parent.after_cancel(self.blinking_task)
#             self.blinking_task = None

#         self.canvas.itemconfig(self.current_circle, fill="lightgreen")
#         self.count = (self.count + 1) % len(self.circle_ids)
#         self.current_circle = self.circle_ids[self.count]
#         self._blink()

#     def show_popup(self) -> None:
#         """Display a popup when all circles are completed."""
#         popup = customtkinter.CTkToplevel(self)
#         popup.title("Success")
#         popup.geometry("300x200")
#         popup.configure(fg_color="white")

#         # Popup Label
#         label = customtkinter.CTkLabel(
#             popup,
#             text="All arms are correctly mounted.",
#             font=("Arial", 14, "bold"),
#         )
#         label.pack(pady=30)

#         # Close Button
#         close_button = customtkinter.CTkButton(
#             popup,
#             text="Close",
#             command=popup.destroy,
#         )
#         close_button.pack(pady=10)
