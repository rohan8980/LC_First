import tkinter as tk
# from tkinter import messagebox

class ScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Schedule")

        # Employee names
        self.employees = ["Emmanuel", "Nick", "Tej", "Javed", "Santosh", "Janvi", "Yash", "Divya", 
                          "Rohan", "Gabby", "Emma", "Val", "Ayoub", "Abraham", "Francessca", "Annie", 
                          "Rahi", "Sonika", "Sonakshi" ]
        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


        # Create a canvas for drawing
        self.employee_height = 25
        self.employee_pad = 120
        self.canvas_width = 800
        self.canvas_height = self.employee_height * len(self.employees) + 100
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(padx=10, pady=10)

        # Create a dictionary to store drawn hours
        self.hours_dict = {day: {emp: [] for emp in self.employees} for day in self.days_of_week}


        # Create a frame to hold the day selector, undo, and reset buttons side by side
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
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
       

        # Draw horizontal lines for employees and hour labels
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

    def update_weekday(self, selected_day):
        self.selected_day.set(selected_day)  # Update the selected day variable
        
        self.canvas.delete("all")
        self.undo_stack.clear()  # Clear the undo stack
        self.draw_lines()  # Rdedraw the lines and labels
        self.draw_existing_schedule() # Draw lines for existing schedule
        self.update_hours_label()  # Update the hours display

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

    def draw_lines(self):
        hour_labels = [f"{i} AM" if i < 12 else (f"12 PM" if i == 12 else f"{i - 12} PM") for i in range(9, 24)]  # 9 AM to 11 PM

        # Draw lines for each employee
        for i, emp in enumerate(self.employees):
            y = 50 + i * self.employee_height  # Spacing between lines
            # Draw horizontal line for the employee
            self.canvas.create_line(self.employee_pad, y, self.canvas_width - 30, y, fill="lightgrey", width=2)
            # Draw the employee name
            self.canvas.create_text(50, y, text=emp, anchor="w")

            # Draw dots for each hour
            for j in range(15):  # 15 hours from 9 AM to 11 PM
                hour_x = self.employee_pad + (self.canvas_width - 150) * (j / 14)  # Space them evenly across the width
                self.canvas.create_oval(hour_x - 2, y - 2, hour_x + 2, y + 2, fill="black", outline="black")  # Dots

        # Draw hour labels on the x-axis (outside the employee loop)
        for j in range(15):  # 15 hours from 9 AM to 11 PM
            hour_x = self.employee_pad + (self.canvas_width - 150) * (j / 14)  # Space them evenly across the width
            self.canvas.create_text(hour_x, self.canvas_height - 30, text=hour_labels[j], anchor="s")

    def get_hour_from_x(self, x):
        # Convert x-coordinate to hour index
        if x < self.employee_pad or x > (self.canvas_width - 30):
            return None  # Outside of range
        hour_index = round((x - self.employee_pad) / (self.canvas_width - 150) * 14)
        return hour_index
    
    def get_hour_from_index(self,hour_index):
        hour_name = f'{9+hour_index} AM' if hour_index < 3 else f'{9+hour_index} PM' if hour_index==3 else f'{hour_index-3} PM'
        return hour_name

    def start_drawing(self, event):
        # Start drawing line
        x1 = event.x
        y1 = event.y
        line = self.canvas.create_line(x1, y1, x1, y1, fill="blue", width=2)
        self.lines.append((line, x1, y1))  # Store the line's ID and start coordinates

    def drawing(self, event):
        # Update line while drawing
        line, x1, y1 = self.lines[-1]
        self.canvas.coords(line, x1, y1, event.x, event.y)

    def stop_drawing(self, event):
        # Stop drawing line and store the end coordinates
        line, x1, y1 = self.lines[-1]
        self.canvas.coords(line, x1, y1, event.x, event.y)

        # Determine which employee line was drawn on based on y-coordinate
        for i, emp in enumerate(self.employees):
            y = 50 + i * self.employee_height
            if y - 20 < event.y < y + 20:  # Check if the event is near the employee line
                start_hour = self.get_hour_from_x(x1)
                end_hour = self.get_hour_from_x(event.x)
                print(start_hour, end_hour)
                if start_hour is not None and end_hour is not None:
                    if start_hour > end_hour:
                        start_hour, end_hour = end_hour, start_hour
                    
                    #Saving schedule for selected day, employee and hours
                    day = self.selected_day.get()
                    self.hours_dict[day][emp].append((start_hour, end_hour))
                    self.update_hours_label()
                break
        
        # Save the line for undo
        self.undo_stack.append([line, emp, start_hour, end_hour])
        self.lines.append((line, x1, y1))

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ScheduleApp(root)
    root.mainloop()
