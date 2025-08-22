# Tracking Routes Drawer

A powerful interactive tool for creating, visualizing, and analyzing tracking routes with advanced dimensionality reduction and clustering capabilities.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

### 🎯 Interactive Route Drawing
- **Left-click**: Add points to create tracking routes
- **Drag & Drop**: Left-click and drag existing points to reposition them
- **Right-click on point**: Remove individual points
- **Right-click on line**: Insert new points between existing ones
- **Grid-based coordinate system**: Top-left origin (0,0) with Y increasing downward

### 📊 Route Information Panel
- **Real-time route list**: Shows start/end coordinates and route lengths
- **Route statistics**: Displays total distance and point counts
- **Live updates**: Automatically refreshes as you modify routes

<img width="1000" alt="{347FD732-4044-4686-808A-26921F36AFF5}" src="https://github.com/user-attachments/assets/a6b7f415-dfd2-4038-914e-fe6baec0bf18" />

### 🔬 Advanced Analytics

#### Dimensionality Reduction Algorithms
- **UMAP**: Uniform Manifold Approximation and Projection
- **t-SNE**: t-Distributed Stochastic Neighbor Embedding
- **PCA**: Principal Component Analysis
- **MDS**: Multidimensional Scaling
- **Isomap**: Isometric Mapping

<img width="350" alt="{AAB73FAA-11A9-4BD3-9D3B-73C3B73A43B7}" src="https://github.com/user-attachments/assets/ce0edc86-6d85-4b08-b193-36efe794574e" />

#### Extended Feature Analysis
- **Base features** (5): start_x, start_y, end_x, end_y, route_length
- **Middle point coordinates** (+2): Coordinates at 50% of route distance
- **Third point coordinates** (+4): Coordinates at 1/3 and 2/3 of route distance
- **Euclidean distance** (+1): Straight-line distance from start to end

#### Clustering Analysis
- **DBSCAN**: Density-based clustering for arbitrary cluster shapes
- **OPTICS**: Clustering with varying density tolerance
- **Noise detection**: Identifies outlier routes
- **Color-coded visualization**: Clusters displayed with distinct colors

### 🎨 Visualization Features
- **2D embeddings**: Visualize high-dimensional route data in 2D space
- **Algorithm comparison**: Side-by-side comparison of all reduction methods
- **Interactive clustering**: Apply clustering to 2D results with adjustable parameters
- **Route highlighting**: Color-code original routes based on cluster assignments

<img width="1000" alt="{FA6AE291-1832-46F3-8B66-AA56F1CAB122}" src="https://github.com/user-attachments/assets/50df0242-c3af-491d-9674-b6d2a3406574" />

## Installation

### Requirements
```bash
pip install numpy matplotlib scikit-learn umap-learn tkinter
```

### Dependencies
- Python 3.7+
- NumPy
- Matplotlib
- scikit-learn
- UMAP-learn
- Tkinter (usually included with Python)

## Usage

### Running the Application
```bash
python tracking_routs_drawer.py
```

### Basic Workflow

#### 1. Creating Routes
1. **Start drawing**: Left-click on the canvas to place the first point
2. **Continue route**: Left-click to add more points (they connect automatically)
3. **New route**: Click "New Route" button to start a separate route
4. **Edit points**: 
   - Drag existing points to reposition them
   - Right-click points to remove them
   - Right-click lines to insert new points

#### 2. Route Analysis
1. **Open analysis**: Click "Dimensionality Analysis" (requires 2+ routes)
2. **Select algorithm**: Choose from UMAP, t-SNE, PCA, MDS, or Isomap
3. **Configure features**: Optionally include middle points, third points, or Euclidean distance
4. **Set parameters**: Adjust algorithm-specific parameters
5. **Run analysis**: Click "Run Analysis" or "Compare All"

#### 3. Clustering Analysis
1. **After dimensionality reduction**: Use clustering controls in results window
2. **Choose algorithm**: Select DBSCAN or OPTICS
3. **Adjust parameters**:
   - **Eps**: Distance threshold for cluster formation
   - **Min Samples**: Minimum points required for a cluster
4. **Apply clustering**: View color-coded clusters in 2D space
5. **Highlight routes**: Color original routes based on cluster assignments

## Algorithm Details

### Dimensionality Reduction

| Algorithm | Best For | Key Parameters |
|-----------|----------|----------------|
| **UMAP** | General purpose, preserves local and global structure | n_neighbors, min_dist |
| **t-SNE** | Local structure, tight clusters | perplexity, learning_rate |
| **PCA** | Linear relationships, variance preservation | (parameter-free) |
| **MDS** | Distance preservation | (parameter-free) |
| **Isomap** | Non-linear manifolds, geodesic distances | n_neighbors |

### Clustering

| Algorithm | Best For | Key Parameters |
|-----------|----------|----------------|
| **DBSCAN** | Arbitrary cluster shapes, noise detection | eps, min_samples |
| **OPTICS** | Varying density clusters | min_samples |

### Feature Engineering

The application extracts meaningful features from routes for analysis:

- **Spatial features**: Start/end coordinates
- **Distance metrics**: Route length vs. straight-line distance
- **Shape descriptors**: Middle and third-point coordinates
- **Efficiency measures**: Route directness (euclidean/route_length ratio)

## Examples

### Use Cases

#### 1. Route Pattern Discovery
- Identify similar route types (direct vs. curved)
- Find common starting/ending areas
- Detect unusual or outlier routes

#### 2. Efficiency Analysis
- Compare route directness across different areas
- Identify consistently efficient vs. inefficient routes
- Optimize route planning based on patterns

#### 3. Clustering Applications
- Group routes by similarity
- Identify natural route categories
- Detect anomalous routing behavior

## Controls Reference

### Mouse Controls
- **Left-click**: Place point / Start dragging
- **Left-drag**: Move existing point
- **Right-click on point**: Remove point
- **Right-click on line**: Insert point

### Buttons
- **New Route**: Start a new tracking route
- **Clear All**: Remove all routes
- **Undo Last Point**: Remove the last point from current route
- **Dimensionality Analysis**: Open advanced analytics

### Analysis Controls
- **Algorithm selection**: Choose dimensionality reduction method
- **Feature selection**: Include optional route characteristics
- **Parameter tuning**: Adjust algorithm-specific settings
- **Clustering options**: Apply post-analysis clustering

## Technical Details

### Coordinate System
- **Origin**: Top-left corner (0, 0)
- **X-axis**: Increases rightward
- **Y-axis**: Increases downward
- **Grid**: 20-pixel spacing with coordinate labels

### Data Structure
- Routes stored as lists of (x, y) coordinate tuples
- Feature vectors created dynamically based on user selections
- Clustering results cached for route highlighting

### Performance
- Optimized for interactive use with real-time updates
- Efficient rendering for moderate numbers of routes (2-50)
- Memory-conscious implementation for extended analysis sessions

## Contributing

Contributions are welcome! Areas for enhancement:
- Additional dimensionality reduction algorithms
- More clustering methods
- Export/import functionality
- Advanced visualization options
- Performance optimizations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and Tkinter for cross-platform compatibility
- Uses scikit-learn for machine learning algorithms
- UMAP implementation for advanced dimensionality reduction
- Matplotlib for high-quality visualizations




