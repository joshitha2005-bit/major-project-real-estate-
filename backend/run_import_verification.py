import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.services.dataset_import_service import DatasetImportService
from app.models.property import Property

def run_import():
    # Ensure backend/datasets directory exists and has housing.csv
    base_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(base_dir, "datasets")
    archive_dir = os.path.join(base_dir, "archive")
    os.makedirs(datasets_dir, exist_ok=True)
    
    src_csv = os.path.join(archive_dir, "housing.csv")
    dst_csv = os.path.join(datasets_dir, "housing.csv")
    if os.path.exists(src_csv) and not os.path.exists(dst_csv):
        shutil.copy(src_csv, dst_csv)
        print(f"Copied {src_csv} to {dst_csv}")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Import datasets
    result = DatasetImportService.import_datasets(db, max_records_per_file=500)
    
    db.close()

if __name__ == "__main__":
    run_import()
