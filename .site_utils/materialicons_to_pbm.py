"""
Convert Google's Material Icons SVG files to PBM
source files:  https://github.com/google/material-design-icons
"""
import os


src_dir = "/home/brad/gh2/material-design-icons/src"
dst_dir = "/home/brad/pbm/"

for root, dirs, files in os.walk(src_dir):
    for file in files:
        if file == "24px.svg":
            rel_path = os.path.relpath(root, src_dir)
            print(f"\nProcessing: {rel_path}")
            folders = rel_path.split("/")
            out_dir = folders[-1]
            suffix = out_dir.split("materialicons")[1]
            out_file_base = "-".join(folders[:-1])
            out_file = f"{out_file_base}{("-" + suffix) if suffix else ""}.pbm"
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_dir, out_dir, out_file)
            print(f"    output: {dst_file}")
            os.makedirs(os.path.join(dst_dir, out_dir), exist_ok=True)
            os.system(f"convert {src_file} {dst_file}")
            # os.system(f"rm {dst_file}.png")