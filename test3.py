import trimesh
import numpy as np
import svgwrite
from shapely.geometry import Polygon, LinearRing
from shapely.ops import unary_union

def slice_stl(stl_file, z_level, svg_file, line_width=1.0, scale_factor=25.4):
    print("Loading STL file...")
    try:
        # Load the STL file
        mesh = trimesh.load_mesh(stl_file)
        print(f"Loaded STL file with {len(mesh.faces)} faces.")
    except Exception as e:
        print(f"Error loading STL file: {e}")
        return

    # Define the slicing plane
    plane_origin = np.array([0, 0, z_level])
    plane_normal = np.array([0, 0, 1])

    print("Slicing the mesh...")
    # Slice the mesh
    slice = mesh.section(plane_origin=plane_origin, plane_normal=plane_normal)
    if slice is None:
        print("No intersections found at the given z level.")
        return

    # Get the 2D projection of the slice
    slice_2D, _ = slice.to_planar()

    # Create the SVG file
    print("Creating the SVG file...")
    dwg = svgwrite.Drawing(svg_file, profile='tiny')

    # Ensure we are dealing with multiple polygons
    polygons = slice_2D.polygons_full
    if not isinstance(polygons, list):
        polygons = [polygons]

    num_polygons = len(polygons)
    print(f"Number of polygons found: {num_polygons}")

    for i, polygon in enumerate(polygons):
        if polygon is not None and isinstance(polygon, Polygon):
            print(f"Processing polygon {i + 1}/{num_polygons}")
            # Convert to Shapely Polygon and apply scaling
            scaled_exterior = [(p[0] * scale_factor, p[1] * scale_factor) for p in polygon.exterior.coords]
            scaled_polygon = Polygon(scaled_exterior)

            # Check if the polygon needs to be simplified to close gaps
            if not scaled_polygon.is_valid:
                print(f"Polygon {i + 1} is not valid, attempting to fix it.")
                scaled_polygon = scaled_polygon.buffer(0)  # Attempt to fix invalid polygon

            # Create a LinearRing to ensure the polygon is closed
            closed_ring = LinearRing(scaled_polygon.exterior.coords)
            if not closed_ring.is_closed:
                closed_ring = LinearRing(closed_ring.coords[:] + [closed_ring.coords[0]])

            # Convert the ring to a path
            points = [(p[0], p[1]) for p in closed_ring.coords]
            dwg.add(dwg.polyline(points, stroke='black', fill='none', stroke_width=line_width, stroke_linejoin='miter'))

    try:
        dwg.save()
        print(f"SVG file saved as {svg_file}")
    except Exception as e:
        print(f"Error saving SVG file: {e}")

# Example usage
stl_file = '~/Downloads/head-research.stl'  # Path to your STL file
z_level = 0.5  # The Z-level for the slice
svg_file = 'slice.svg'  # Output SVG file
line_width = 1.0  # Line width for the SVG
scale_factor = 20.0 / 5.74  # Calculated scale factor

slice_stl(stl_file, z_level, svg_file, line_width, scale_factor)

