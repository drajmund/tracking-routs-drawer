import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import math
import numpy as np
try:
    import umap
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from sklearn.manifold import TSNE, MDS, Isomap
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN, OPTICS
    ALGORITHMS_AVAILABLE = True
except ImportError:
    ALGORITHMS_AVAILABLE = False

class TrackingRouteDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("Tracking Routes Drawer")
        self.root.geometry("1200x600")
        
        # Create main frame to hold canvas and route list
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas setup
        self.canvas = tk.Canvas(main_frame, bg='white', width=780, height=580)
        self.canvas.pack(side=tk.LEFT, padx=(0, 10))
        
        # Route list setup
        list_frame = tk.Frame(main_frame)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="Route Information", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        
        # Create listbox with scrollbar
        list_container = tk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.route_listbox = tk.Listbox(list_container, font=("Courier", 9))
        scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.route_listbox.yview)
        self.route_listbox.config(yscrollcommand=scrollbar.set)
        
        self.route_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Grid settings
        self.grid_size = 20
        self.origin_x = 0  # Top-left origin
        self.origin_y = 0  # Top-left origin
        
        # Tracking routes data
        self.routes = []  # List of routes, each route is a list of points
        self.current_route = []  # Current route being drawn
        self.point_radius = 4
        self.click_tolerance = 8  # Tolerance for clicking near points/lines
        
        # Dragging state
        self.dragging = False
        self.drag_route_idx = None
        self.drag_point_idx = None
        self.drag_start_x = None
        self.drag_start_y = None
        
        # Colors
        self.grid_color = "#E0E0E0"
        self.axis_color = "#808080"
        self.point_color = "#FF0000"
        self.line_color = "#0000FF"
        
        # Draw initial grid and axes
        self.draw_grid()
        self.draw_axes()
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_left_click)  # Left click
        self.canvas.bind("<Button-3>", self.on_right_click)  # Right click
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)  # Left release
        self.canvas.bind("<B1-Motion>", self.on_drag)  # Drag with left button
        
        # Status label
        self.status_label = tk.Label(root, text="Left-click to add points or drag existing points | Right-click on point to remove | Right-click on line to insert point")
        self.status_label.pack()
        
        # Control buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)
        
        tk.Button(button_frame, text="New Route", command=self.start_new_route).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Undo Last Point", command=self.undo_last_point).pack(side=tk.LEFT, padx=5)
        
        # Dimensionality Reduction button
        if ALGORITHMS_AVAILABLE:
            tk.Button(button_frame, text="Dimensionality Analysis", command=self.open_analysis_dialog).pack(side=tk.LEFT, padx=5)
        else:
            analysis_btn = tk.Button(button_frame, text="Analysis (Not Available)", state=tk.DISABLED)
            analysis_btn.pack(side=tk.LEFT, padx=5)
        
        # Coordinate display
        self.coord_label = tk.Label(root, text="Coordinates: (0, 0)")
        self.coord_label.pack()
        
        # Initialize route list display
        self.update_route_list()
        
    def draw_grid(self):
        """Draw grid lines on the canvas"""
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        
        # Vertical grid lines
        for x in range(0, canvas_width, self.grid_size):
            self.canvas.create_line(x, 0, x, canvas_height, fill=self.grid_color, tags="grid")
        
        # Horizontal grid lines
        for y in range(0, canvas_height, self.grid_size):
            self.canvas.create_line(0, y, canvas_width, y, fill=self.grid_color, tags="grid")
    
    def draw_axes(self):
        """Draw coordinate axes"""
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        
        # X-axis (horizontal line at top)
        self.canvas.create_line(0, self.origin_y, canvas_width, self.origin_y, 
                               fill=self.axis_color, width=2, tags="axes")
        
        # Y-axis (vertical line at left)
        self.canvas.create_line(self.origin_x, 0, self.origin_x, canvas_height, 
                               fill=self.axis_color, width=2, tags="axes")
        
        # Add coordinate labels
        self.draw_coordinate_labels()
    
    def draw_coordinate_labels(self):
        """Draw coordinate labels on axes"""
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        
        # X-axis labels
        for x in range(0, canvas_width, self.grid_size * 5):  # Every 5th grid line
            coord_x = self.canvas_to_coord_x(x)
            if coord_x != 0:  # Don't draw 0 twice
                self.canvas.create_text(x, 15, text=str(coord_x), 
                                      font=("Arial", 8), tags="labels")
        
        # Y-axis labels
        for y in range(0, canvas_height, self.grid_size * 5):  # Every 5th grid line
            coord_y = self.canvas_to_coord_y(y)
            if coord_y != 0:  # Don't draw 0 twice
                self.canvas.create_text(15, y, text=str(coord_y), 
                                      font=("Arial", 8), tags="labels")
        
        # Origin label
        self.canvas.create_text(10, 10, text="(0,0)", 
                               font=("Arial", 8), tags="labels")
    
    def canvas_to_coord_x(self, canvas_x):
        """Convert canvas x coordinate to graph coordinate"""
        return round((canvas_x - self.origin_x) / self.grid_size)
    
    def canvas_to_coord_y(self, canvas_y):
        """Convert canvas y coordinate to graph coordinate (Y increases downward)"""
        return round((canvas_y - self.origin_y) / self.grid_size)
    
    def coord_to_canvas_x(self, coord_x):
        """Convert graph x coordinate to canvas coordinate"""
        return self.origin_x + coord_x * self.grid_size
    
    def coord_to_canvas_y(self, coord_y):
        """Convert graph y coordinate to canvas coordinate (Y increases downward)"""
        return self.origin_y + coord_y * self.grid_size
    
    def on_left_click(self, event):
        """Handle left mouse click to add points or start dragging"""
        # Check if clicking on an existing point to start dragging
        clicked_point_info = self.find_point_at_position(event.x, event.y)
        if clicked_point_info:
            # Start dragging
            self.dragging = True
            self.drag_route_idx, self.drag_point_idx = clicked_point_info
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.status_label.config(text="Dragging point... Release to place.")
            return
        
        # If not clicking on a point, add new point
        # Get coordinates
        coord_x = self.canvas_to_coord_x(event.x)
        coord_y = self.canvas_to_coord_y(event.y)
        
        # Convert back to exact canvas position (snap to grid)
        canvas_x = self.coord_to_canvas_x(coord_x)
        canvas_y = self.coord_to_canvas_y(coord_y)
        
        # Add point to current route
        point = (coord_x, coord_y)
        self.current_route.append(point)
        
        # Draw the point
        self.draw_point(canvas_x, canvas_y, coord_x, coord_y)
        
        # Draw line to previous point if this isn't the first point
        if len(self.current_route) > 1:
            prev_point = self.current_route[-2]
            prev_canvas_x = self.coord_to_canvas_x(prev_point[0])
            prev_canvas_y = self.coord_to_canvas_y(prev_point[1])
            self.draw_line(prev_canvas_x, prev_canvas_y, canvas_x, canvas_y)
        
        # Update status
        if len(self.current_route) == 1:
            self.status_label.config(text=f"Started new route at ({coord_x}, {coord_y}). Left-click to add more points.")
        else:
            self.status_label.config(text=f"Added point ({coord_x}, {coord_y}). Route has {len(self.current_route)} points.")
        
        # Update route list
        self.update_route_list()
    
    def draw_point(self, canvas_x, canvas_y, coord_x, coord_y):
        """Draw a point on the canvas"""
        # Draw circle
        self.canvas.create_oval(
            canvas_x - self.point_radius, canvas_y - self.point_radius,
            canvas_x + self.point_radius, canvas_y + self.point_radius,
            fill=self.point_color, outline="black", width=1, tags="points"
        )
        
        # Add coordinate label
        self.canvas.create_text(
            canvas_x, canvas_y - 15, 
            text=f"({coord_x},{coord_y})", 
            font=("Arial", 8), 
            fill="black", 
            tags="point_labels"
        )
    
    def draw_line(self, x1, y1, x2, y2):
        """Draw a line between two points"""
        self.canvas.create_line(x1, y1, x2, y2, fill=self.line_color, width=2, tags="lines")
    
    def start_new_route(self):
        """Start a new tracking route"""
        if self.current_route:
            # Save current route if it has points
            self.routes.append(self.current_route.copy())
        
        # Start new route
        self.current_route = []
        self.status_label.config(text="Ready to start new route. Left-click to add first point.")
        
        # Update route list
        self.update_route_list()
    
    def clear_all(self):
        """Clear all routes and points"""
        self.routes = []
        self.current_route = []
        
        # Clear canvas drawings (keep grid and axes)
        self.canvas.delete("points")
        self.canvas.delete("lines")
        self.canvas.delete("point_labels")
        
        self.status_label.config(text="All routes cleared. Left-click to start a new tracking route.")
        
        # Update route list
        self.update_route_list()
    
    def undo_last_point(self):
        """Remove the last point from current route"""
        if self.current_route:
            # Remove last point
            removed_point = self.current_route.pop()
            
            # Redraw everything (simple approach)
            self.redraw_all_routes()
            
            if self.current_route:
                self.status_label.config(text=f"Removed point {removed_point}. Route has {len(self.current_route)} points.")
            else:
                self.status_label.config(text="Removed last point. Route is now empty.")
            
            # Update route list
            self.update_route_list()
        else:
            messagebox.showinfo("Info", "No points to remove in current route.")
    
    def redraw_all_routes(self):
        """Redraw all routes and points"""
        # Clear existing drawings
        self.canvas.delete("points")
        self.canvas.delete("lines")
        self.canvas.delete("point_labels")
        
        # Redraw completed routes
        for route in self.routes:
            self.draw_route(route)
        
        # Redraw current route
        if self.current_route:
            self.draw_route(self.current_route)
    
    def draw_route(self, route):
        """Draw a complete route (points and connecting lines)"""
        for i, point in enumerate(route):
            coord_x, coord_y = point
            canvas_x = self.coord_to_canvas_x(coord_x)
            canvas_y = self.coord_to_canvas_y(coord_y)
            
            # Draw point
            self.draw_point(canvas_x, canvas_y, coord_x, coord_y)
            
            # Draw line to previous point
            if i > 0:
                prev_point = route[i-1]
                prev_canvas_x = self.coord_to_canvas_x(prev_point[0])
                prev_canvas_y = self.coord_to_canvas_y(prev_point[1])
                self.draw_line(prev_canvas_x, prev_canvas_y, canvas_x, canvas_y)
    
    def on_right_click(self, event):
        """Handle right mouse click for point removal or line insertion"""
        # Check if clicking on an existing point
        clicked_point_info = self.find_point_at_position(event.x, event.y)
        if clicked_point_info:
            route_idx, point_idx = clicked_point_info
            self.remove_point(route_idx, point_idx)
            return
        
        # Check if clicking on a line
        line_info = self.find_line_at_position(event.x, event.y)
        if line_info:
            route_idx, point1_idx, point2_idx = line_info
            # Insert new point between point1 and point2
            coord_x = self.canvas_to_coord_x(event.x)
            coord_y = self.canvas_to_coord_y(event.y)
            self.insert_point_in_route(route_idx, point1_idx + 1, (coord_x, coord_y))
    
    def find_point_at_position(self, canvas_x, canvas_y):
        """Find if there's a point at the given canvas position"""
        # Check current route
        for i, point in enumerate(self.current_route):
            point_canvas_x = self.coord_to_canvas_x(point[0])
            point_canvas_y = self.coord_to_canvas_y(point[1])
            distance = math.sqrt((canvas_x - point_canvas_x)**2 + (canvas_y - point_canvas_y)**2)
            if distance <= self.click_tolerance:
                return (-1, i)  # -1 indicates current route
        
        # Check completed routes
        for route_idx, route in enumerate(self.routes):
            for point_idx, point in enumerate(route):
                point_canvas_x = self.coord_to_canvas_x(point[0])
                point_canvas_y = self.coord_to_canvas_y(point[1])
                distance = math.sqrt((canvas_x - point_canvas_x)**2 + (canvas_y - point_canvas_y)**2)
                if distance <= self.click_tolerance:
                    return (route_idx, point_idx)
        
        return None
    
    def find_line_at_position(self, canvas_x, canvas_y):
        """Find if there's a line at the given canvas position"""
        # Check current route lines
        for i in range(len(self.current_route) - 1):
            point1 = self.current_route[i]
            point2 = self.current_route[i + 1]
            if self.is_point_on_line(canvas_x, canvas_y, point1, point2):
                return (-1, i, i + 1)  # -1 indicates current route
        
        # Check completed routes lines
        for route_idx, route in enumerate(self.routes):
            for i in range(len(route) - 1):
                point1 = route[i]
                point2 = route[i + 1]
                if self.is_point_on_line(canvas_x, canvas_y, point1, point2):
                    return (route_idx, i, i + 1)
        
        return None
    
    def is_point_on_line(self, canvas_x, canvas_y, point1, point2):
        """Check if a canvas position is close to a line between two points"""
        x1 = self.coord_to_canvas_x(point1[0])
        y1 = self.coord_to_canvas_y(point1[1])
        x2 = self.coord_to_canvas_x(point2[0])
        y2 = self.coord_to_canvas_y(point2[1])
        
        # Calculate distance from point to line segment
        line_length_sq = (x2 - x1)**2 + (y2 - y1)**2
        if line_length_sq == 0:
            return False
        
        # Calculate the parameter t for the closest point on the line
        t = max(0, min(1, ((canvas_x - x1) * (x2 - x1) + (canvas_y - y1) * (y2 - y1)) / line_length_sq))
        
        # Find the closest point on the line segment
        closest_x = x1 + t * (x2 - x1)
        closest_y = y1 + t * (y2 - y1)
        
        # Calculate distance from click point to closest point on line
        distance = math.sqrt((canvas_x - closest_x)**2 + (canvas_y - closest_y)**2)
        
        return distance <= self.click_tolerance
    
    def remove_point(self, route_idx, point_idx):
        """Remove a point from a route"""
        if route_idx == -1:  # Current route
            if 0 <= point_idx < len(self.current_route):
                removed_point = self.current_route.pop(point_idx)
                self.redraw_all_routes()
                self.status_label.config(text=f"Removed point {removed_point} from current route.")
                self.update_route_list()
        else:  # Completed route
            if 0 <= route_idx < len(self.routes) and 0 <= point_idx < len(self.routes[route_idx]):
                removed_point = self.routes[route_idx].pop(point_idx)
                # Remove empty routes
                if not self.routes[route_idx]:
                    self.routes.pop(route_idx)
                self.redraw_all_routes()
                self.status_label.config(text=f"Removed point {removed_point} from route {route_idx + 1}.")
                self.update_route_list()
    
    def insert_point_in_route(self, route_idx, insert_idx, new_point):
        """Insert a new point in a route at the specified index"""
        if route_idx == -1:  # Current route
            self.current_route.insert(insert_idx, new_point)
            self.redraw_all_routes()
            self.status_label.config(text=f"Inserted point {new_point} in current route.")
            self.update_route_list()
        else:  # Completed route
            if 0 <= route_idx < len(self.routes):
                self.routes[route_idx].insert(insert_idx, new_point)
                self.redraw_all_routes()
                self.status_label.config(text=f"Inserted point {new_point} in route {route_idx + 1}.")
                self.update_route_list()
    
    def on_left_release(self, event):
        """Handle left mouse button release to finish dragging"""
        if self.dragging:
            # Update the point position
            coord_x = self.canvas_to_coord_x(event.x)
            coord_y = self.canvas_to_coord_y(event.y)
            
            if self.drag_route_idx == -1:  # Current route
                self.current_route[self.drag_point_idx] = (coord_x, coord_y)
            else:  # Completed route
                self.routes[self.drag_route_idx][self.drag_point_idx] = (coord_x, coord_y)
            
            # Redraw everything
            self.redraw_all_routes()
            
            # Reset dragging state
            self.dragging = False
            self.drag_route_idx = None
            self.drag_point_idx = None
            self.status_label.config(text=f"Moved point to ({coord_x}, {coord_y}).")
            
            # Update route list
            self.update_route_list()
    
    def on_drag(self, event):
        """Handle dragging motion"""
        if self.dragging:
            # Visual feedback during drag - could show preview line here
            coord_x = self.canvas_to_coord_x(event.x)
            coord_y = self.canvas_to_coord_y(event.y)
            self.coord_label.config(text=f"Dragging to: ({coord_x}, {coord_y})")
    
    def calculate_route_length(self, route):
        """Calculate the total length of a route"""
        if len(route) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(route) - 1):
            x1, y1 = route[i]
            x2, y2 = route[i + 1]
            # Calculate Euclidean distance
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            total_length += distance
        
        return total_length
    
    def calculate_euclidean_distance(self, route):
        """Calculate straight-line distance from start to end"""
        if len(route) < 2:
            return 0.0
        
        start_x, start_y = route[0]
        end_x, end_y = route[-1]
        return math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
    
    def get_point_at_distance(self, route, target_distance):
        """Get coordinates at a specific distance along the route"""
        if len(route) < 2:
            return route[0] if route else (0, 0)
        
        if target_distance <= 0:
            return route[0]
        
        current_distance = 0.0
        
        for i in range(len(route) - 1):
            x1, y1 = route[i]
            x2, y2 = route[i + 1]
            segment_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            if current_distance + segment_length >= target_distance:
                # Target point is in this segment
                remaining_distance = target_distance - current_distance
                if segment_length == 0:
                    return (x1, y1)
                
                # Interpolate along the segment
                ratio = remaining_distance / segment_length
                x = x1 + ratio * (x2 - x1)
                y = y1 + ratio * (y2 - y1)
                return (x, y)
            
            current_distance += segment_length
        
        # If target distance exceeds route length, return end point
        return route[-1]
    
    def get_middle_point(self, route):
        """Get coordinates at the middle of the route (by distance)"""
        total_length = self.calculate_route_length(route)
        return self.get_point_at_distance(route, total_length / 2)
    
    def get_third_points(self, route):
        """Get coordinates at 1/3 and 2/3 points along the route"""
        total_length = self.calculate_route_length(route)
        point_1_3 = self.get_point_at_distance(route, total_length / 3)
        point_2_3 = self.get_point_at_distance(route, 2 * total_length / 3)
        return point_1_3, point_2_3
    
    def update_route_list(self):
        """Update the route information list"""
        self.route_listbox.delete(0, tk.END)
        
        # Add completed routes
        for i, route in enumerate(self.routes):
            if len(route) >= 2:
                start = route[0]
                end = route[-1]
                length = self.calculate_route_length(route)
                info = f"Route {i+1}: ({start[0]},{start[1]}) → ({end[0]},{end[1]}) | Len: {length:.2f}"
                self.route_listbox.insert(tk.END, info)
            elif len(route) == 1:
                start = route[0]
                info = f"Route {i+1}: ({start[0]},{start[1]}) (single point)"
                self.route_listbox.insert(tk.END, info)
        
        # Add current route if it has points
        if self.current_route:
            if len(self.current_route) >= 2:
                start = self.current_route[0]
                end = self.current_route[-1]
                length = self.calculate_route_length(self.current_route)
                info = f"Current: ({start[0]},{start[1]}) → ({end[0]},{end[1]}) | Len: {length:.2f}"
                self.route_listbox.insert(tk.END, info)
            elif len(self.current_route) == 1:
                start = self.current_route[0]
                info = f"Current: ({start[0]},{start[1]}) (single point)"
                self.route_listbox.insert(tk.END, info)
        
        # If no routes, show placeholder
        if not self.routes and not self.current_route:
            self.route_listbox.insert(tk.END, "No routes created yet")
    
    def extract_route_features(self, include_middle=False, include_thirds=False, include_euclidean=False):
        """Extract features from routes for analysis"""
        features = []
        route_labels = []
        feature_names = ["start_x", "start_y", "end_x", "end_y", "length"]
        
        # Add optional feature names
        if include_middle:
            feature_names.extend(["middle_x", "middle_y"])
        if include_thirds:
            feature_names.extend(["third1_x", "third1_y", "third2_x", "third2_y"])
        if include_euclidean:
            feature_names.append("euclidean_dist")
        
        # Extract features from completed routes
        for i, route in enumerate(self.routes):
            if len(route) >= 2:
                feature_vector = self._extract_single_route_features(route, include_middle, include_thirds, include_euclidean)
                features.append(feature_vector)
                route_labels.append(f"Route {i+1}")
        
        # Add current route if it has at least 2 points
        if len(self.current_route) >= 2:
            feature_vector = self._extract_single_route_features(self.current_route, include_middle, include_thirds, include_euclidean)
            features.append(feature_vector)
            route_labels.append("Current Route")
        
        return np.array(features), route_labels, feature_names
    
    def _extract_single_route_features(self, route, include_middle=False, include_thirds=False, include_euclidean=False):
        """Extract features from a single route"""
        start_x, start_y = route[0]
        end_x, end_y = route[-1]
        length = self.calculate_route_length(route)
        
        # Base features: [start_x, start_y, end_x, end_y, length]
        feature_vector = [start_x, start_y, end_x, end_y, length]
        
        # Add middle point coordinates
        if include_middle:
            middle_x, middle_y = self.get_middle_point(route)
            feature_vector.extend([middle_x, middle_y])
        
        # Add 1/3 and 2/3 point coordinates
        if include_thirds:
            point_1_3, point_2_3 = self.get_third_points(route)
            feature_vector.extend([point_1_3[0], point_1_3[1], point_2_3[0], point_2_3[1]])
        
        # Add Euclidean distance from start to end
        if include_euclidean:
            euclidean_dist = self.calculate_euclidean_distance(route)
            feature_vector.append(euclidean_dist)
        
        return feature_vector
    
    def open_analysis_dialog(self):
        """Open dimensionality reduction analysis dialog"""
        if not ALGORITHMS_AVAILABLE:
            messagebox.showerror("Error", "Required libraries not available. Please install: pip install umap-learn matplotlib scikit-learn")
            return
        
        # Check if we have enough routes (basic check)
        total_routes = len(self.routes) + (1 if len(self.current_route) >= 2 else 0)
        if total_routes < 2:
            messagebox.showwarning("Warning", "Need at least 2 routes for analysis")
            return
        
        # Create parameter dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Dimensionality Reduction Analysis")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Parameter frame
        param_frame = tk.Frame(dialog)
        param_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        tk.Label(param_frame, text="Dimensionality Reduction Analysis", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Algorithm selection
        tk.Label(param_frame, text="Select Algorithm:").pack(anchor=tk.W)
        algorithm_var = tk.StringVar(value="UMAP")
        algorithm_combo = ttk.Combobox(param_frame, textvariable=algorithm_var, 
                                     values=["UMAP", "t-SNE", "PCA", "MDS", "Isomap"], state="readonly")
        algorithm_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Create a notebook for algorithm-specific parameters
        notebook = ttk.Notebook(param_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # UMAP parameters frame
        umap_frame = ttk.Frame(notebook)
        notebook.add(umap_frame, text="UMAP")
        
        tk.Label(umap_frame, text="Number of Neighbors (2-50):").pack(anchor=tk.W, pady=(10, 0))
        n_neighbors_var = tk.IntVar(value=min(15, total_routes - 1))
        n_neighbors_scale = tk.Scale(umap_frame, from_=2, to=min(50, total_routes - 1), 
                                   orient=tk.HORIZONTAL, variable=n_neighbors_var)
        n_neighbors_scale.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(umap_frame, text="Minimum Distance (0.0-1.0):").pack(anchor=tk.W)
        min_dist_var = tk.DoubleVar(value=0.1)
        min_dist_scale = tk.Scale(umap_frame, from_=0.0, to=1.0, resolution=0.01,
                                orient=tk.HORIZONTAL, variable=min_dist_var)
        min_dist_scale.pack(fill=tk.X, pady=(0, 10))
        
        # t-SNE parameters frame
        tsne_frame = ttk.Frame(notebook)
        notebook.add(tsne_frame, text="t-SNE")
        
        tk.Label(tsne_frame, text="Perplexity (5-50):").pack(anchor=tk.W, pady=(10, 0))
        perplexity_var = tk.IntVar(value=min(30, total_routes - 1))
        perplexity_scale = tk.Scale(tsne_frame, from_=5, to=min(50, total_routes - 1), 
                                  orient=tk.HORIZONTAL, variable=perplexity_var)
        perplexity_scale.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(tsne_frame, text="Learning Rate (10-1000):").pack(anchor=tk.W)
        learning_rate_var = tk.IntVar(value=200)
        learning_rate_scale = tk.Scale(tsne_frame, from_=10, to=1000, 
                                     orient=tk.HORIZONTAL, variable=learning_rate_var)
        learning_rate_scale.pack(fill=tk.X, pady=(0, 10))
        
        # PCA parameters frame
        pca_frame = ttk.Frame(notebook)
        notebook.add(pca_frame, text="PCA")
        tk.Label(pca_frame, text="PCA is parameter-free for 2D projection", 
                font=("Arial", 10), fg="gray").pack(pady=20)
        
        # MDS parameters frame
        mds_frame = ttk.Frame(notebook)
        notebook.add(mds_frame, text="MDS")
        tk.Label(mds_frame, text="MDS is parameter-free for 2D projection", 
                font=("Arial", 10), fg="gray").pack(pady=20)
        
        # Isomap parameters frame
        isomap_frame = ttk.Frame(notebook)
        notebook.add(isomap_frame, text="Isomap")
        
        tk.Label(isomap_frame, text="Number of Neighbors (2-50):").pack(anchor=tk.W, pady=(10, 0))
        iso_neighbors_var = tk.IntVar(value=min(5, total_routes - 1))
        iso_neighbors_scale = tk.Scale(isomap_frame, from_=2, to=min(50, total_routes - 1), 
                                     orient=tk.HORIZONTAL, variable=iso_neighbors_var)
        iso_neighbors_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Common parameters
        tk.Label(param_frame, text="Distance Metric:").pack(anchor=tk.W)
        metric_var = tk.StringVar(value="euclidean")
        metric_combo = ttk.Combobox(param_frame, textvariable=metric_var, 
                                  values=["euclidean", "manhattan", "cosine"], state="readonly")
        metric_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Feature selection frame
        feature_frame = tk.LabelFrame(param_frame, text="Optional Features")
        feature_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Feature checkboxes
        include_middle_var = tk.BooleanVar(value=False)
        include_thirds_var = tk.BooleanVar(value=False)
        include_euclidean_var = tk.BooleanVar(value=False)
        
        tk.Checkbutton(feature_frame, text="Include middle point coordinates", 
                      variable=include_middle_var).pack(anchor=tk.W, padx=5, pady=2)
        tk.Checkbutton(feature_frame, text="Include 1/3 and 2/3 point coordinates", 
                      variable=include_thirds_var).pack(anchor=tk.W, padx=5, pady=2)
        tk.Checkbutton(feature_frame, text="Include Euclidean distance (start to end)", 
                      variable=include_euclidean_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Info label (will be updated dynamically)
        base_features = 5
        info_text = f"Data: {total_routes} routes with {base_features} base features\n(start_x, start_y, end_x, end_y, length)"
        info_label = tk.Label(param_frame, text=info_text, fg="gray")
        info_label.pack(pady=(0, 15))
        
        def update_feature_count():
            """Update feature count based on selected options"""
            count = base_features
            feature_list = ["start_x", "start_y", "end_x", "end_y", "length"]
            
            if include_middle_var.get():
                count += 2
                feature_list.extend(["middle_x", "middle_y"])
            if include_thirds_var.get():
                count += 4
                feature_list.extend(["third1_x", "third1_y", "third2_x", "third2_y"])
            if include_euclidean_var.get():
                count += 1
                feature_list.append("euclidean_dist")
            
            info_text = f"Data: {total_routes} routes with {count} features\n({', '.join(feature_list)})"
            info_label.config(text=info_text)
        
        # Bind checkbox events
        include_middle_var.trace('w', lambda *args: update_feature_count())
        include_thirds_var.trace('w', lambda *args: update_feature_count())
        include_euclidean_var.trace('w', lambda *args: update_feature_count())
        
        # Buttons
        button_frame = tk.Frame(param_frame)
        button_frame.pack(fill=tk.X)
        
        def run_analysis():
            try:
                algorithm = algorithm_var.get()
                metric = metric_var.get()
                
                # Extract features with selected options
                final_features, final_labels, feature_names = self.extract_route_features(
                    include_middle=include_middle_var.get(),
                    include_thirds=include_thirds_var.get(),
                    include_euclidean=include_euclidean_var.get()
                )
                
                # Validate that we have enough data
                if len(final_features) < 2:
                    messagebox.showwarning("Warning", "Need at least 2 routes for analysis")
                    return
                
                # Create parameter dictionary for the specific algorithm
                analysis_params = {
                    'algorithm': algorithm,
                    'metric': metric,
                    'feature_names': feature_names
                }
                
                if algorithm == "UMAP":
                    analysis_params['n_neighbors'] = n_neighbors_var.get()
                    analysis_params['min_dist'] = min_dist_var.get()
                elif algorithm == "t-SNE":
                    analysis_params['perplexity'] = perplexity_var.get()
                    analysis_params['learning_rate'] = learning_rate_var.get()
                elif algorithm == "Isomap":
                    analysis_params['n_neighbors'] = iso_neighbors_var.get()
                
                dialog.destroy()
                self.run_dimensionality_analysis(final_features, final_labels, **analysis_params)
            except Exception as e:
                messagebox.showerror("Error", f"Analysis failed: {str(e)}")
        
        def compare_all():
            try:
                # Extract features with selected options
                final_features, final_labels, feature_names = self.extract_route_features(
                    include_middle=include_middle_var.get(),
                    include_thirds=include_thirds_var.get(),
                    include_euclidean=include_euclidean_var.get()
                )
                dialog.destroy()
                self.compare_all_algorithms(final_features, final_labels, feature_names)
            except Exception as e:
                messagebox.showerror("Error", f"Comparison failed: {str(e)}")
        
        tk.Button(button_frame, text="Run Analysis", command=run_analysis).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="Compare All", command=compare_all).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
    
    def run_dimensionality_analysis(self, features, labels, algorithm, metric='euclidean', feature_names=None, **params):
        """Run dimensionality reduction analysis with specified algorithm"""
        try:
            # Normalize features for better performance
            scaler = StandardScaler()
            features_normalized = scaler.fit_transform(features)
            
            # Validate parameters based on data size
            n_samples = features_normalized.shape[0]
            
            # Create reducer based on algorithm
            if algorithm == "UMAP":
                n_neighbors = min(params.get('n_neighbors', 15), n_samples - 1)
                reducer = umap.UMAP(
                    n_neighbors=max(2, n_neighbors),
                    min_dist=params.get('min_dist', 0.1),
                    n_components=2,
                    metric=metric,
                    random_state=42
                )
            elif algorithm == "t-SNE":
                # t-SNE only supports certain metrics
                tsne_metric = metric if metric in ['euclidean', 'manhattan', 'cosine'] else 'euclidean'
                perplexity = min(params.get('perplexity', 30), (n_samples - 1) // 3)
                reducer = TSNE(
                    n_components=2,
                    perplexity=max(1, perplexity),
                    learning_rate=params.get('learning_rate', 200),
                    random_state=42,
                    metric=tsne_metric
                )
            elif algorithm == "PCA":
                # PCA doesn't use metric parameter
                reducer = PCA(n_components=2, random_state=42)
            elif algorithm == "MDS":
                # MDS doesn't use metric parameter in this context
                reducer = MDS(n_components=2, metric=True, random_state=42)
            elif algorithm == "Isomap":
                # Isomap only supports certain metrics
                iso_metric = metric if metric in ['euclidean', 'manhattan'] else 'euclidean'
                n_neighbors = min(params.get('n_neighbors', 5), n_samples - 1)
                reducer = Isomap(
                    n_neighbors=max(2, n_neighbors),
                    n_components=2,
                    metric=iso_metric
                )
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            # Fit and transform data
            embedding = reducer.fit_transform(features_normalized)
            
            # Create visualization window
            self.show_analysis_results(embedding, labels, features, algorithm, params, metric, feature_names)
            
        except Exception as e:
            messagebox.showerror("Error", f"{algorithm} analysis failed: {str(e)}")
    
    def compare_all_algorithms(self, features, labels, feature_names=None):
        """Compare all algorithms side by side"""
        
        try:
            # Normalize features
            scaler = StandardScaler()
            features_normalized = scaler.fit_transform(features)
            
            # Use n_samples instead of len(features) for parameter validation
            n_samples = features_normalized.shape[0]
            
            algorithms = {
                'UMAP': umap.UMAP(n_neighbors=min(15, n_samples-1), min_dist=0.1, n_components=2, random_state=42),
                't-SNE': TSNE(n_components=2, perplexity=min(30, n_samples-1), random_state=42, metric='euclidean'),
                'PCA': PCA(n_components=2, random_state=42),
                'MDS': MDS(n_components=2, metric=True, random_state=42),
                'Isomap': Isomap(n_neighbors=min(5, n_samples-1), n_components=2, metric='euclidean')
            }
            
            embeddings = {}
            for name, reducer in algorithms.items():
                try:
                    embeddings[name] = reducer.fit_transform(features_normalized)
                except Exception as e:
                    print(f"Failed to run {name}: {e}")
                    continue
            
            # Create comparison visualization
            self.show_algorithm_comparison(embeddings, labels, features, feature_names)
            
        except Exception as e:
            messagebox.showerror("Error", f"Algorithm comparison failed: {str(e)}")
    
    def show_analysis_results(self, embedding, labels, original_features, algorithm, params, metric, feature_names=None):
        """Show UMAP results in a new window"""
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title("UMAP Analysis Results")
        results_window.geometry("800x600")
        
        # Create matplotlib figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot 1: UMAP embedding
        colors = np.random.rand(len(embedding), 3)  # Random colors for each point
        scatter = ax1.scatter(embedding[:, 0], embedding[:, 1], c=colors, s=100, alpha=0.7)
        
        # Add labels to points
        for i, label in enumerate(labels):
            ax1.annotate(label, (embedding[i, 0], embedding[i, 1]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
        ax1.set_title(f'{algorithm} Projection\n({param_str}, metric={metric})')
        ax1.set_xlabel('UMAP 1')
        ax1.set_ylabel('UMAP 2')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Original feature space (length vs distance between start/end)
        distances = []
        lengths = []
        for feature in original_features:
            # Extract only the first 5 features (start_x, start_y, end_x, end_y, length)
            start_x, start_y, end_x, end_y, length = feature[:5]
            euclidean_dist = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
            distances.append(euclidean_dist)
            lengths.append(length)
        
        ax2.scatter(distances, lengths, c=colors, s=100, alpha=0.7)
        for i, label in enumerate(labels):
            ax2.annotate(label, (distances[i], lengths[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax2.set_title('Original Feature Space')
        ax2.set_xlabel('Euclidean Distance (Start to End)')
        ax2.set_ylabel('Route Length')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Embed matplotlib in tkinter
        canvas = FigureCanvasTkAgg(fig, results_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add info panel
        info_frame = tk.Frame(results_window)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if feature_names:
            feature_text = ", ".join(feature_names)
            info_text = f"Analysis of {len(labels)} routes | Features: {feature_text}"
        else:
            info_text = f"Analysis of {len(labels)} routes | Features: start_x, start_y, end_x, end_y, length"
        tk.Label(info_frame, text=info_text, font=("Arial", 10)).pack()
        
        # Clustering controls
        cluster_frame = tk.LabelFrame(info_frame, text="Clustering Options")
        cluster_frame.pack(fill=tk.X, pady=5)
        
        # Clustering algorithm selection
        cluster_algo_frame = tk.Frame(cluster_frame)
        cluster_algo_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(cluster_algo_frame, text="Algorithm:").pack(side=tk.LEFT)
        cluster_algo_var = tk.StringVar(value="DBSCAN")
        cluster_algo_combo = ttk.Combobox(cluster_algo_frame, textvariable=cluster_algo_var, 
                                        values=["DBSCAN", "OPTICS"], state="readonly", width=10)
        cluster_algo_combo.pack(side=tk.LEFT, padx=5)
        
        # DBSCAN parameters
        dbscan_frame = tk.Frame(cluster_frame)
        dbscan_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(dbscan_frame, text="Eps:").pack(side=tk.LEFT)
        eps_var = tk.DoubleVar(value=0.5)
        eps_scale = tk.Scale(dbscan_frame, from_=0.1, to=2.0, resolution=0.1, 
                           orient=tk.HORIZONTAL, variable=eps_var, length=150)
        eps_scale.pack(side=tk.LEFT, padx=5)
        
        tk.Label(dbscan_frame, text="Min Samples:").pack(side=tk.LEFT, padx=(10, 0))
        min_samples_var = tk.IntVar(value=max(2, len(labels) // 4))
        min_samples_scale = tk.Scale(dbscan_frame, from_=2, to=len(labels), 
                                   orient=tk.HORIZONTAL, variable=min_samples_var, length=100)
        min_samples_scale.pack(side=tk.LEFT, padx=5)
        
        # Clustering buttons
        button_frame = tk.Frame(cluster_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def apply_clustering():
            try:
                self.apply_clustering_to_embedding(
                    embedding, labels, original_features, algorithm, params, metric, feature_names,
                    results_window, fig, ax1, ax2,
                    cluster_algo_var.get(), eps_var.get(), min_samples_var.get()
                )
            except Exception as e:
                messagebox.showerror("Error", f"Clustering failed: {str(e)}")
        
        def highlight_routes():
            try:
                self.highlight_original_routes_by_clusters(
                    embedding, labels, cluster_algo_var.get(), eps_var.get(), min_samples_var.get()
                )
            except Exception as e:
                messagebox.showerror("Error", f"Route highlighting failed: {str(e)}")
        
        tk.Button(button_frame, text="Apply Clustering", command=apply_clustering).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Highlight Routes", command=highlight_routes).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=results_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_algorithm_comparison(self, embeddings, labels, original_features, feature_names=None):
        """Show comparison of all algorithms in a single window"""
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title("Algorithm Comparison")
        results_window.geometry("1200x800")
        
        # Calculate number of algorithms
        n_algorithms = len(embeddings)
        if n_algorithms == 0:
            messagebox.showwarning("Warning", "No algorithms succeeded")
            results_window.destroy()
            return
        
        # Create matplotlib figure with subplots
        cols = min(3, n_algorithms)
        rows = (n_algorithms + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(15, 5*rows))
        
        # Handle case of single subplot
        if n_algorithms == 1:
            axes = [axes]
        elif rows == 1:
            axes = [axes] if n_algorithms == 1 else axes
        else:
            axes = axes.flatten()
        
        colors = np.random.rand(len(labels), 3)  # Random colors for each point
        
        for i, (algorithm, embedding) in enumerate(embeddings.items()):
            ax = axes[i]
            
            # Plot embedding
            scatter = ax.scatter(embedding[:, 0], embedding[:, 1], c=colors, s=100, alpha=0.7)
            
            # Add labels to points
            for j, label in enumerate(labels):
                ax.annotate(label, (embedding[j, 0], embedding[j, 1]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
            
            ax.set_title(f'{algorithm}')
            ax.set_xlabel(f'{algorithm} 1')
            ax.set_ylabel(f'{algorithm} 2')
            ax.grid(True, alpha=0.3)
        
        # Hide unused subplots
        for i in range(n_algorithms, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        # Embed matplotlib in tkinter
        canvas = FigureCanvasTkAgg(fig, results_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add info panel
        info_frame = tk.Frame(results_window)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = f"Comparison of {len(embeddings)} algorithms on {len(labels)} routes"
        if feature_names:
            info_text += f" using {len(feature_names)} features"
        tk.Label(info_frame, text=info_text, font=("Arial", 12, "bold")).pack()
        
        # Algorithm descriptions
        descriptions = {
            'UMAP': 'Preserves local and global structure',
            't-SNE': 'Good for local structure, may distort global',
            'PCA': 'Linear, preserves variance',
            'MDS': 'Preserves pairwise distances',
            'Isomap': 'Non-linear, preserves geodesic distances'
        }
        
        desc_text = "\n".join([f"{alg}: {descriptions.get(alg, '')}" for alg in embeddings.keys()])
        tk.Label(info_frame, text=desc_text, font=("Arial", 9), justify=tk.LEFT).pack(pady=5)
        
        # Close button
        tk.Button(info_frame, text="Close", command=results_window.destroy).pack(pady=5)
    
    def apply_clustering_to_embedding(self, embedding, labels, original_features, algorithm, params, metric, feature_names,
                                    results_window, fig, ax1, ax2, cluster_algo, eps, min_samples):
        """Apply clustering to the 2D embedding and update visualization"""
        try:
            # Perform clustering
            if cluster_algo == "DBSCAN":
                clusterer = DBSCAN(eps=eps, min_samples=min_samples)
            elif cluster_algo == "OPTICS":
                clusterer = OPTICS(min_samples=min_samples)
            else:
                raise ValueError(f"Unknown clustering algorithm: {cluster_algo}")
            
            cluster_labels = clusterer.fit_predict(embedding)
            
            # Get unique clusters (excluding noise points labeled as -1)
            unique_clusters = np.unique(cluster_labels)
            n_clusters = len(unique_clusters) - (1 if -1 in unique_clusters else 0)
            n_noise = np.sum(cluster_labels == -1)
            
            # Create color map for clusters
            colors = self.generate_cluster_colors(cluster_labels)
            
            # Clear and redraw the first plot with clustering
            ax1.clear()
            
            # Plot points with cluster colors
            for i, (point, label, cluster_label) in enumerate(zip(embedding, labels, cluster_labels)):
                color = colors[i]
                marker = 'o' if cluster_label != -1 else 'x'  # X for noise points
                size = 100 if cluster_label != -1 else 50
                ax1.scatter(point[0], point[1], c=[color], marker=marker, s=size, alpha=0.7, edgecolors='black')
                
                # Add route label
                ax1.annotate(label, (point[0], point[1]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
            
            param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
            ax1.set_title(f'{algorithm} + {cluster_algo} Clustering\n'
                         f'({param_str}, metric={metric})\n'
                         f'Clusters: {n_clusters}, Noise: {n_noise}')
            ax1.set_xlabel(f'{algorithm} 1')
            ax1.set_ylabel(f'{algorithm} 2')
            ax1.grid(True, alpha=0.3)
            
            # Add legend for clusters
            legend_elements = []
            for cluster_id in unique_clusters:
                if cluster_id == -1:
                    legend_elements.append(plt.Line2D([0], [0], marker='x', color='w', 
                                                    markerfacecolor='gray', markersize=8, label='Noise'))
                else:
                    cluster_color = colors[np.where(cluster_labels == cluster_id)[0][0]]
                    legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                                    markerfacecolor=cluster_color, markersize=8, 
                                                    label=f'Cluster {cluster_id}'))
            
            if legend_elements:
                ax1.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
            
            # Refresh the canvas
            fig.canvas.draw()
            
            # Store clustering results for route highlighting
            self.last_clustering_results = {
                'embedding': embedding,
                'labels': labels,
                'cluster_labels': cluster_labels,
                'colors': colors,
                'algorithm': cluster_algo,
                'params': {'eps': eps, 'min_samples': min_samples}
            }
            
            messagebox.showinfo("Clustering Complete", 
                              f"Clustering complete!\nClusters found: {n_clusters}\nNoise points: {n_noise}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Clustering failed: {str(e)}")
    
    def generate_cluster_colors(self, cluster_labels):
        """Generate distinct colors for each cluster"""
        unique_clusters = np.unique(cluster_labels)
        colors = []
        
        # Define a set of distinct colors
        cluster_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                         '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA',
                         '#F1948A', '#85C9F5', '#F9E79F', '#D7BDE2', '#A9DFBF']
        
        # Create color mapping
        cluster_color_map = {}
        color_idx = 0
        
        for cluster_id in unique_clusters:
            if cluster_id == -1:  # Noise points
                cluster_color_map[cluster_id] = '#808080'  # Gray
            else:
                cluster_color_map[cluster_id] = cluster_colors[color_idx % len(cluster_colors)]
                color_idx += 1
        
        # Assign colors to each point
        for cluster_label in cluster_labels:
            colors.append(cluster_color_map[cluster_label])
        
        return colors
    
    def highlight_original_routes_by_clusters(self, embedding, labels, cluster_algo, eps, min_samples):
        """Highlight original routes on the main canvas with cluster colors"""
        try:
            # Check if we have clustering results
            if not hasattr(self, 'last_clustering_results'):
                messagebox.showwarning("Warning", "Please apply clustering first!")
                return
            
            clustering_results = self.last_clustering_results
            
            # Clear existing route drawings and redraw with cluster colors
            self.canvas.delete("lines")
            self.canvas.delete("points")
            self.canvas.delete("point_labels")
            
            # Create route-to-cluster mapping
            route_to_cluster = {}
            for i, label in enumerate(clustering_results['labels']):
                cluster_id = clustering_results['cluster_labels'][i]
                color = clustering_results['colors'][i]
                route_to_cluster[label] = {'cluster_id': cluster_id, 'color': color}
            
            # Redraw completed routes with cluster colors
            for i, route in enumerate(self.routes):
                route_label = f"Route {i+1}"
                if route_label in route_to_cluster:
                    cluster_info = route_to_cluster[route_label]
                    self.draw_route_with_color(route, cluster_info['color'])
                else:
                    # Fallback to default color if not found
                    self.draw_route_with_color(route, "#0000FF")
            
            # Redraw current route with cluster color
            if self.current_route and "Current Route" in route_to_cluster:
                cluster_info = route_to_cluster["Current Route"]
                self.draw_route_with_color(self.current_route, cluster_info['color'])
            elif self.current_route:
                # Fallback to default color
                self.draw_route_with_color(self.current_route, "#0000FF")
            
            messagebox.showinfo("Routes Highlighted", 
                              "Original routes have been color-coded by their clusters!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Route highlighting failed: {str(e)}")
    
    def draw_route_with_color(self, route, color):
        """Draw a route with a specific color"""
        for i, point in enumerate(route):
            coord_x, coord_y = point
            canvas_x = self.coord_to_canvas_x(coord_x)
            canvas_y = self.coord_to_canvas_y(coord_y)
            
            # Draw point with cluster color
            self.canvas.create_oval(
                canvas_x - self.point_radius, canvas_y - self.point_radius,
                canvas_x + self.point_radius, canvas_y + self.point_radius,
                fill=color, outline="black", width=1, tags="points"
            )
            
            # Add coordinate label
            self.canvas.create_text(
                canvas_x, canvas_y - 15, 
                text=f"({coord_x},{coord_y})", 
                font=("Arial", 8), 
                fill="black", 
                tags="point_labels"
            )
            
            # Draw line to previous point with cluster color
            if i > 0:
                prev_point = route[i-1]
                prev_canvas_x = self.coord_to_canvas_x(prev_point[0])
                prev_canvas_y = self.coord_to_canvas_y(prev_point[1])
                self.canvas.create_line(prev_canvas_x, prev_canvas_y, canvas_x, canvas_y, 
                                      fill=color, width=2, tags="lines")
    
    def on_mouse_move(self, event):
        """Update coordinate display as mouse moves"""
        if not self.dragging:  # Only update if not dragging
            coord_x = self.canvas_to_coord_x(event.x)
            coord_y = self.canvas_to_coord_y(event.y)
            self.coord_label.config(text=f"Coordinates: ({coord_x}, {coord_y})")

def main():
    root = tk.Tk()
    app = TrackingRouteDrawer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
