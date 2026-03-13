from config import ALLOWED_EXTENSIONS
from config import INBOX_DIR

p = INBOX_DIR

def list_files(p):
    accept = []
    skip = []
    for item in p.iterdir():
            if not item.is_file():
                print("item not in file: {item.is_file()}\n")
                skip.append(item.name)
                continue
            
            if item.suffix.lower() in ALLOWED_EXTENSIONS:
                    
                    accept.append(item.name)
            else:
                    skip.append(item.name)
                    
    return accept,skip

if __name__=="__main__":
      acceptable,skippable = list_files(p)
      print(acceptable)
      print(skippable)
      
      

    

     

    


                    
                  
             



                
        
       



