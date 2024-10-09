import numpy as np
from stl import mesh
from scipy.spatial import ConvexHull, QhullError


# Function to calculate the area of a 2D polygon using ConvexHull
def polygon_area(points):
    if len(points) < 3:
        return 0  # No area can be formed with fewer than 3 points
    try:
        hull = ConvexHull(points)
        return hull.volume  # In 2D, 'volume' is the area
    except QhullError:
        return 0  # Return 0 if ConvexHull fails


# Function to calculate volume using the trapezoidal rule
def calculate_volume(slice_intervals, cross_section_areas, y_value):
    # Select slices below the given Y value
    valid_slices = slice_intervals <= y_value
    selected_intervals = slice_intervals[valid_slices]
    selected_areas = np.array(cross_section_areas)[valid_slices]

    # Calculate volume using the trapezoidal rule
    return np.trapezoid(selected_areas, x=selected_intervals)


# Function to convert pounds to kilograms
def pounds_to_kg(weight_in_pounds):
    return weight_in_pounds * 0.453592


# Load the STL file (coordinates are in millimeters)
your_mesh = mesh.Mesh.from_file(r'C:\Users\josia\OneDrive\Documents\STL_Files\hull100.stl')  # INSERT FILE PATH HERE

# Get the minimum and maximum Y values from the mesh
min_y = np.min(your_mesh.vectors[:, :, 1])  # Min Y value from the mesh (lowest point of the hull)
max_y = np.max(your_mesh.vectors[:, :, 1])  # Max Y value from the mesh (highest point of the hull)

# Set slicing parameters in millimeters
slice_thickness = 0.1  # Slice thickness in millimeters (0.5 mm)

# Create slice intervals with 0.5 mm spacing starting from the min Y value
slice_intervals = np.arange(min_y, max_y, slice_thickness)

# Store cross-sectional areas in square millimeters
cross_section_areas = []

# Loop through each slice and calculate the cross-sectional area
for idx, slice_y in enumerate(slice_intervals):
    print(f"Processing slice {idx + 1}/{len(slice_intervals)} at Y = {slice_y:.2f} mm")
    slice_points = []

    # Loop through each triangle in the mesh
    for triangle in your_mesh.vectors:
        y_values = triangle[:, 1]

        # Check if the triangle intersects with the current slicing plane
        if np.min(y_values) <= slice_y <= np.max(y_values):
            # Interpolate to find the intersection points
            for i in range(3):
                v1 = triangle[i]
                v2 = triangle[(i + 1) % 3]
                if (v1[1] <= slice_y <= v2[1]) or (v2[1] <= slice_y <= v1[1]):
                    if v1[1] != v2[1]:
                        t = (slice_y - v1[1]) / (v2[1] - v1[1])
                        intersection_point = v1 + t * (v2 - v1)
                        slice_points.append(intersection_point[[0, 2]])  # Use X and Z

    # Calculate the area if enough points are available
    if len(slice_points) > 2:
        slice_points = np.array(slice_points)
        area = polygon_area(slice_points)
        cross_section_areas.append(area)
    else:
        cross_section_areas.append(0)

# Continuously ask for number of hulls and total weight, then calculate the waterline
while True:
    try:
        print()  # Add a single space before the prompt
        num_hulls = int(input("How many of these hulls will there be: ").strip())

        weight_input = input("Enter the total weight of the object (all hulls) in pounds (lb) or 'e' to exit: ").strip()

        if weight_input.lower() == 'e':
            print("Exiting the program.")
            break

        weight_lb = float(weight_input)  # Convert input to float
        weight_kg = pounds_to_kg(weight_lb)  # Convert to kilograms

        # Calculate weight per hull
        weight_per_hull_kg = weight_kg / num_hulls

        # Calculate volume of water displaced (mass / density) in cubic meters per hull
        water_density = 1000  # kg/m^3 for water
        volume_displaced_per_hull_m3 = weight_per_hull_kg / water_density

        # Calculate total displaced water volume for all hulls
        total_displaced_volume_m3 = volume_displaced_per_hull_m3 * num_hulls

        print("\n===================================================")
        print(f"Number of hulls: {num_hulls}")
        print(f"Total weight: {weight_lb:.2f} lb ({weight_kg:.2f} kg)")
        print(f"Displaced water volume per hull: {volume_displaced_per_hull_m3:.6f} cubic meters")
        print(f"Total water volume displaced: {total_displaced_volume_m3:.6f} cubic meters")

        # Find the waterline where the displaced volume matches the hull volume
        for slice_y in slice_intervals:
            current_volume_m3 = calculate_volume(slice_intervals, cross_section_areas,
                                                 slice_y) / 1e9  # Convert mm^3 to m^3
            if current_volume_m3 >= volume_displaced_per_hull_m3:
                # Calculate waterline relative to the bottom and top of the hull
                waterline_from_bottom = slice_y - min_y  # Waterline from the bottom of the hull
                waterline_from_top = max_y - slice_y  # Waterline distance from the top of the hull

                # Display the result in inches and millimeters
                waterline_mm = waterline_from_bottom
                waterline_inches = waterline_mm / 25.4
                print(f"Waterline depth from bottom of hull: {waterline_mm:.2f} mm ({waterline_inches:.2f} inches)")
                print(
                    f"Waterline distance from top of hull: {waterline_from_top:.2f} mm ({waterline_from_top / 25.4:.2f} inches)")
                break

        print("===================================================")

    except ValueError as e:
        print(f"Invalid input: {e}. Please enter valid numbers or 'e' to exit.")
