from config import ALLOWED_EXTENSIONS
from config import INBOX_DIR
from normalize_script import normalize_filename

def rename_files(INBOX_DIR):
    files = []
    for item in INBOX_DIR.iterdir():
            if not item.is_file():
                continue
            if item.suffix.lower() in ALLOWED_EXTENSIONS:        
                    old_name = item.name
                    new_name = normalize_filename(old_name)
                    if old_name == new_name:
                        continue
                    new_path = item.with_name(new_name)
                    if new_path.exists():
                        continue    
                    new_path = item.rename(new_path)
                    print(f"Renamed: {old_name} -> {new_name}")
                    files.append((old_name, new_name))             
    return files
if __name__ == "__main__":
    file_list = rename_files(INBOX_DIR)
    for item in file_list:
        print(f"OLD FILES: {item[0]}\nNEW FILES: {item[1]}\n")


      

      
      

    

     

    


                    
                  
             



                
        
       



