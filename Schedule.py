import tkinter as tk
from tkinter import filedialog
# import customtkinter
import csv
import os

class ScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Schedule")

        # Initialization of employees and availability
        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.availability_filename = 'schedule_availability.csv'
        self.employees_filename = 'employees.csv'
        self.employees = []
        self.load_employees()

        self.hours_dict = {day: {emp: [] for emp in self.employees} for day in self.days_of_week}
        self.availability_dict = {emp: [] for emp in self.employees}
        self.load_availability()

        # Create a canvas for drawing
        self.employee_height = 25
        self.employee_pad = 120
        self.canvas_width = 800
        self.canvas_height = self.employee_height * len(self.employees) + 100
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(padx=10, pady=10)

        # Create a frame to hold the Availability, day selector, undo, and reset buttons side by side
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        # Availability Button
        self.availability_button = tk.Button(control_frame, text="Availability", command=self.open_availability_window)
        self.availability_button.pack(side="left", padx=5)
        # Day Selector (If new day is selected, fetch canvas of that day and also clear undo stack)
        self.selected_day = tk.StringVar(value=self.days_of_week[0])
        self.day_selector = tk.OptionMenu(control_frame, self.selected_day, *self.days_of_week, command=self.update_weekday)
        self.day_selector.pack(side="left", padx=5)
        # Undo Button
        self.undo_stack = []  # Stack for undo actions
        self.undo_button = tk.Button(control_frame, text="Undo", command=self.undo)
        self.undo_button.pack(side="left", padx=5)
        # Reset Button
        self.reset_button = tk.Button(control_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side="left", padx=5)
        # Export CSV Button
        self.save_button = tk.Button(control_frame, text="Download", command=self.save_to_csv)
        self.save_button.pack(side="left", padx=5)
       

        # Draw lines for available employees and hour labels
        self.draw_lines()

        # Bind mouse events for drawing
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.drawing)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

        # Store drawn lines
        self.lines = []

        # Display saved hours
        label_frame = tk.Frame(self.root)
        label_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.label_canvas = tk.Canvas(label_frame)
        self.label_canvas.pack(side="left", fill="both", expand=True)
        self.label_container = tk.Frame(self.label_canvas)
        self.label_canvas.create_window((0, 0), window=self.label_container, anchor="nw")
        self.hours_text = tk.Text(self.label_container, wrap="word", bg="white", height=10, width=50)
        self.hours_text.pack(pady=10, padx=10, fill="x") 
        self.label_container.pack(side="top", padx=10) 
        self.update_hours_label()


    def load_employees(self):
        if os.path.exists(self.employees_filename):
            with open(self.employees_filename, mode='r') as file:
                reader = csv.reader(file)
                self.employees = [row[0] for row in reader]
        else:
            default_employees = ["Emmanuel", "Nick", "Tej", "Javed", "Santosh", "Janvi", "Yash", "Divya", "Rohan", "Rahi"]
            with open(self.employees_filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                for emp in default_employees:
                    writer.writerow([emp]) 

    def load_availability(self):
        if os.path.exists(self.availability_filename):
            with open(self.availability_filename, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    row = ','.join(row)
                    emp, days = row.split(',')[0], row.split(',')[1:]
                    self.availability_dict[emp] = days
        else:
            with open(self.availability_filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                for emp in self.employees:
                    writer.writerow([emp, 'All'])
                    self.availability_dict[emp] = ['All']

    def draw_lines(self):
        day = self.selected_day.get()
        hour_labels = [f"{i} AM" if i < 12 else (f"12 PM" if i == 12 else f"{i - 12} PM") for i in range(9, 24)]  # 9 AM to 11 PM
        available_employees = [emp for emp in self.employees if day in self.availability_dict.get(emp, []) or "All" in self.availability_dict.get(emp, [])]

        for i, emp in enumerate(available_employees):
            y = 50 + i * self.employee_height  
            # Employee name and horizontal line
            self.canvas.create_line(self.employee_pad, y, self.canvas_width - 30, y, fill="lightgrey", width=2)
            self.canvas.create_text(50, y, text=emp, anchor="w")
            # Draw dots for each hour
            for j in range(15):  # 15 hours from 9 AM to 11 PM
                hour_x = self.employee_pad + (self.canvas_width - 150) * (j / 14)
                self.canvas.create_oval(hour_x - 2, y - 2, hour_x + 2, y + 2, fill="black", outline="black")

        # Draw hour labels on the x-axis - 15hrs(9 AM to 11 PM)
        for j in range(15): 
            hour_x = self.employee_pad + (self.canvas_width - 150) * (j / 14) 
            self.canvas.create_text(hour_x, y + 35, text=hour_labels[j], anchor="s")
        # Draw vertical lines for every third hour
        for j in [0, 3, 6, 9, 12]:
            hour_x = self.employee_pad + (self.canvas_width - 150) * ((j) / 14) 
            self.canvas.create_line(hour_x, 50, hour_x, y + 15, fill="grey", dash=(3, 5), width=1)

    def draw_existing_schedule(self):
        # Draw lines for the existing hours for the selected day
        day = self.selected_day.get()
        if day in self.hours_dict:
            for emp, hours in self.hours_dict[day].items():
                for start, end in hours:
                    # Get the employee index to calculate Y-position
                    if emp in self.employees:
                        emp_index = self.employees.index(emp)
                        y = 50 + emp_index * self.employee_height  # Same logic as stop_drawing to get the Y position

                        # Calculate X-coordinates based on start and end hours
                        x_start = self.employee_pad + (start / 14) * (self.canvas_width - 150)  # Using your get_hour_from_x logic
                        x_end = self.employee_pad + (end / 14) * (self.canvas_width - 150)
                        
                        # Draw the line for this employee's hours
                        line = self.canvas.create_line(x_start, y, x_end, y, width=5, fill="blue")
                        
                        # Add the drawn line to the undo stack
                        self.undo_stack.append([line, emp, start, end])

    def start_drawing(self, event):
        # Start drawing line
        x1 = event.x
        y1 = event.y
        line = self.canvas.create_line(x1, y1, x1, y1, fill="blue", width=2)
        self.lines.append((line, x1, y1))  # Store the line's ID and start coordinates

    def drawing(self, event):
        line, x1, y1 = self.lines[-1]
        self.canvas.coords(line, x1, y1, event.x, event.y)

    def stop_drawing(self, event):
        # Stop drawing line and store the end coordinates
        day = self.selected_day.get()
        line, x1, y1 = self.lines[-1]
        self.canvas.coords(line, x1, y1, event.x, event.y)
        available_employees = [emp for emp in self.employees if day in self.availability_dict.get(emp, []) or "All" in self.availability_dict.get(emp, [])]

        # Determine which employee line was drawn on based on y-coordinate
        for i, emp in enumerate(available_employees):
            y = 50 + i * self.employee_height
            if y - 20 < event.y < y + 20:  # Check if the event is near the employee line
                start_hour = self.get_hour_from_x(x1)
                end_hour = self.get_hour_from_x(event.x)
                # print(start_hour, end_hour)
                if start_hour == end_hour:
                    break
                if start_hour is not None and end_hour is not None:
                    if start_hour > end_hour:
                        start_hour, end_hour = end_hour, start_hour
                    
                    # Check if the employee is available before saving
                    if emp in available_employees:
                        # Saving schedule for selected day, employee and hours
                        self.hours_dict[day][emp].append((start_hour, end_hour))
                        self.update_hours_label()
            
                break
        
        # Save the line for undo
        self.undo_stack.append([line, emp, start_hour, end_hour])
        self.lines.append((line, x1, y1))

    def get_hour_from_x(self, x):
        # Convert x-coordinate to hour index
        if x < self.employee_pad or x > (self.canvas_width - 30):
            return None  # Outside of range
        hour_index = round((x - self.employee_pad) / (self.canvas_width - 150) * 14)
        return hour_index
    
    def get_hour_from_index(self,hour_index):
        hour_name = f'{9+hour_index} AM' if hour_index < 3 else f'{9+hour_index} PM' if hour_index==3 else f'{hour_index-3} PM'
        return hour_name

    def update_hours_label(self):
        # Create a string to show saved hours for each employee
        hours_summary = ""
        # Access hours for the selected day
        day = self.selected_day.get()
        for emp, hours in self.hours_dict[day].items():
            if hours:  #Fetching hours for given employee
                day_total_hours = sum(end - start for start, end in hours)
                week_total_hours = 0
                for d in self.days_of_week:
                    if emp in self.hours_dict[d]:
                        week_total_hours += sum(end - start for start, end in self.hours_dict[d][emp])

                hours_summary += f"{emp} ({week_total_hours}): "  # Total week hours
                hours_summary += f"{', '.join([f'{self.get_hour_from_index(start)} - {self.get_hour_from_index(end)}' for start, end in hours])} ({day_total_hours})\n"  # Total day hours

        # self.hours_label.config(text=hours_summary if hours_summary else "No hours saved yet.")
        self.hours_text.delete(1.0, tk.END)  # Clear existing text
        self.hours_text.insert(tk.END, hours_summary if hours_summary else "No hours saved yet.")

    def update_weekday(self, selected_day):
        self.selected_day.set(selected_day)  # Update the selected day variable
        
        self.canvas.delete("all")
        self.undo_stack.clear()  # Clear the undo stack
        self.draw_lines()  # Rdedraw the lines and labels
        self.draw_existing_schedule() # Draw lines for existing schedule
        self.update_hours_label()  # Update the hours display

    def open_availability_window(self):
        self.avail_window = tk.Toplevel(self.root)
        self.avail_window.title("Employee Availability")
        days = ["All"] + [day[:3] for day in self.days_of_week] + ["# Days"] 

        # Create a grid of checkboxes for each employee and day
        self.avail_checkbuttons = {}
        for i, emp in enumerate(self.employees):
            tk.Label(self.avail_window, text=emp).grid(row=i+1, column=0, padx=10, pady=5)
            # Create checkbuttons for each day of the week plus 'All'
            self.avail_checkbuttons[emp] = {}
            for j, day in enumerate(days[:-1]): #
                var = tk.BooleanVar()
                # Pre-check the checkbuttons if the day is in the availability_dict for the employee
                if day in self.availability_dict.get(emp, []):
                    var.set(True)
                checkbutton = tk.Checkbutton(self.avail_window, variable=var)
                checkbutton.grid(row=i+1, column=j+1, padx=5, pady=5)
                self.avail_checkbuttons[emp][day] = var
            
            # Entry for max days at the end of the row
            max_days_entry = tk.Entry(self.avail_window)
            max_days_entry.grid(row=i+1, column=len(days), padx=5, pady=5)
            # Pre-enter existing data if available in availability_dict for the employee
            max_days = self.availability_dict[emp][-1] if len(self.availability_dict[emp]) > 0 else ''
            max_days = max_days if max_days.isdigit() else ''
            max_days_entry.insert(0, max_days)

        # Add headers for the days of the week
        for j, day in enumerate(days[:-1]):
            tk.Label(self.avail_window, text=day).grid(row=0, column=j+1, padx=10)
        tk.Label(self.avail_window, text="# Days").grid(row=0, column=len(days), padx=10)

        # Save button to store availability
        save_avail_button = tk.Button(self.avail_window, text="Save Availability", command=self.save_availability)
        save_avail_button.grid(row=len(self.employees) + 1, column=0, columnspan=len(days) + 2, pady=10)

    def save_availability(self):
        # Iterate through each employee and day, and store the selection
        for emp, days_vars in self.avail_checkbuttons.items():
            self.availability_dict[emp] = []
            for day, var in days_vars.items():
                if var.get():  # If the checkbutton is checked
                    self.availability_dict[emp].append(day)    
            max_days_entry = self.avail_window.grid_slaves(row=self.employees.index(emp) + 1, column=len(self.days_of_week) + 2)
            max_days = max_days_entry[0].get()
            max_days = max_days if max_days.isdigit() else ''
            self.availability_dict[emp].append(max_days)

        with open(self.availability_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for emp, days in self.availability_dict.items():
                writer.writerow([emp, ','.join(days[:-1]), days[-1]])

        # Close the availability window after saving
        self.avail_window.destroy()
        self.update_weekday(self.selected_day.get())

    def undo(self):
        if self.undo_stack:
            # Get the last line and remove it
            last_line, employee, start, end = self.undo_stack.pop()
            self.canvas.delete(last_line)  # Delete the last drawn line

            # Remove the associated entry from hours_dict for the selected day
            day = self.selected_day.get()
            if employee in self.hours_dict[day]:
                self.hours_dict[day][employee] = [entry for entry in self.hours_dict[day][employee] if entry != (start, end)]

            self.update_hours_label()  # Update the hours display

    def reset(self):
        # Clear the canvas
        self.canvas.delete("all")
        self.undo_stack.clear()  # Clear the undo stack
        self.hours_dict[self.selected_day.get()] = {emp: [] for emp in self.employees}  # Reset hours dict
        self.draw_lines()  # Redraw the lines and labels
        self.update_hours_label()  # Update the hours display

    def save_to_csv(self):
        # Open a dialog to ask where to save the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        
        if not file_path:
            return  # If no file is selected, exit the function

        # Write data to CSV
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write header (Employee, Mon, Tue, Wed, Thur, Fri, Sat, Sun)
            header = ["Employee"] + [day[:3].upper() for day in self.days_of_week]
            writer.writerow(header)
            
            # Write schedule for each employee
            for emp in self.employees:
                row = [emp]
                for day in self.days_of_week:
                    # Fetch saved hours for each day
                    if emp in self.hours_dict[day]:
                        hours = self.hours_dict[day][emp]
                        if hours:
                            # Format hours as 'Start-End' for each entry
                            hours_str = ', '.join([f' {self.get_hour_from_index(start).replace(" AM", "").replace(" PM", "")}-{self.get_hour_from_index(end).replace(" AM", "").replace(" PM", "")}' for start, end in hours])
                        else:
                            hours_str = "-"
                    else:
                        hours_str = "-"
                    row.append(hours_str)
                
                # Write the employee's row to the CSV
                writer.writerow(row)

if __name__ == "__main__":
    root = tk.Tk()
    # root = customtkinter.CTk()
    app = ScheduleApp(root)
    root.mainloop()
