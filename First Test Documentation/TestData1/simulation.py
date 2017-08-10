import numpy as np
import copy
import matplotlib.pyplot as plt
#approximate 2 degree FOV
start_x = 77
end_x = 82
#should the y boundaries create a square (117, 122) or a curtain (larger)???
start_y = 117
end_y = 122
#width of window
w = 6
#height of window
h = 6
#number of samples kept at a given time (use 32 or 64 for the bit shifting?)
d = 32 

magic_number = 0.6745
prev_values = np.zeros((4,6,6,32,3))#Matrix to hold previous values
medians = np.zeros((4,6,6))
means =  np.zeros((4,6,6))
alert_count = np.zeros((4,6,6, 153))
alert_total = np.zeros((4, 153))
trigger = np.zeros((4, 153))
median_array = np.zeros((32))

means = np.zeros((4, 6, 6, 153))
accountants = []
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
      if self.index >= d:
         if value > (self.mean + 6*self.std_dev):
            return 1
         elif value < (self.mean - 6*self.std_dev):
            return 1
      return 0
      
   def add_value(self, camera, value, time):
      if self.index == d:
         self.add_value_full(value, camera, time)
      else:
         self.add_value_filling(value, camera, time)

   def add_value_filling(self, value, camera, time):
      global k
      global means
      prev_values[camera][self.x][self.y][self.index][0] = value
      prev_values[camera][self.x][self.y][self.index][1] = self.index
      prev_values[camera][self.x][self.y][self.first][2] = time 
      for i in range(self.index, -1, -1):
         for j in range(self.index, -1, -1):
            if  prev_values[camera][self.x][self.y][i][0] < prev_values[camera][self.x][self.y][j][0]:
               temp = copy.copy(prev_values[camera][self.x][self.y][i])
               prev_values[camera][self.x][self.y][i] = prev_values[camera][self.x][self.y][j]
               prev_values[camera][self.x][self.y][j] = temp
               
      current_total = 0
      for i in range(self.index):
         current_total+= prev_values[camera][self.x][self.y][i][0]
         if prev_values[camera][self.x][self.y][i][1] == 0:
            self.first = i
      if self.index > 0:
         self.mean = current_total /self.index                #WOULD NEED UPDATING IF d CHANGES
      else:
         self.mean = value
      means[camera][self.x][self.y][k] = self.mean
      self.median = prev_values[camera][self.x][self.y][self.index/2][0]
      self.std_dev = self.calculate_MAD(camera)/magic_number
      self.index += 1
   
   def calculate_MAD(self, camera):
      for i in range(self.index):
         median_array[i] = abs(self.median - prev_values[camera][self.x][self.y][i][0])
      median_array.sort() 
      if median_array[self.index/2] == 0:
         return 1
      else:
         return median_array[self.index/2]
      
   def add_value_full(self, value, camera, time):
      global k
      global means
      #remove the oldest 
      r = self.first
      current_total = 0
      prev_values[camera][self.x][self.y][self.first][0] = value
      prev_values[camera][self.x][self.y][self.first][1] = 32  
      prev_values[camera][self.x][self.y][self.first][2] = time 
      #subtract one from each index
      for i in range(self.index-1, -1, -1):
         prev_values[camera][self.x][self.y][self.first][1] -= 1
      #sort the list
      for i in range(self.index-1, -1, -1):
         for j in range(self.index-1, -1, -1):
            
            if  prev_values[camera][self.x][self.y][i][0] < prev_values[camera][self.x][self.y][j][0]:
               temp = copy.copy(prev_values[camera][self.x][self.y][i])
               prev_values[camera][self.x][self.y][i] = prev_values[camera][self.x][self.y][j]
               prev_values[camera][self.x][self.y][j] = temp
      #update the stats
      current_total = 0
      for i in range(d):
         current_total+= prev_values[camera][self.x][self.y][i][0]
         if prev_values[camera][self.x][self.y][i][1] == 0:
            self.first = i
      self.mean = current_total / 32                #WOULD NEED UPDATING IF d CHANGES
      self.median = prev_values[camera][self.x][self.y][15][0]
      self.std_dev = self.calculate_MAD(camera)/magic_number
   
   def getIndex(self):
      return self.index

def add_sorted_all(i, j, camera,  value, time):
   global k
   if accountants[36*camera+j*w+i].test_value(value):
      alert_count[camera][i][j][k] += 1
      alert_total[camera][k] += 1
   accountants[36*camera+j*w+i].add_value(camera, value, time)

def add_sorted_good(i, j, camera,  value, time):
   global k
   if accountants[36*camera+j*w+i].test_value(value):
      alert_count[camera][i][j][k] += 1
      alert_total[camera][k] += 1
   if (accountants[36*camera+j*w+i].test_value(value) == 0) or (accountants[36*camera+j*w+i].getIndex() < d):
      accountants[36*camera+j*w+i].add_value(camera, value, time)
#declare accountants
for c in range(4):
   for x in range(0, w): 
         for y in range(0, h): 
            accountants.append(accountant(x, y))
            
with open('AllTestGood.txt') as f:
   lines = f.readlines()
   
Data = np.zeros((4,6,6,153))
Int = np.zeros((4, 153))
SimData = np.zeros((4, 6, 6, 32))
x = range(0, 153)
count = 0
index = 0
for line in lines:
   exploded = line.split(' ')
   if exploded[0] == 'Camera':
      camera = int(exploded[1])
      time = 0
      i = int(exploded[3])
      j = int(exploded[4])
      value = int(exploded[6])
      if len(exploded) > 8:
         mean = float(exploded[8])
         means[camera][i][j][index] = mean
      if len(exploded) > 13:
         time = exploded[13]
      #print camera, i, j, value
      #print , , , , stats float(exploded[8]), int(exploded[9]), float(exploded[10])
      Data[camera][i][j][index] = value
      
      count+=1
      if count == 36*4:
         index+= 1
         count = 0
   elif exploded[0] == 'INTRUSION':
      Int[int(exploded[1])][index] = 1
threshold = 30
for k in range(0, 153):
   #process the data frame by frame
   #print k
   for c in range(0, 4):
      for i in range(0, 6):
         for j in range(0, 6):
            add_sorted_good(i, j, c, Data[c][i][j][k], 0 )
   if alert_total[0][k] >= threshold:
      trigger[0][k] = 1#115
   else:
      trigger[0][k] = 0#-115
      
   if alert_total[1][k] >= threshold:
      trigger[1][k] = 1#110
   else:
      trigger[1][k] = 0#-110
      
   if alert_total[2][k] >= threshold:
      trigger[2][k] = 1#105
   else:
      trigger[2][k] = 0#-105
      
   if alert_total[3][k] >= threshold:
      trigger[3][k] = 1#100
   else:
      trigger[3][k] = 0#-100
   #print accountants[0].mean, accountants[0].std_dev
   #print prev_values[0][0][0]
   #print '\n'
#print Data[0][3][3]
plt.figure(1)
s = plt.subplot(221)
plt.plot(x, alert_total[0], 'r--')
plt.plot(x, alert_total[1], 'g--')
plt.plot(x, alert_total[2], 'b--')
plt.plot(x, alert_total[3], 'y--')
s.set_title('Number of pixels detected as changed per Sample')
s = plt.subplot(222)
plt.plot(x, trigger[0], 'r-')
plt.plot(x, trigger[1], 'go')
plt.plot(x, trigger[2], 'b-')
plt.plot(x, trigger[3], 'yo')
s.set_title('Simulation detection per Sample')
s = plt.subplot(223)
plt.plot(x, Data[0][3][3], 'r--')
plt.plot(x, Data[1][3][3], 'g--')
plt.plot(x, Data[2][3][3], 'b--')
plt.plot(x, Data[3][3][3], 'y--')
plt.plot(x, means[0][3][3], 'r')
plt.plot(x, means[1][3][3], 'g')
plt.plot(x, means[2][3][3], 'b')
plt.plot(x, means[3][3][3], 'y')
s.set_title('IR Data (--) and running average (-) per Sample')
s = plt.subplot(224)
plt.plot(x, Int[0], 'r')
plt.plot(x, Int[1], 'g')
plt.plot(x, Int[2], 'b')
plt.plot(x, Int[3], 'y')
s.set_title('Measured detection per Sample')
plt.show()
