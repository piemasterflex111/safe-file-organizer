from pathlib import Path
import csv

from .classifier import classify_name
from .categories import DESTINATIONS

ONEDRIVE_ROOT = Path(r"C:\Users\payam_vngz\OneDrive")
skipped = []
def build_move_plan(item: Path) -> list[dict]:
    rows = []
    if item.is_file():
            category_key = classify_name(item.name)
            destination_folder = ONEDRIVE_ROOT / DESTINATIONS[category_key]
            destination_path = destination_folder / item.name
            rows.append({
                "source_path" : str(item),
                "item_name" : item.name,
                "destination_bucket" : DESTINATIONS[category_key],
                "destination_path" : str(destination_path),
                "reason" : category_key,
                "status" : "PLANNED"
            })
    return rows

def walk_and_move_out_plan(root: Path) -> list[dict]:
      
      all_files = []
      for item in root.iterdir():
            if item.is_file():
                  file = build_move_plan(item)
                  all_files.extend(file)
            elif item.is_dir():
                  file_folder = walk_and_move_out_plan(item)
                  all_files.extend(file_folder)
            else:
                 skipped.append(item.name)
      return all_files        
            
def write_csv(rows: list[dict], out_path: Path) -> None:
    if not rows:
        return
    fieldname = list(rows[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldname)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    walking_dir = walk_and_move_out_plan(ONEDRIVE_ROOT)
    #print(f"Total planned rows: {len(walking_dir)}")
    write_csv(walking_dir, Path("move_plan.csv"))
    print("Wrote move_plan.csv")

    


    
    

    
