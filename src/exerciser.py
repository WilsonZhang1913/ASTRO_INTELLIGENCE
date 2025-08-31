def sixth_func(x):
  for num in range(2,x):
    if x%num==0:
      return False
  return True
temp=999
while temp>0:
  if sixth_func(temp): 
    print(temp)
    break
  else: 
    temp=temp-1
      
print("no answer found")