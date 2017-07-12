from Queue import Queue
import thread
import math
import time

s1_times = []
s2_times = []
s3_times = []
s4_times = []

flag1 = 0
flag2 = 0
flag3 = 0
flag4 = 0

tan_1 = 0.1763269807
tan_2 = 1.19175359259

length_1 = 5
length_2 = 1
length_3 = 1
length_4 = 5

angle_1 = 100.0*(2.0*math.pi)/360.0
angle_2 = 140.0*(2.0*math.pi)/360.0
angle_3 = angle_2
angle_4 = angle_1

fov = 2.0*(2.0*math.pi)/360.0

CLIPPING = 0
d_low = 35
d_high = 45

def mean(numbers):
   return float(sum(numbers) / max(len(numbers), 1))
   
def velocity_estimate(avg_time_1, avg_time_2, avg_time_3, avg_time_4):
   global length_1, length_2, length_3, length_4, tan_1, tan_2, CLIPPING
   
   #center convergence equations
   time_difference_1_4 = abs(avg_time_4 - avg_time_1)
   time_difference_2_3 = abs(avg_time_3 - avg_time_2)
   
   if time_difference_1_4 != 0 and time_difference_2_3 != 0:
      equation_1_left = (length_1 + length_4)/time_difference_1_4
      equation_2_left = (length_2 + length_3)/time_difference_2_3
      equation_1_coefficient = (2*tan_1)/time_difference_1_4
      equation_2_coefficient = (2*tan_2)/time_difference_2_3
      difference_left = equation_1_left - equation_2_left
      difference_coefficient = equation_1_coefficient - equation_2_coefficient
      if difference_coefficient != 0:
         distance_estimate = abs(difference_left/difference_coefficient)
         if CLIPPING:
            if distance_estimate < d_low:
               distance_estimate = d_low
            elif distance_estimate > d_high:
               distance_estimate = d_high
         return (abs((length_1 + length_4 + 2*tan_1*distance_estimate)/(time_difference_1_4)), distance_estimate)
   #time differency of 0 or coefficient difference of 0
   return (-1, -1)
   
def width_estimate(velocity, distance, s1, s2, s3, s4):
   global angle_1, angle_2, angle_3, angle_4, fov
   
   #estimate width using the velocity estimate and the longest time the object was detected by one cone
   time_dif_1 = 0
   deltas = []
   cones = []
   if len(s1) > 1:
      time_dif_1 = s1[-1] - s1[0]
      deltas.append(time_dif_1)
    
   time_dif_2 = 0
   if len(s2) > 1:
      time_dif_2 = s2[-1] - s2[0]
      deltas.append(time_dif_2)
      
   time_dif_3 = 0
   if len(s3) > 1:
      time_dif_3 = s3[-1] - s3[0]
      deltas.append(time_dif_3)
      
   time_dif_4 = 0
   if len(s4) > 1:
      time_dif_4 = s4[-1] - s4[0]
      deltas.append(time_dif_4)
      
   #use the smallest sensor, least error introduced by FOV spread
   width_guess = 0
   if len(deltas) >= 1:
      return min(deltas)*velocity
   #if the object was detected at most one time, use the largest fov spread at this point
   elif width_guess == 0:
      s1 = abs(distance/math.tan(angle_1 + (fov/2)) - distance/math.tan(angle_1 - (fov/2)))
      cones.append(s1)
       
      s2 = abs(distance/math.tan(angle_2 + (fov/2)) - distance/math.tan(angle_2 - (fov/2)))
      cones.append(s2)
         
      s3 = abs(distance/math.tan(angle_3 + (fov/2)) - distance/math.tan(angle_3 - (fov/2)))
      cones.append(s3)
        
      s4 = abs(distance/math.tan(angle_4 + (fov/2)) - distance/math.tan(angle_4 - (fov/2)))
      cones.append(s4)
      return max(cones)
   
def estimate(fh, times_1, times_2, times_3, times_4):
   #each sensor detected intrusion
   if times_1 and times_2 and times_3 and times_4:
      (velocity, distance) = velocity_estimate(mean(times_1), mean(times_2), mean(times_3), mean(time_4))
      if velocity > 0:
         width = width_estimate(velocity, distance, times_1, times_2, times_3, times_4)
         date = time.gmtime()
         year = date.year
         month = date.tm_mon
         day = date.tm_mday
         hour = date.tm_hour
         minute = date.tm_min
         second = date.tm_second
         fh.write('Velocity ', velocity, ' width ', width, ' Distance ', distance)
         fh.write(' at time ' hour, ':', minute, ':', second, ' on ', month, '/', day, '/', year, '\n')
   
def estimator(q_s1, q_s2, q_s3, q_s4):
   #wait for a valid range of times
   #add timeouts to try 2 and 3 sensor estimation
   fh = open('log.txt')
   while (not flag1) and (not flag2) and (not flag3) and (not flag4):
      try:
         v1 = q_s1.get(False)
         #if the value is -1 the detection stream has stopped, else a valid time
         if v1 == -1:
            flag1 = 1
         else
            s1_times.append(v1)
      except Queue.Empty:
         pass
      
      try:
         v2 = q_s2.get(False)
         #if the value is -1 the detection stream has stopped, else a valid time
         if v2 == -1:
            flag2 = 1
         else
            s2_times.append(v2)
      except Queue.Empty:
         pass
      
      
      try:
         v3 = q_s3.get(False)
         #if the value is -1 the detection stream has stopped, else a valid time
         if v3 == -1:
            flag3 = 1
         else
            s3_times.append(v3)
      except Queue.Empty:
         pass
      
      
      try:
         v4 = q_s4.get(False)
         #if the value is -1 the detection stream has stopped, else a valid time
         if v4 == -1:
            flag4 = 1
         else
            s4_times.append(v4)
      except Queue.Empty:
         pass
   #times are gathered, do the estimation!
   #make copies of these arrays and spin off a thread for this?
   c1 = list(s1_times)
   c2 = list(s2_times)
   c3 = list(s3_times)
   c4 = list(s4_times)
   
   #clear old times
   s1_times = []
   s2_times = []
   s3_times = []
   s4_times = []
   
   estimate(fh, c1, c2, c3, c4)
   
   
   
      