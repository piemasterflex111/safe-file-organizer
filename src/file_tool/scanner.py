from config import ALLOWED_EXTENSIONS
from config import INBOX_DIR
from normalize import normalize_filename

def rename_files(INBOX_DIR):
    files = []
    for item in INBOX_DIR.iterdir():
            if not item.is_dir():
                 continue
            for sub_item in item.iterdir():
                if sub_item.is_file() and sub_item.suffix.lower() in ALLOWED_EXTENSIONS:
                    old_name = sub_item.name
                    new_name = normalize_filename(old_name)
                    if old_name == new_name:
                        continue
                    new_path = sub_item.with_name(new_name)
                    if new_path.exists():
                        continue    
                    new_path = sub_item.rename(new_path)
                    files.append((old_name, new_name))
            if item.suffix.lower() in ALLOWED_EXTENSIONS:        
                    old_name = item.name
                    new_name = normalize_filename(old_name)
                    if old_name == new_name:
                        continue
                    new_path = item.with_name(new_name)
                    if new_path.exists():
                        continue    
                    new_path = item.rename(new_path)
                    files.append((old_name, new_name))
    return files
if __name__ == "__main__":
    print(f"Scanning directory: {INBOX_DIR}")
    file_list = rename_files(INBOX_DIR)
    for item in file_list:
        print(f"OLD FILES: {item[0]}\nNEW FILES: {item[1]}\n")


      

      
      

    

     

    


                    
                  
             



                
        
       



