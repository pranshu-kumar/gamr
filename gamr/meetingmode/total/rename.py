import os

for i in range(898,2227):
    
    prev_name=str(i)+'.txt'
    new_name=str((i-1))+'.txt' 
    
    os.rename(prev_name,new_name)
