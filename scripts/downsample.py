import numpy as np
import open3d as o3d

import argparse
import os

def voxel_downsample(pcd: o3d.geometry.PointCloud, voxel_size: float) -> o3d.geometry.PointCloud:
    """
    Downsample point cloud using voxels.
    """
    pcd_down = pcd.voxel_down_sample(voxel_size)

    # Adjust coordinates
    pts = np.floor(np.asarray(pcd_down.points) / voxel_size).astype(np.int32)
    pcd_down.points = o3d.utility.Vector3dVector(pts)
    return pcd_down


def process_directory(input_dir: str, output_dir: str, voxel_size: float):
    ply_files = os.listdir(input_dir)
    print(ply_files)
    if not ply_files:
        print(f"[WARN] No .ply files found in {input_dir}")
        return

    os.makedirs(output_dir, exist_ok=True)

    for ply_file in ply_files:
        ply_path = os.path.join(input_dir, ply_file)
        out_path = os.path.join(output_dir, ply_file)
        print(ply_path)

        pcd = o3d.io.read_point_cloud(ply_path)

        pcd_out = voxel_downsample(pcd, voxel_size)
        o3d.io.write_point_cloud(out_path, pcd_out, write_ascii=True)

def main():
    parser = argparse.ArgumentParser(description="Voxel downsample .ply files.")
    parser.add_argument("input_dir", type=str, help="Directory with input .ply files")
    parser.add_argument("output_dir", type=str, help="Directory to write downsampled .ply files")
    parser.add_argument("--factor", type=float, default=2.0, help="Downsampling factor (default=2.0)")
    args = parser.parse_args()

    if not os.path.exists(args.input_dir):
        parser.error(f"{args.input_dir} is not a valid directory.")

    process_directory(args.input_dir, args.output_dir, args.factor)

if __name__ == "__main__":
    main()
