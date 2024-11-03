import tkinter as tk
import math
import heapq
import time
import os

# Define the Cell class
class Cell:
    def __init__(self):
        self.parent_i = 0  # Parent cell's row index
        self.parent_j = 0  # Parent cell's column index
        self.f = float('inf')  # Total cost of the cell (g + h)
        self.g = float('inf')  # Cost from start to this cell
        self.h = 0  # Heuristic cost from this cell to destination

class MazeGame:
    def __init__(self, master):
        self.master = master
        self.grid_size = (0, 0)
        self.start = (0, 0)
        self.goal = (0, 0)
        self.obstacles = []
        self.canvas = None
        self.cost_frame = None
        self.scrollbar = None

        self.setup_gui()

        # Attempt to read inputs from a file
        self.read_inputs_from_file('maze_input.txt')

    def read_inputs_from_file(self, filename):
        if not os.path.isfile(filename):
            self.display_message(f"File {filename} not found.")
            return False

        with open(filename, 'r') as file:
            try:
                n, m = map(int, file.readline().strip().split())
                self.start = tuple(map(int, file.readline().strip().split()))
                self.goal = tuple(map(int, file.readline().strip().split()))
                self.obstacles = []

                for line in file:
                    x, y = map(int, line.strip().split())
                    self.obstacles.append((y, x))  # Adjusting for 0-indexing

                self.grid_size = (n, m)

                # Create the maze and initialize the canvas
                self.cell_size = 600 // max(n, m)
                self.canvas = tk.Canvas(self.master, width=600, height=600)
                self.canvas.pack(side=tk.LEFT)  # Pack canvas to the left
                self.draw_grid()
                self.hide_input_fields()
                self.create_cost_canvas()
                self.draw_obstacles()
                self.submit_button.config(state=tk.NORMAL)
                self.restart_button.config(state=tk.NORMAL)

                return True
            except Exception as e:
                return False
            
    
    def draw_obstacles(self):
        for obstacle in self.obstacles:
            y, x = obstacle
            self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size,
                                      (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                      outline="black", fill="black")
    def setup_gui(self):
        self.master.title("Maze Game")
        self.frame = tk.Frame(self.master)
        self.frame.pack()

        tk.Label(self.frame, text="Grid Size (n m):").grid(row=0, column=0)
        self.n_entry = tk.Entry(self.frame)
        self.m_entry = tk.Entry(self.frame)
        self.n_entry.grid(row=0, column=1)
        self.m_entry.grid(row=0, column=2)

        tk.Label(self.frame, text="Start (x0 y0):").grid(row=1, column=0)
        self.start_x_entry = tk.Entry(self.frame)
        self.start_y_entry = tk.Entry(self.frame)
        self.start_x_entry.grid(row=1, column=1)
        self.start_y_entry.grid(row=1, column=2)

        tk.Label(self.frame, text="Goal (x1 y1):").grid(row=2, column=0)
        self.goal_x_entry = tk.Entry(self.frame)
        self.goal_y_entry = tk.Entry(self.frame)
        self.goal_x_entry.grid(row=2, column=1)
        self.goal_y_entry.grid(row=2, column=2)

        self.create_button = tk.Button(self.frame, text="Create Maze", command=self.create_maze)
        self.create_button.grid(row=4, column=0, columnspan=4)

        self.submit_button = tk.Button(self.master, text="Find Path", command=self.find_path)
        self.submit_button.pack()
        self.submit_button.config(state=tk.DISABLED)  # Disable until maze is created

        self.restart_button = tk.Button(self.master, text="Restart", command=self.restart_game)
        self.restart_button.pack()
        self.restart_button.config(state=tk.DISABLED)  # Disable until maze is created

        # Text area for displaying messages
        self.message_area = tk.Text(self.master, height=5, width=70, state=tk.DISABLED)
        self.message_area.pack(pady=10)

    def display_message(self, message):
        self.message_area.config(state=tk.NORMAL)  # Enable the text area
        self.message_area.insert(tk.END, message + "\n")  # Insert message
        self.message_area.config(state=tk.DISABLED)  # Disable it again

    def create_maze(self):
        n = int(self.n_entry.get())
        m = int(self.m_entry.get())
        self.start = (int(self.start_x_entry.get()), int(self.start_y_entry.get()))
        self.goal = (int(self.goal_x_entry.get()) , int(self.goal_y_entry.get()))

        self.grid_size = (n, m)
        self.obstacles = []
    
        self.cell_size = 600 // max(n, m)
        self.canvas = tk.Canvas(self.master, width=600, height=600)
        self.canvas.pack(side=tk.LEFT)  # Pack canvas to the left
        self.canvas.bind("<Button-1>", self.set_obstacle)
        
        self.draw_grid()
        self.hide_input_fields()

        # Create a canvas for displaying cost values
        self.create_cost_canvas()

        # Enable the Find Path and Restart buttons after creating the maze
        self.submit_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.NORMAL)

    def hide_input_fields(self):
        for widget in self.frame.winfo_children():
            widget.grid_forget()  # Remove all input widgets from the grid
        self.create_button.grid_forget()  # Hide the Create Maze button

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                x0, y0 = j * self.cell_size, i * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="white")
            
            # Draw row and column numbers
                self.canvas.create_text(x0 + self.cell_size // 2, y0 + self.cell_size // 2, 
                                    text=f"({i},{j})", fill="black", font=("Arial", 8))

        self.show_start_goal()


    def show_start_goal(self):
        start_x, start_y = self.start[1] * self.cell_size, self.start[0] * self.cell_size
        goal_x, goal_y = self.goal[1] * self.cell_size, self.goal[0] * self.cell_size
        self.canvas.create_oval(start_x + 10, start_y + 10, start_x + self.cell_size - 10, start_y + self.cell_size - 10, fill="blue")
        self.canvas.create_oval(goal_x + 10, goal_y + 10, goal_x + self.cell_size - 10, goal_y + self.cell_size - 10, fill="red")

    def create_cost_canvas(self):
        # Create a frame for the canvas and scrollbar
        self.cost_frame = tk.Frame(self.master)
        self.cost_frame.pack(side=tk.LEFT)  # Pack to the left of the main canvas

        # Create a canvas
        self.cost_canvas = tk.Canvas(self.cost_frame, width=800, height=800)  # Adjust width and height as needed
        self.cost_canvas.pack(side=tk.RIGHT)

        # Create a scrollbar
        self.yscrollbar = tk.Scrollbar(self.cost_frame, orient="vertical", command=self.cost_canvas.yview)
        self.yscrollbar.pack(side=tk.LEFT, fill='y')

        # Configure canvas to use scrollbar
        self.cost_canvas.configure(yscrollcommand=self.yscrollbar.set)
        
        # Create a scrollbar
        self.xscrollbar = tk.Scrollbar(self.cost_frame, orient="horizontal", command=self.cost_canvas.xview)
        self.xscrollbar.pack(side=tk.TOP, fill='x')

        # Configure canvas to use scrollbar
        self.cost_canvas.configure(xscrollcommand=self.xscrollbar.set)

        # Create an additional frame inside the canvas for the cost grid
        self.cost_grid_frame = tk.Frame(self.cost_canvas)
        self.cost_canvas.create_window((0, 0), window=self.cost_grid_frame, anchor='nw')

        # Update scroll region
        self.cost_grid_frame.bind("<Configure>", lambda e: self.cost_canvas.configure(scrollregion=self.cost_canvas.bbox("all")))

    def draw_cost_grid(self, cell_details):
        for widget in self.cost_grid_frame.winfo_children():
            widget.destroy()  # Clear previous content

        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                g_value = cell_details[i][j].g
                h_manhattan = abs(i - self.goal[0]) + abs(j - self.goal[1])
                h_diagonal = max(abs(i - self.goal[0]), abs(j - self.goal[1]))
                f_manhattan = g_value + h_manhattan
                f_diagonal = g_value + h_diagonal

                # Create a frame for each cell
                cell_frame = tk.Frame(self.cost_grid_frame, width=200, height=100, relief='solid', borderwidth=1)
                cell_frame.grid(row=i, column=j, padx=2, pady=2)

                label = tk.Label(cell_frame, text=f"g(n): {g_value:.1f}\n[man] h(n): {h_manhattan:.1f}\n[man] f(n): {f_manhattan:.1f}\n[dia] h(n): {h_diagonal:.1f}\n[dia] f(n): {f_diagonal:.1f}", anchor='center')
                label.pack(expand=True)

    def set_obstacle(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        if (y, x) not in self.obstacles and (y, x) != self.start and (y, x) != self.goal:
            self.obstacles.append((y, x))
            self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size,
                                          (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                          outline="black", fill="black")

    def a_star_search(self, grid, src, dest):
        if not self.is_valid(src[0], src[1]) or not self.is_valid(dest[0], dest[1]):
            self.display_message("Source or destination is invalid")
            return

        if not self.is_unblocked(grid, src[0], src[1]) or not self.is_unblocked(grid, dest[0], dest[1]):
            self.display_message("Source or the destination is blocked")
            return

        if self.is_destination(src[0], src[1], dest):
            self.display_message("We are already at the destination")
            return

        closed_list = [[False for _ in range(self.grid_size[1])] for _ in range(self.grid_size[0])]
        cell_details = [[Cell() for _ in range(self.grid_size[1])] for _ in range(self.grid_size[0])]

        i, j = src
        cell_details[i][j].f = 0
        cell_details[i][j].g = 0
        cell_details[i][j].h = 0
        cell_details[i][j].parent_i = i
        cell_details[i][j].parent_j = j

        open_list = []
        heapq.heappush(open_list, (0.0, i, j))

        found_dest = False

        while len(open_list) > 0:
            p = heapq.heappop(open_list)

            i = p[1]
            j = p[2]
            closed_list[i][j] = True

            directions = [
    (0, 1), (0, -1), (1, 0), (-1, 0),  # Vertical and horizontal
    (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonal movements
]

            for dir in directions:
                new_i = i + dir[0]
                new_j = j + dir[1]

                if self.is_valid(new_i, new_j) and self.is_unblocked(grid, new_i, new_j) and not closed_list[new_i][new_j]:
                    if self.is_destination(new_i, new_j, dest):
                        cell_details[new_i][new_j].parent_i = i
                        cell_details[new_i][new_j].parent_j = j
                        found_dest = True
                        self.draw_cost_grid(cell_details)  # Draw cost grid before returning
                        return self.trace_path(cell_details, dest)

                    g_new = math.sqrt((new_i - dest[0]) ** 2 + (new_j - dest[1]) ** 2)
                    h_manhattan = abs(new_i - dest[0]) + abs(new_j - dest[1])
                    h_diagonal = max(abs(new_i - dest[0]), abs(new_j - dest[1]))

                    # Choosing the minimum h value
                    h_new = min(h_manhattan, h_diagonal)
                    
                    f_new = g_new + h_new

                    if cell_details[new_i][new_j].f == float('inf') or cell_details[new_i][new_j].f > f_new:
                        heapq.heappush(open_list, (f_new, new_i, new_j))
                        cell_details[new_i][new_j].f = f_new
                        cell_details[new_i][new_j].g = g_new
                        cell_details[new_i][new_j].h = h_new
                        cell_details[new_i][new_j].parent_i = i
                        cell_details[new_i][new_j].parent_j = j

        if not found_dest:
            self.display_message("Failed to find the destination cell")
            self.draw_cost_grid(cell_details)  # Draw cost grid if no path found

    def is_valid(self, row, col):
        return (0 <= row < self.grid_size[0]) and (0 <= col < self.grid_size[1])

    def is_unblocked(self, grid, row, col):
        return (row, col) not in self.obstacles

    def is_destination(self, row, col, dest):
        return row == dest[0] and col == dest[1]

    def trace_path(self, cell_details, dest):
        path = []
        total_cost = 0  # Initialize total cost to zero
        row, col = dest

        while not (cell_details[row][col].parent_i == row and cell_details[row][col].parent_j == col):
            path.append((row, col))
            total_cost += cell_details[row][col].h  # Add the g cost of the current cell
            temp_row = cell_details[row][col].parent_i
            temp_col = cell_details[row][col].parent_j
            row, col = temp_row, temp_col

    # Add the starting cell's g cost
        total_cost += cell_details[row][col].g
        path.append((row, col))  # Include the starting cell
        path.reverse()

    # Optionally display the total cost in the GUI
        self.display_message(f"Path: {path}\nTotal Path Cost: {total_cost:.1f}")

        self.animate_path(path)


    def animate_path(self, path):
        for step in path:
            x, y = step[1] * self.cell_size, step[0] * self.cell_size
            
            # Draw full-width path line in dark yellow
            self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill="darkorange", outline="")

            # Draw stick man
            self.draw_stick_man(x, y)
            self.master.update()
            time.sleep(0.5)

    def draw_stick_man(self, x, y):
        head_radius = self.cell_size // 8  # Adjusted for visibility
        head_x = x + self.cell_size // 2
        head_y = y + self.cell_size // 2 - head_radius

    # Draw head
        self.canvas.create_oval(head_x - head_radius, head_y - head_radius,
                             head_x + head_radius, head_y + head_radius, fill="black")
    
    # Draw body
        body_length = head_radius * 2
        self.canvas.create_line(head_x, head_y, head_x, head_y + body_length, fill="black")

    # Draw arms
        arm_length = head_radius * 1.5
        self.canvas.create_line(head_x, head_y + head_radius, head_x - arm_length, head_y + head_radius, fill="black")
        self.canvas.create_line(head_x, head_y + head_radius, head_x + arm_length, head_y + head_radius, fill="black")

        # Draw legs
        leg_length = body_length * 1.5
        self.canvas.create_line(head_x, head_y + body_length, head_x - head_radius, head_y + body_length + leg_length,  fill="black")
        self.canvas.create_line(head_x, head_y + body_length, head_x + head_radius, head_y + body_length + leg_length,  fill="black")


    def find_path(self):
        start_time= time.time()
        grid = [[1 if (i, j) not in self.obstacles else 0 for j in range(self.grid_size[1])] for i in range(self.grid_size[0])]
        self.a_star_search(grid, self.start, self.goal)
        end_time=time.time()
        self.display_message(f'Time Taken By StickMan : {abs(start_time-end_time)}')

    def restart_game(self):
        self.canvas.destroy()
        self.cost_frame.destroy()
        self.obstacles = []
        self.setup_gui()

if __name__ == "__main__":
    root = tk.Tk()
    game = MazeGame(root)
    root.mainloop()
