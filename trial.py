# 1. Import necessary libraries
import open3d as o3d
import numpy as np
from PIL import Image as PILImage
import matplotlib.pyplot as plt

# 2. Load the human body mesh (.obj)
body_mesh = o3d.io.read_triangle_mesh(
    r"C:\Users\Hajar Fawzi\AppData\Local\Temp\fdbb036e-f0c6-4bc5-85d2-e94e17ca2654_Machine.learn() CSAI253 ML Project.zip.654\Final\female.obj"
)

# 3. Load the shirt mesh (.obj)
shirt_mesh = o3d.io.read_triangle_mesh(
    r"C:\Users\Hajar Fawzi\AppData\Local\Temp\fdbb036e-f0c6-4bc5-85d2-e94e17ca2654_Machine.learn() CSAI253 ML Project.zip.654\Final\Untitled.obj"
)

# 4. Compute normals for lighting and smoothing
body_mesh.compute_vertex_normals()
shirt_mesh.compute_vertex_normals()

# 5. Print number of vertices for both meshes for debugging
print("Body vertices:", len(np.asarray(body_mesh.vertices)))
print("Shirt vertices:", len(np.asarray(shirt_mesh.vertices)))

# 6. Scale the shirt mesh slightly for a looser fit
shirt_mesh.scale(1.20, center=shirt_mesh.get_center())

# 7. Get bounding boxes for alignment
body_bbox = body_mesh.get_axis_aligned_bounding_box()
shirt_bbox = shirt_mesh.get_axis_aligned_bounding_box()

# 8. Align shirt horizontally to body
shirt_center = shirt_bbox.get_center()
body_center = body_bbox.get_center()
shirt_mesh.translate([
    body_center[0] - shirt_center[0] + 1.45,  # offset X
    0,                                        # keep Y
    body_center[2] - shirt_center[2]          # offset Z
])

# 9. Align shirt vertically to body height
body_height = body_bbox.get_extent()[1]
y_offset = (body_center[1] - shirt_center[1]) + 0.111 * body_height
shirt_mesh.translate([0, y_offset, 0])

# 10. Convert shirt to NumPy array for editing
vertices = np.asarray(shirt_mesh.vertices)
normals = np.asarray(shirt_mesh.vertex_normals)

# 11. Define chest area bounds
y_min, y_max = shirt_bbox.get_min_bound()[1], shirt_bbox.get_max_bound()[1]
y_chest_low = y_min + 0.65 * (y_max - y_min)
y_chest_high = y_min + 0.95 * (y_max - y_min)
y_chest_center = (y_chest_low + y_chest_high) / 2
center_x, center_z = shirt_bbox.get_center()[0], shirt_bbox.get_center()[2]
x_extent = shirt_bbox.get_extent()[0]
x_limit = 0.50 * x_extent

# 12. Expand shirt at chest (front only)
for i, v in enumerate(vertices):
    y, x, z = v[1], v[0], v[2]
    in_chest = y_chest_low < y < y_chest_high
    in_torso = abs(x - center_x) < x_limit
    in_front = z > center_z
    if in_chest and in_torso and in_front:
        weight_y = 1.0 - abs(y - y_chest_center) / (y_chest_high - y_chest_low)
        scale_x = 0.89 + 0.15 * weight_y
        scale_z = 2.0
        vertices[i][0] = center_x + (x - center_x) * scale_x
        vertices[i][2] = center_z + (z - center_z) * scale_z

# 13. Recompute bounding box and expand hips
shirt_bbox = o3d.geometry.AxisAlignedBoundingBox.create_from_points(o3d.utility.Vector3dVector(vertices))
y_min, y_max = shirt_bbox.get_min_bound()[1], shirt_bbox.get_max_bound()[1]
hip_start = y_min + 0.19 * (y_max - y_min)
hip_end = y_min + 0.32 * (y_max - y_min)
center_x = shirt_bbox.get_center()[0]

for i, v in enumerate(vertices):
    y, x = v[1], v[0]
    if hip_start <= y <= hip_end:
        weight = (y - hip_start) / (hip_end - hip_start)
        offset = (x - center_x)
        flare = 1.05 + 0.01 * weight
        vertices[i][0] = center_x + offset * flare

# 14. Push shirt outward globally using normals (relaxation)
vertices += 0.3 * normals
shirt_mesh.vertices = o3d.utility.Vector3dVector(vertices)
shirt_mesh = shirt_mesh.filter_smooth_laplacian(number_of_iterations=30)
shirt_mesh.compute_vertex_normals()
vertices = np.asarray(shirt_mesh.vertices)

# 15. Highlight sleeve regions (for debug coloring)
x_min, x_max = -35.7, 35.7
y_min, y_max = 66.85, 151.26
sleeve_y_low, sleeve_y_high = 100, 130
colors = np.tile([0.7, 0.7, 0.7], (vertices.shape[0], 1))
for i, v in enumerate(vertices):
    x, y, z = v
    if (x < -28.0 or x > 28.0) and sleeve_y_low < y < sleeve_y_high:
        colors[i] = [1.0, 0.0, 0.0]
shirt_mesh.vertex_colors = o3d.utility.Vector3dVector(colors)

# 16. Adjust shoulder areas (pull in X and Z)
shoulder_y_min, shoulder_y_max = 95, 135
shoulder_z_threshold = 7
for i, v in enumerate(vertices):
    x, y, z = v
    if (-35 < x < -25) and (shoulder_y_min < y < shoulder_y_max) and (-shoulder_z_threshold < z < shoulder_z_threshold):
        vertices[i][0] -= 3.0
        vertices[i][2] = 0.8 + (z - 0.8) * 0.95
    elif (25 < x < 35) and (shoulder_y_min < y < shoulder_y_max) and (-shoulder_z_threshold < z < shoulder_z_threshold):
        vertices[i][0] += 3.0
        vertices[i][2] = 0.8 + (z - 0.8) * 0.95

# 17. Smooth shirt again after sleeve adjustments
shirt_mesh.vertices = o3d.utility.Vector3dVector(vertices)
shirt_mesh = shirt_mesh.filter_smooth_laplacian(number_of_iterations=15)
shirt_mesh.compute_vertex_normals()
vertices = np.asarray(shirt_mesh.vertices)

# 18. Adjust armpit area for better fit
armpit_y_min, armpit_y_max = 105, 118
armpit_z_min, armpit_z_max = -6, 6
for i, v in enumerate(vertices):
    x, y, z = v
    if armpit_y_min <= y <= armpit_y_max and armpit_z_min <= z <= armpit_z_max:
        if -35 < x < -20:
            vertices[i][0] -= 1.5
            vertices[i][1] += 0.3
        elif 20 < x < 35:
            vertices[i][0] += 1.5
            vertices[i][1] += 0.3

# 19. Final smooth & update shirt
shirt_mesh.vertices = o3d.utility.Vector3dVector(vertices)
shirt_mesh = shirt_mesh.filter_smooth_laplacian(number_of_iterations=15)
shirt_mesh.compute_vertex_normals()

# 20. Combine body and shirt into one mesh (for export)
combined_mesh = body_mesh + shirt_mesh
o3d.io.write_triangle_mesh("tryon_result.obj", combined_mesh)  # Save final model

# 21. Assign distinct colors for visualization
body_mesh.paint_uniform_color([0.7, 0.7, 0.9])   # blue
shirt_mesh.paint_uniform_color([0.9, 0.7, 0.7])  # pink

# 22. Visualize both meshes together in an interactive 3D window
o3d.visualization.draw_geometries(
    [body_mesh, shirt_mesh],
    window_name="Virtual Try-On Viewer",
    zoom=0.7,
    front=[0, 0, -1],
    lookat=body_mesh.get_center(),
    up=[0, 1, 0]
)
