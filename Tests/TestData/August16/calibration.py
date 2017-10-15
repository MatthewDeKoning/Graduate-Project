import numpy as np
import copy
import matplotlib.pyplot as plt
import math
import os



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

#geometric constants
length_1 = 3                                    #distances for the sensors on the X-axis from left to right
length_2 = 1
length_3 = 1
length_4 = 3

h_1 = 90                               #height of triangle made by sensor 1 and y axis
h_4 = 90
fov = 2.0*(2.0*math.pi)/360.0 

angle_1 = 100*(2.0*math.pi)/360.0     #angles toward y axis for each sensor
angle_2 = 130*(2.0*math.pi)/360.0
angle_3 = 130*(2.0*math.pi)/360.0
angle_4 = 100*(2.0*math.pi)/360.0

tan_1 = math.tan(angle_1)               #tangent values for each sensor angle
tan_2 = math.tan(angle_2)
tan_3 = math.tan(angle_3)
tan_4 = math.tan(angle_4)

#arrays to old detected times

files = ['R_30_cutoff_R.txt', 
'S_20_15_cutoff_R.txt', 
'S_20_20_cutoff_R.txt', 
'S_20_20_cutoff_R2.txt', 
'S_20_25_cutoff_R.txt', 
'S_20_30_cutoff_R.txt', 
'S_20_30_cutoff_R2.txt', 
'S_20_40_cutoff_R.txt', 
'T_20_20_cutoff_R.txt', 
'T_20_20_std_R.txt', 
'T_20_30_cutoff_R.txt', 
'T_20_30_std_R.txt',
'T_25_15_cutoff_R.txt', 
'T_25_15_std_R.txt', 
'T_25_25_cutoff_R.txt', 
'T_25_25_std_R.txt', 
'T_25_40_cutoff_R.txt', 
'T_25_40_std_R.txt', 
'T_30_20_cutoff_R.txt', 
'T_30_20_std_R.txt', 
'T_30_30_cutoff_R.txt']

        
for file in files:
    #actual_s = int(file.split("_")[2])
    #actual_d = int(file.split("_")[1])
    #print file, actual_s, actual_d
    with open(file) as f:
       lines = f.readlines()
    DataSize = len(lines) / (36*4) + 1
    magic_number = 0.6745
    prev_values = np.zeros((4,6,6,32,3))#Matrix to hold previous values
    medians = np.zeros((4,6,6))
    means_sim = np.zeros((4, 6, 6, DataSize))
    alert_count = np.zeros((4,6,6, DataSize))
    alert_total = np.zeros((4, DataSize))
    trigger = np.zeros((4, DataSize))
    sensor_1_times = []
    sensor_2_times = []
    sensor_3_times = []
    sensor_4_times = []
    median_array = np.zeros((32))
    temp = np.zeros(3)

    means = np.zeros((4, 6, 6, DataSize))
    accountants = []

    def average(numbers):
       return float(sum(numbers) / max(float(len(numbers)), 1.0))
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
          
       def test_range(self, value):
          if self.index >= d:
             if value > (self.mean + 30):
                return 1
             elif value < (self.mean - 30):
                return 1
          return 0
          
       def add_value(self, camera, value, time):
          if self.index == d:
             self.add_value_full(value, camera, time)
          else:
             self.add_value_filling(value, camera, time)

       def add_value_filling(self, value, camera, time):
          global k
          prev_values[camera][self.x][self.y][self.index][0] = value
          prev_values[camera][self.x][self.y][self.index][1] = self.index
          prev_values[camera][self.x][self.y][self.index][2] = time 
          
          for i in range(self.index, -1, -1):
             for j in range(self.index, -1, -1):
                if  prev_values[camera][self.x][self.y][i][0] < prev_values[camera][self.x][self.y][j][0]:
                   v = prev_values[camera][self.x][self.y][i][0]
                   p = prev_values[camera][self.x][self.y][i][1]
                   t = prev_values[camera][self.x][self.y][i][2]
                   prev_values[camera][self.x][self.y][i][0] = prev_values[camera][self.x][self.y][j][0]
                   prev_values[camera][self.x][self.y][i][1] = prev_values[camera][self.x][self.y][j][1]
                   prev_values[camera][self.x][self.y][i][2] = prev_values[camera][self.x][self.y][j][2]
                   prev_values[camera][self.x][self.y][j][0] = v
                   prev_values[camera][self.x][self.y][j][1] = p
                   prev_values[camera][self.x][self.y][j][2] = t
                   
          current_total = 0
          for i in range(self.index):
             current_total+= prev_values[camera][self.x][self.y][i][0]
             if prev_values[camera][self.x][self.y][i][1] == 0:
                self.first = i
          if self.index > 0:
             self.mean = current_total /self.index                #WOULD NEED UPDATING IF d CHANGES
          else:
             self.mean = value
          means_sim[camera][self.x][self.y][k] = self.mean
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
          if self.x == 3 and self.y == 3 and camera == 0:
            pass
          #subtract one from each index
          for i in range(self.index-1, -1, -1):
             prev_values[camera][self.x][self.y][i][1] -= 1
          #sort the list
          for i in range(self.index-1, -1, -1):
             for j in range(self.index-1, -1, -1):
                if  prev_values[camera][self.x][self.y][i][0] < prev_values[camera][self.x][self.y][j][0]:
                   v = prev_values[camera][self.x][self.y][i][0]
                   p = prev_values[camera][self.x][self.y][i][1]
                   t = prev_values[camera][self.x][self.y][i][2]
                   prev_values[camera][self.x][self.y][i][0] = prev_values[camera][self.x][self.y][j][0]
                   prev_values[camera][self.x][self.y][i][1] = prev_values[camera][self.x][self.y][j][1]
                   prev_values[camera][self.x][self.y][i][2] = prev_values[camera][self.x][self.y][j][2]
                   prev_values[camera][self.x][self.y][j][0] = v
                   prev_values[camera][self.x][self.y][j][1] = p
                   prev_values[camera][self.x][self.y][j][2] = t
          #update the stats
          current_total = 0
          for i in range(d):
             current_total+= prev_values[camera][self.x][self.y][i][0]
             if prev_values[camera][self.x][self.y][i][1] == 0:
                self.first = i
          self.mean = int(current_total / 32)                #WOULD NEED UPDATING IF d CHANGES
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
       if (accountants[36*camera+j*w+i].test_range(value) == 0) or (accountants[36*camera+j*w+i].getIndex() < d):
          accountants[36*camera+j*w+i].add_value(camera, value, time)
       means_sim[camera][accountants[36*camera+j*w+i].x][accountants[36*camera+j*w+i].y][k] = accountants[36*camera+j*w+i].mean
       
    def velocity_est():
          #center convergence equations
          global sensor_1_times
          global sensor_2_times
          global sensor_3_times
          global sensor_4_times 
          avg_time_1 = average(sensor_1_times) / 9.0
          avg_time_2 = average(sensor_2_times) / 9.0
          avg_time_3 = average(sensor_3_times) / 9.0
          avg_time_4 = average(sensor_4_times) / 9.0
          #print "measured times ", times[0][3][3][sensor_1_times[0]], times[1][3][3][sensor_2_times[0]], times[2][3][3][sensor_3_times[0]], times[3][3][3][sensor_4_times[0]] 
          print "Average times: ",avg_time_1, ', ', avg_time_2, ', ', avg_time_3, ', ', avg_time_4
          
          time_difference_1_4 = abs(avg_time_4 - avg_time_1)
          time_difference_2_3 = abs(avg_time_3 - avg_time_2)
          print "td14 ", time_difference_1_4, " td23 ", time_difference_2_3
          tan_1 = math.tan(angle_1 - math.pi/2)
          tan_2 = math.tan(angle_2 - math.pi/2)
          if time_difference_1_4 != 0 and time_difference_2_3 != 0:
             equation_1_left = abs((length_1 + length_4)/time_difference_1_4)
             equation_2_left = abs((length_2 + length_3)/time_difference_2_3)
             equation_1_coefficient = abs((2*tan_1)/time_difference_1_4)
             equation_2_coefficient = (2*tan_2)/time_difference_2_3
             difference_left = abs(equation_1_left - equation_2_left)
             difference_coefficient = abs(equation_1_coefficient - equation_2_coefficient)
             print "EQ1L ", equation_1_left, " EQ2L ", equation_2_left, " DIFL ", difference_left
             print "EQ1C ", equation_1_coefficient, " EQ2C ", equation_2_coefficient, " DIFC ",difference_coefficient
             if difference_coefficient != 0:
                distance_estimate = 1*abs(difference_left/difference_coefficient)
                velocity_estimate = 1*((length_2 + length_3 + 2*tan_2*distance_estimate)/(time_difference_2_3))
                return (distance_estimate, velocity_estimate)
                
                
    def estimate_width(velocity_est):
          #estimate width using the velocity estimate and the longest time the object was detected by one cone
          global sensor_1_times
          global sensor_2_times
          global sensor_3_times
          global sensor_4_times
          time_dif_1 = 0
          deltas = []
          cones = []
          if len(sensor_1_times) > 1:
             time_dif_1 = (sensor_1_times[-1] - sensor_1_times[0])/9.0
             deltas.append(time_dif_1)
          
          time_dif_2 = 0
          if len(sensor_2_times) > 1:
             time_dif_2 = (sensor_2_times[-1] - sensor_2_times[0])/9.0
             deltas.append(time_dif_2)
             
          time_dif_3 = 0
          if len(sensor_3_times) > 1:
             time_dif_3 = (sensor_3_times[-1] - sensor_3_times[0])/9.0
             deltas.append(time_dif_3)
             
          time_dif_4 = 0
          if len(sensor_4_times) > 1:
             time_dif_4 = (sensor_4_times[-1] - sensor_4_times[0])/9.0
             deltas.append(time_dif_4)
          
          #print deltas, ', ', self.velocity_estimate[i]
          #use the smallest sensor, least error introduced by FOV spread
          width_guess = 0
          if len(deltas) >= 1:
             width_guess = max(deltas)*velocity_est
             return width_guess
    #declare accountants
    for c in range(4):
       for x in range(0, w): 
             for y in range(0, h): 
                accountants.append(accountant(x, y))

       
    Data = np.zeros((4,6,6,DataSize))
    Int = np.zeros((4, DataSize))
    SimData = np.zeros((4, 6, 6, 32))
    alerts = np.zeros((4, 6, 6, DataSize))
    std = np.zeros((4, 6, 6, DataSize))
    alertCount = np.zeros((4, DataSize))

    times = np.zeros((4, 6, 6, DataSize))

    x = range(0, DataSize)
    count = 0
    index = 0
    for line in lines:
       exploded = line.split(' ')
       if exploded[0] == 'Camera':
          time = 0
          if len(exploded) > 14:
             camera = int(exploded[1])
             i = int(exploded[3])
             j = int(exploded[4])
             value = int(exploded[6])
             mean = float(exploded[8])
             means[camera][i][j][index] = mean
             times[camera][i][j][index] = int(exploded[13])
             alertCount[camera][index] += int(exploded[14])
             std[camera][i][j][index] = float(exploded[10])
             '''
             if camera == 3 and i == 0 and j == 0 and index > 0:
                print index, exploded[13], exploded[12], times[camera][i][j][index] - times[camera][i][j][index-1]
             '''
          #print camera, i, j, value
          #print , , , , stats float(exploded[8]), int(exploded[9]), float(exploded[10])
          Data[camera][i][j][index] = value
          
          count+=1
          if count == 36*4:
             index+= 1
             count = 0
       elif exploded[0] == 'INTRUSION':
          Int[int(exploded[1])][index] = 1
    threshold = 16

    for k in range(0, DataSize-1):
       #process the data frame by frame
       #print k
       for c in range(0, 4):
          for i in range(0, 6):
             for j in range(0, 6):
                add_sorted_good(i, j, c, Data[c][i][j][k], k )
       if alert_total[0][k] >= threshold:
          trigger[0][k] = 1#115
          sensor_1_times.append(k)
          #sensor_1_times.append(times[0][3][3][k])
       else:
          trigger[0][k] = 0#-115
          
       if alert_total[1][k] >= threshold:
          trigger[1][k] = 1#110
          sensor_2_times.append(k)
          #sensor_2_times.append(times[1][3][3][k])
       else:
          trigger[1][k] = 0#-110
          
       if alert_total[2][k] >= threshold:
          trigger[2][k] = 1#105
          sensor_3_times.append(k)
          #sensor_3_times.append(times[2][3][3][k])
       else:
          trigger[2][k] = 0#-105
          
       if alert_total[3][k] >= threshold:
          trigger[3][k] = 1#100
          sensor_4_times.append(k)
          #sensor_4_times.append(times[3][3][3][k])
       else:
          trigger[3][k] = 0#-100
          
    if len(sensor_1_times) > 1 and (abs(sensor_1_times[-1] - sensor_1_times[-2]) > 1):
        sensor_1_times = sensor_1_times[:-1]
    if len(sensor_2_times) > 1 and (abs(sensor_2_times[-1] - sensor_2_times[-2]) > 1):
        sensor_2_times = sensor_2_times[:-1]
    if len(sensor_3_times) > 1 and (abs(sensor_3_times[-1] - sensor_3_times[-2]) > 1):
        sensor_3_times = sensor_3_times[:-1]
    if len(sensor_4_times) > 1 and (abs(sensor_4_times[-1] - sensor_4_times[-2]) > 1):
        sensor_4_times = sensor_4_times[:-1]
        
    if len(sensor_1_times) > 0 and len(sensor_2_times) > 0 and len(sensor_3_times) > 0 and len(sensor_4_times) > 0:
        good_files.append(file)
        
        
        
print good_files
'''
   #print accountants[0].mean, accountants[0].std_dev
   #print prev_values[0][3][3]
   #print 'time: ' ,k
   #print '\n'
#print Data[0][3][3]
#sensor_4_times = sensor_4_times[:-1]
#fix times
if len(sensor_1_times) > 1 and (abs(sensor_1_times[-1] - sensor_1_times[-2]) > 1):
    sensor_1_times = sensor_1_times[:-1]
if len(sensor_2_times) > 1 and (abs(sensor_2_times[-1] - sensor_2_times[-2]) > 1):
    sensor_2_times = sensor_2_times[:-1]
if len(sensor_3_times) > 1 and (abs(sensor_3_times[-1] - sensor_3_times[-2]) > 1):
    sensor_3_times = sensor_3_times[:-1]
if len(sensor_4_times) > 1 and (abs(sensor_4_times[-1] - sensor_4_times[-2]) > 1):
    sensor_4_times = sensor_4_times[:-1]
   
sensor_3_times = sensor_3_times[:-1]
sensor_3_times = sensor_3_times[:-1]
sensor_4_times = sensor_4_times[:-1]
sensor_4_times = sensor_4_times[:-1]

    
print sensor_1_times
print sensor_2_times
print sensor_3_times
print sensor_4_times

#estimate velocity
(d, s) = velocity_est()
w = estimate_width(s)
s = s*0.681818 #convert to mph
print 'distance estimate: ', d, 'ft, speed estimate: ', s, 'mph, width estimate: ', w, ' ft'
print 'ratio distance: ', d/actual_d, ' ratio speed: ', s/actual_s, ' ratio width: ', w/17.0

plt.figure(1)
s = plt.subplot(221)
plt.plot(x, alert_total[0], 'r--')
plt.plot(x, alert_total[1], 'g--')
plt.plot(x, alert_total[2], 'b--')
plt.plot(x, alert_total[3], 'y--')
#plt.plot(x, alertCount[0], 'r')
#plt.plot(x, alertCount[1], 'g')
#plt.plot(x, alertCount[2], 'b')
#plt.plot(x, alertCount[3], 'y')
s.set_title('Number of pixels detected as changed per Sample')
s = plt.subplot(222)
plt.plot(x, std[0][3][3], 'r-')
plt.plot(x, std[1][3][3], 'g-')
plt.plot(x, std[2][3][3], 'b-')
plt.plot(x, std[3][3][3], 'y-')
s.set_title('Standard Deviation')
s = plt.subplot(223)

plt.plot(x, Data[0][3][3], 'r--')
plt.plot(x, Data[1][3][3], 'g--')
plt.plot(x, Data[2][3][3], 'b--')
plt.plot(x, Data[3][3][3], 'y--')
#plt.plot(x, means[0][3][3], 'r')
#plt.plot(x, means[1][3][3], 'g')
#plt.plot(x, means[2][3][3], 'b')
#plt.plot(x, means[3][3][3], 'y')
#plt.plot(x, means_sim[0][3][3], 'r^')
#plt.plot(x, means_sim[1][3][3], 'g^')
#plt.plot(x, means_sim[2][3][3], 'b^')
#plt.plot(x, means_sim[3][3][3], 'y^')
#plt.title('IR Data (--) and running average (-) per Sample')
    
#print prev_values[0][3][3]

s = plt.subplot(224)
#plt.plot(x, Int[0], 'r')
#plt.plot(x, Int[1], 'g')
#plt.plot(x, Int[2], 'b')
#plt.plot(x, Int[3], 'y')
plt.plot(x, trigger[0], 'r--')
plt.plot(x, trigger[1], 'g--')
plt.plot(x, trigger[2], 'b--')
plt.plot(x, trigger[3], 'y--')
s.set_title('Measured detection per Sample')

plt.show()
'''