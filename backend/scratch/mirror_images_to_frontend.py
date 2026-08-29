import shutil
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_dir = os.path.join(backend_dir, "static", "property-images")

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
dst_dir = os.path.join(frontend_dir, "public", "property-images")

if os.path.exists(dst_dir):
    shutil.rmtree(dst_dir)

shutil.copytree(src_dir, dst_dir)
print(f"Successfully mirrored dataset to {dst_dir}")
