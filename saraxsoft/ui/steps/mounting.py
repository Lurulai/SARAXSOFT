"""Contains the MountingFrame class, which is a custom tkinter frame that contains the mounting page."""

from __future__ import annotations

import customtkinter
from PIL import Image  # type: ignore
from saraxsoft.settings import AppConfig # type: ignore
from saraxsoft.ui.common.label_separator import LabelSeparator # type: ignore
import threading
import time
import sys
import os
# import serial
from typing import List
from saraxsoft.ui.steps.mcp_py_test import MemoryController
# Constants for Arduino connection
arduino_port = 'COM8'  
baud_rate = 9600

EEPROM_ADDRESS_BASE = 0x0010  # Starting address for circles


class MountingFrame(customtkinter.CTkFrame):
    """A custom tkinter frame for the Mounting page."""
    def __init__(self, parent: customtkinter.CTk) -> None:

        """
        Initialize the MountingFrame.

        Parameters
        ----------
        parent : customtkinter.CTk
            The parent of the frame.
        """
        super().__init__(parent, corner_radius=0, fg_color="white")

        self.mcp_chip = MemoryController(serial_number="0001757257", cs_pin_number=0)
        #self.addresses = [EEPROM_ADDRESS_BASE + i for i in range(8)]  # 0x0010, 0x0011, 0x0012, 0x0013
        self.stop=0
        self.parent = parent
        self.stop_thread = threading.Event()
        self.circle_ids: List[int] = []
        self.circles = []
        self.count = 0
        self.current_circle = None
        self.blinking_task = None
        

        # try:
        #     self.ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        #     print(f"Serial object: {self.ser}")
        #     time.sleep(2)  # Allow Arduino to reset
        # except serial.SerialException as e:
        #     print(f"Failed to initialize serial connection: {e}")
        #     self.ser = None

        self._create_ui()
        

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        

    def _create_ui(self) -> None:
        """Create the UI components for the Mounting page."""
        # Top-level title
        self.title_label = customtkinter.CTkLabel(
            self, text="Robotic Arms Configuration", font=("Arial", 30, "bold"), fg_color="white"
        )
        self.title_label.grid(row=0, column=0, pady=10, sticky="n")

        # Canvas for mounting positions
        self.canvas = customtkinter.CTkCanvas(self, width=400, height=400, bg="white", highlightthickness=0)
        self.canvas.grid(row=1, column=0, padx=200, pady=0, sticky="n")

    def _populate_circles(self, config: str) -> None:
        """
        Populate the circle data based on the configuration.

        Parameters
        ----------
        config : str
            The selected configuration (e.g., "4-Arms", "4-Arms-X", "6-Arms", "8-Arms").
        """
        if config == "FOUR_ARMS":
            self.circles = [(200, 100, "red", "1"), (300, 200, "red", "2"), (200, 300, "red", "3"), (100, 200, "red", "4")]
            self.max_circles = 4
            self.addresses = [EEPROM_ADDRESS_BASE + i for i in range(self.max_circles)]  # 0x0010, 0x0011, 0x0012, 0x0013
            
        elif config == "FOUR_ARMS_X":
            self.circles = [(120, 120, "red", "1"), (280, 120, "red", "2"), (280, 280, "red", "3"), (120, 280, "red", "4")]
            self.max_circles = 4
            self.addresses = [EEPROM_ADDRESS_BASE + i for i in range(self.max_circles)]  # 0x0010, 0x0011, 0x0012, 0x0013
            

        elif config == "SIX_ARMS":
            self.circles = [
                (200, 80, "red", "1"),
                (280, 140, "red", "2"),
                (280, 260, "red", "3"),
                (200, 320, "red", "4"),
                (120, 260, "red", "5"),
                (120, 140, "red", "6"),
            ]
            self.max_circles = 6
            self.addresses = [EEPROM_ADDRESS_BASE + i for i in range(self.max_circles)]  # 0x0010, 0x0011, 0x0012, 0x0013
            

        elif config == "EIGHT_ARMS":
            self.circles = [
                (200, 80, "red", "1"),
                (270, 120, "red", "2"),
                (300, 200, "red", "3"),
                (270, 280, "red", "4"),
                (200, 320, "red", "5"),
                (130, 280, "red", "6"),
                (100, 200, "red", "7"),
                (130, 120, "red", "8"),
            ]
            self.max_circles = 8
            self.addresses = [EEPROM_ADDRESS_BASE + i for i in range(self.max_circles)]  # 0x0010, 0x0011, 0x0012, 0x0013
            

        else:
            self.circles = []  # Default to an empty list if the configuration is unknown
        self._draw_circles()
        self.check_thread = threading.Thread(target=self.check_rotation)
        self.check_thread.daemon = True
        self.check_thread.start()

    def _draw_circles(self) -> None:
        """Draw the circles on the canvas."""
        self.circle_ids = []
        
        for x, y, color, label in self.circles:
            circle_id = self.canvas.create_oval(x - 30, y - 30, x + 30, y + 30, fill=color, outline="black", width=2)
            self.canvas.create_text(x, y, text=label, font=("Arial", 14, "bold"), fill="black")
            self.circle_ids.append(circle_id)

        print(f"Circle IDs: {self.circle_ids}")  # Debugging output

        if self.circle_ids:
            self.current_circle = self.circle_ids[self.count]
            self._blink()

    def _blink(self) -> None:
        """Create a blinking effect for the current circle."""
        current_color = self.canvas.itemcget(self.current_circle, "fill")
        new_color = "yellow" if current_color != "yellow" else self.circles[self.count][2]
        self.canvas.itemconfig(self.current_circle, fill=new_color)
        self.blinking_task = self.parent.after(500, self._blink)

    def _go_back(self) -> None:
        """Navigate back to the ConfigurationFrame."""
        # self.parent.navigate_to_configuration()  # Ensure this method exists in the parent

    def get_original_color(self) -> str:
        """Return the original color of the current selected circle."""
        return self.circles[self.count][2]

    def check_rotation(self):
        """
        Continuously write a value to address 0x0010 in the EEPROM, then read it back.
        Compare the read value with self.count to decide whether to call next_circle().
        """

        while not self.stop_thread.is_set() and self.stop == 0 and self.count <= 3:
            try:
                if self.count == 4:
                    print("All circles have been processed.")
                    self.canvas.itemconfig(self.current_circle, fill="lightgreen")
                    self.show_popup()
                    self.stop = 1  # Stop further processing
                    break  # Exit the method

                current_address = EEPROM_ADDRESS_BASE
                # Define the expected value based on the circle's position (1, 0, 1, 0, ...)
                input_value = [1,0,1,0]
                
                # if self.count == 2:
                #     input_value = 45

                # # Write the value to the current EEPROM address
                # self.data_to_write = (1).to_bytes(1, 'big')
                # self.mcp_chip.write_to_eeprom(address=EEPROM_ADDRESS_BASE, data=self.data_to_write)
                # self.mcp_chip.wait_for_write_completion()

                # print(f"Wrote value {self.data_to_write} to EEPROM address {hex(current_address)}.")
                # data_read = self.mcp_chip.read_from_eeprom(address=EEPROM_ADDRESS_BASE, length=1)
                # print(f"Read value {int.from_bytes(data_read, 'big')}")

                # self.mcp_chip.select_pin(1)
                # self.data_to_write = (0).to_bytes(1, 'big')
                # self.mcp_chip.write_to_eeprom(address=EEPROM_ADDRESS_BASE, data=self.data_to_write)
                # self.mcp_chip.wait_for_write_completion()
                # print(f"Wrote value {self.data_to_write} to EEPROM address {hex(current_address)}.")
                # data_read = self.mcp_chip.read_from_eeprom(address=EEPROM_ADDRESS_BASE, length=1)
                # print(f"Read value {int.from_bytes(data_read, 'big')}")

                # self.mcp_chip.select_pin(2)
                # self.data_to_write = (1).to_bytes(1, 'big')
                # self.mcp_chip.write_to_eeprom(address=EEPROM_ADDRESS_BASE, data=self.data_to_write)
                # self.mcp_chip.wait_for_write_completion()
                # print(f"Wrote value {self.data_to_write} to EEPROM address {hex(current_address)}.")
                # data_read = self.mcp_chip.read_from_eeprom(address=EEPROM_ADDRESS_BASE, length=1)
                # print(f"Read value {int.from_bytes(data_read, 'big')}")


                # self.mcp_chip.select_pin(3)
                # self.data_to_write = (0).to_bytes(1, 'big')
                # self.mcp_chip.write_to_eeprom(address=EEPROM_ADDRESS_BASE, data=self.data_to_write)
                # self.mcp_chip.wait_for_write_completion()
                # print(f"Wrote value {self.data_to_write} to EEPROM address {hex(current_address)}.")
                # data_read = self.mcp_chip.read_from_eeprom(address=EEPROM_ADDRESS_BASE, length=1)
                # print(f"Read value {int.from_bytes(data_read, 'big')}")

                
                # Read back the value from EEPROM
                self.mcp_chip.select_pin(self.count)
                data_read = self.mcp_chip.read_from_eeprom(address=EEPROM_ADDRESS_BASE, length=1)
                if not data_read:
                    print(f"No data returned from EEPROM at address {hex(current_address)}. Waiting...")
                    time.sleep(1)
                    continue

                id_val = int.from_bytes(data_read, 'big')
                # print(f"Received from EEPROM at address {hex(current_address)}: {id_val}")

                # Check if the read value matches the written value
                if id_val == input_value[self.count]:
                    print(f"Correct input '{id_val}' received at address {hex(current_address)}. Next circle...")
                    self.next_circle()
                else:
                    print(f"Wrong input '{id_val}' at address {hex(current_address)}. Expected '{input_value[self.count]}'.")
                    self.stop=1
                    break

                    # Optionally, decide whether to continue or break
                    # For continuous monitoring, do not break

                # # Write 1 byte (value 4) to EEPROM address 0x0010
                # self.data_to_write = (1).to_bytes(1, 'big')
                # self.mcp_chip.write_to_eeprom(address=0x0010, data=self.data_to_write)

                # # Read 1 byte from EEPROM address 0x0010
                # data_read = self.mcp_chip.read_from_eeprom(address=0x0010, length=1)
                # if not data_read:

                #     print("No data returned from EEPROM. Waiting...")
                #     time.sleep(1)
                #     continue

                # # Convert the single byte to an integer
                # id_val = int.from_bytes(data_read, 'big')

                # if id_val:
                #     print(f"Received from EEPROM: {id_val}")
                # else:
                #     print("EEPROM returned 0. Waiting...")

                # # Compare (id_val - 1) with self.count
                # if (id_val - 1 == self.count):
                #     self.next_circle()

            except Exception as e:
                # If you're specifically dealing with serial exceptions, you could catch them:
                # except (serial.SerialException, AttributeError) as e:
                print(f"Error during EEPROM operation: {e}")
                break

        time.sleep(1)



    # def close_serial(self) -> None:
    #     """Close the serial connection."""
    #     if self.ser:
    #         self.ser.close()

    def next_circle(self) -> None:
        """Transition to the next circle."""
        if not self.circle_ids:
            print("No circles to transition.")
            return

        if self.current_circle not in self.circle_ids:
            print("Current circle is invalid.")
            return
        
        

        # if self.count == len(self.circle_ids) - 1:
        #     # self.close_serial()
        #     self.show_popup()

        if self.blinking_task is not None:
            self.parent.after_cancel(self.blinking_task)
            self.blinking_task = None

        self.canvas.itemconfig(self.current_circle, fill="lightgreen")
        # print(f"Circle {self.count + 1} completed.")
        # self.count = (self.count + 1) % len(self.circle_ids)
        # if self.count == self.max_circles:
        #     print("All circles have been processed.")
        #     self.show_popup()
        #     self.stop=1
        #     return  # All circles are done
        # self.current_circle = self.circle_ids[self.count]
        # self._blink()
        # time.sleep(2)

        # Move to the next circle
        self.count += 1
        # Check if this is the last circle
        if self.count == self.max_circles:
            print("All circles have been processed.")
            self.canvas.itemconfig(self.current_circle, fill="lightgreen")
            self.show_popup()
            self.stop = 1  # Stop further processing
            return  # Exit the method
        self.current_circle = self.circle_ids[self.count]
        # print(f"Moving to circle {self.count + 1}.")
        self._blink()
        time.sleep(4)

    def center(self, window_width: int, window_height: int) -> tuple[float, float]:
        """Return the coordinates to center the window."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        return (x, y)
    
    def show_popup(self) -> None:
        """Display a popup when all circles are completed."""
        popup = customtkinter.CTkToplevel(self)
        popup.title("Success")
        # popup.geometry("300x200")
        popup.configure(fg_color="white")

        center = self.center(window_width=330, window_height=245)
        popup.geometry(f"{300}x{200}+{int(center[0])}+{int(center[1])}")

        # Keep the popup on top
        popup.attributes("-topmost", True)
        popup.focus_force()  # Focus on the popup window
        

        # Popup Label
        label = customtkinter.CTkLabel(
            popup,
            text="All arms are correctly mounted.",
            font=("Arial", 14, "bold"),
        )
        label.pack(pady=30)

        def close_all():
            popup.destroy()  # Close the popup
            self.quit()      # Stop the main event loop
            self.destroy()   # Destroy the main window

        # Close Button
        close_button = customtkinter.CTkButton(
            popup,
            text="Close",
            command=close_all,
        )
        close_button.pack(pady=10)




