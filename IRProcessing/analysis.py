import time
import thread
from Queue import Queue

#approximate 2 degree FOV
start_x = 77
end_x = 82
#should the y boundaries create a square (117, 122) or a curtain (larger)???
start_y = 117
end_y = 122
#width of window
w = end_x - start_x
#height of window
h = end_y - start_y
#number of samples kept at a given time (use 32 or 64 for the bit shifting?)
d = 32 
prev_values = [[[[0 for x in range(w)] 0 for y in range(h)] 0 for z in range(d)] 0 for v in range(2)]#Matrix to hold previous values
medians = [[0 for x in range(w)] 0 for y in range(h)]
means = [[0 for x in range(w)] 0 for y in range(h)]
#alert flag - 0 if no intrusion detected in previous frame, 1 if previous frame detected intrusion
alert_flag = 0
#global count of pixels with significant deviation
alert_count = 0
#Median Absolute Deviation magic number to get standard deviation
magic_number = 0.6745
#number of pixels in window that must be significantly different to add an intrusion time
threshold = 1 
#list of intrusion times
times = []
#list of accountant objects
accountants = []
'''
accountant class
-- keeps track of statistic data for a pixel (mean, median, std_dev)
-- updates statistical data for a pixel
-- tests incoming values against current pixel statistics
'''
class accountant:
   def __init__(self, x, y):
      self.x = x
      self.y = y
      #the index of the next value in the depth array to leave
      self.first = 0
      #count of number of samples processed (when filling buffer)
      self.index = 0
      #statistical data
      self.mean = 0
      self.median = 0
      self.std_dev = 0
      
   
   def test_value(self, value):
      if value > self.mean + 5*self.std_dev:
         return 1
      elif value < self.mean - 5*self.std_dev:
         return 1
      return 0
      
   def add_value(self, value):
      if self.index == d:
         self.add_value_full(value)
      else:
         self.add_value_filling(value)
      
   #fill the "order" buffer and the "prev_values" buffer in sequential order using the 
   #"accountant" class's "index" while also updating the mean and median values
   def add_value_filling(self, value):
      low = 0
      high = self.index
      mid = int((low + high) >> 1)
      while low != high:
         if value > prev_values[self.x][self.y][mid][0]:
            low = mid
            mid = int((low + high) >> 1)
         else
            high = mid
            mid = int((low + high) >> 1)
      #index found, add value
      #first shift existing values over to make room
      self.index += 1
      for j in range(self.index, (mid - 1), -1):
         prev_values[self.x][self.y][j][0] = prev_values[self.x][self.y][j-1][0]
         prev_values[self.x][self.y][j][1] = prev_values[self.x][self.y][j-1][1]
         #keep first pointing to the value with index of 0
         if prev_values[self.x][self.y][j][1] == 0: 
            self.first = j
      #next add value in location
      prev_values[self.x][self.y][mid][0] = value
      prev_values[self.x][self.y][mid][1] = self.index - 1
      #update the stats
      self.mean = (self.mean*self.index + value)/(self.index+1)
      self.median = prev_values[self.x][self.y][self.index>>1][0]
      self.std_dev = self.median/magic_number
   
   
   def add_value_full(self, value):
      #remove the oldest 
      r = self.first
      current_total = 0
      prev_values[self.x][self.y][j][self.first][0] = 0
      prev_values[self.x][self.y][j][self.first][1] = 31   
      #shift the rest of the values to low 30 indices
      for i in range(d-1):
         if i < r:
            current_total += prev_values[self.x][self.y][j][i][0]
            prev_values[self.x][self.y][j][i][1] -= 1
            if prev_values[self.x][self.y][j][i][1] == 0:
               self.first = i
         elif i > r:
            prev_values[self.x][self.y][j][i][0] = prev_values[self.x][self.y][j][i+1][0]
            current_total += prev_values[self.x][self.y][j][i][0]
            prev_values[self.x][self.y][j][i][1] -= 1
            if prev_values[self.x][self.y][j][i][1] == 0:
               self.first = i
      #binary sort the new value into position         
      low = 0
      high = d - 1
      mid = int((low + high) >> 1)
      while low != high:
         if value > prev_values[self.x][self.y][mid]:
            low = mid
            mid = int((low + high) >> 1)
         else
            high = mid
            mid = int((low + high) >> 1)
      #index found, add value
      #first shift existing values greater than new value over to make room
      for j in range(self.index, (mid-1), -1):
         prev_values[self.x][self.y][j][0] = prev_values[self.x][self.y][j-1][0]
         prev_values[self.x][self.y][j][1] = prev_values[self.x][self.y][j-1][1]
      #next add value in location
      prev_values[self.x][self.y][mid][0] = value
      prev_values[self.x][self.y][mid][1] = d - 1
      #update the stats
      self.mean = (current_total*31 + value) >> 5                 #WOULD NEED UPDATING IF d CHANGES
      self.median = prev_values[self.x][self.y][15][0]
      self.std_dev = self.median/magic_number


    
class coordinates:
   def __init__(self, index):
      self.x = index % 160
      self.y = index / 160

def add_sorted(index, value):
   global alert_count
   coords = coordinates(index)
   if accountants[coords.y*w+coords.x].test_value(value):
      alert_count += 1
   accountants[coords.y*w+coords.x].add_value(value)

def process_image(image_values, img_time):
   global alert_count, alert_flag
   alert_count = 0
   #skip unnecessary rows
   index_1 = 160*start_y + start_x #first pixel analyzed
   index_2 = 160*end_y + end_x     #last
   index = index_1
   while index < index_2:
      for i in range(0, w):
         add_sorted(index, image_values[index])
         index += 1
      index+= 160 - w
   #given there is sufficient deviation from the previous average, add the time to a list of detected intrusions
   if alert_count > threshold:
      q.put(img_time)
      alert_flag = 1
   else:
      if alert_flag == 1:
         q.put(-1)
      alert_flag = 0
      
def analyze(q, num):
   for x in range(0, w): 
      for y in range(0, h): 
         accountants.append(accountant(x, y))
   while 1:
      #GRAB IMAGE, USE NUM TO DETERMINE THE SENSOR
      img_time = time.clock()
      #turn data into 160x120 16 bit values
      process_image(image_values, q)
      time.sleep(0)
      


+    