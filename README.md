# Virtual Try-On Integration for 3D Body Mesh  
**Submitted by:** Hajar ALSHAFAI  
**Date:**26 April 2025

## 1. Approach

For this prototype, I divided the task into two stages:

1. **Automated Script-Based Fitting**:
   - I used Open3D in Python to fit the provided t-shirt mesh onto the female body mesh.
   - Translations and scaling were computed by aligning the center of mass of both meshes and applying fixed scale ratios.
   - Vertex normal adjustment was used to slightly sink the shirt into the mesh for a natural look.

2. **Manual Fitting in Blender**:
   - For the remaining body meshes, I used Blender to manually adjust the shirt position using the “Proportional Editing” tool.
   - The goal was to ensure realistic draping and alignment without clipping artifacts.

## 2. Assumptions

- I assumed the shirt was created with a neutral pose that approximately matches the body meshes.
- Minor deformation and alignment issues were acceptable given the lack of cloth physics.
- Blender’s visual editor was sufficient for adjusting male meshes since automated deformation wasn’t part of the minimum deliverables.

## 3. Challenges and Solutions

- **Mesh alignment**: Different body meshes had slightly varied proportions. For female mesh, I computed bounding box centers and applied translation vectors accordingly.
- **Clipping**: I used vertex normal offsets to push the shirt outward slightly.
- **Manual fitting**: Blender was chosen for its flexibility when script-based fitting was limited for other bodies.

## 4. Future Improvements

- Integrate physics-based cloth simulation using Blender Cloth or PyBullet for more realistic draping.
- Implement UV texture mapping to enhance realism of garments.
- Automate the process for diverse body types using SMPL-X parameters and blend shapes.
- Add collision detection to prevent mesh overlap during animation.
