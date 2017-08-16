import copy
import random
import numpy as np

array = np.zeros((10,2))

def add(value, index):
   low = 0
   high = index
   mid = int((low + high) >> 1)
   while (low - high) > 1:
      #print low, high
      if value > array[mid]:
         low = mid
         mid = int((low + high) >> 1)
      else:
         high = mid
         mid = int((low + high) >> 1)
    
   return mid

def add_value(value, index):
   global array
   array[index][0] = value
   array[index][1] = index
   print value
   for i in range(index, -1, -1):
      for j in range(index, -1, -1):
         if array[j][0] < array[i][0]:
            temp = copy.copy(array[j])
            array[j] = array[i]
            array[i] = temp
   
for k in range(10):
   add_value(random.randint(0, 100), k)
   print array



         
