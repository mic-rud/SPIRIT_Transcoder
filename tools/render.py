import argparse
import open3d as o3d

def render_ply_headless(ply_path, output_image_path, width=640, height=480):
    geometry = o3d.io.read_point_cloud(ply_path)
    if geometry.is_empty():
        raise ValueError(f"Failed to load geometry from {ply_path}")

    render = o3d.visualization.rendering.OffscreenRenderer(width, height)
    render.scene.set_background([1, 1, 1, 1])
    render.scene.add_geometry("object", geometry, o3d.visualization.rendering.MaterialRecord())

    bounds = geometry.get_axis_aligned_bounding_box()
    center = bounds.get_center()
    render.setup_camera(60.0, bounds, center)

    image = render.render_to_image()
    o3d.io.write_image(output_image_path, image)
    render.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Headless Open3D PLY renderer")
    parser.add_argument("ply", help="Path to .ply file")
    parser.add_argument("out", help="Path to output PNG screenshot")
    parser.add_argument("--width", type=int, default=640, help="Image width")
    parser.add_argument("--height", type=int, default=480, help="Image height")
    args = parser.parse_args()

    render_ply_headless(args.ply, args.out, args.width, args.height)
