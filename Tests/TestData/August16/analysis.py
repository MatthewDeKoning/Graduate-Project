import numpy as np
import matplotlib.pyplot as plt

with open('outdoor3.txt') as f:
   lines = f.readlines()
DataSize = 400
Data = np.zeros((4,6,6,DataSize))
means = np.zeros((4, 6, 6, DataSize))
alert = np.zeros((4, 6, 6, DataSize))
ignored = np.zeros((4, 6, 6, DataSize))
std = np.zeros((4, 6, 6, DataSize))
x = range(0, DataSize)
count = 0
index = 0
for line in lines:
   exploded = line.split(' ')
   if exploded[0] == 'Camera':
      value = 0
      camera = int(exploded[1])
      if len(exploded) > 15:
         i = int(exploded[3])
         j = int(exploded[4])
         value = int(exploded[6])
         mean = float(exploded[8])
         std[camera][i][j][index] = float(exploded[10])
         means[camera][i][j][index] = mean
         alert[camera][i][j][index] = int(exploded[14])
         ignored[camera][i][j][index] = int(exploded[15])
      #print camera, i, j, value
      #print , , , , stats float(exploded[8]), int(exploded[9]), float(exploded[10])
         Data[camera][i][j][index] = value
      count+=1
      if count == 36*4:
         index+= 1
         count = 0
#print std[2][3][3] 
#print  alert[2][3][3]
plt.figure(1)
s = plt.subplot(221)      
plt.plot(x, Data[2][3][3], 'r--', x, means[2][3][3], 'r')
s.set_title('IR Data (--) and running average (-) per Sample')
s = plt.subplot(222)
plt.plot(x, alert[2][3][3]) 
s.set_title('Sample alert')
s = plt.subplot(223)
plt.plot(x, std[2][3][3])  
s.set_title('Standard Deviation') 
s = plt.subplot(224)
plt.plot(x, ignored[2][3][3])
s.set_title('Sample ignored (1) or added to running average (0)')
'''     
plt.plot(x, Data[2][0][0], '--', 
         x, Data[2][0][1], '--',
         x, Data[2][0][2], '--',
         x, Data[2][0][3], '--',
         x, Data[2][0][4], '--',
         x, Data[2][0][5], '--')
plt.plot(x, Data[2][1][0], '--', 
         x, Data[2][1][1], '--',
         x, Data[2][1][2], '--',
         x, Data[2][1][3], '--',
         x, Data[2][1][4], '--',
         x, Data[2][1][5], '--')
plt.plot(x, Data[2][2][0], '--', 
         x, Data[2][2][1], '--',
         x, Data[2][2][2], '--',
         x, Data[2][2][3], '--',
         x, Data[2][2][4], '--',
         x, Data[2][2][5], '--')
plt.plot(x, Data[2][3][0], '--', 
         x, Data[2][3][1], '--',
         x, Data[2][3][2], '--',
         x, Data[2][3][3], '--',
         x, Data[2][3][4], '--',
         x, Data[2][3][5], '--')
plt.plot(x, Data[2][4][0], '--', 
         x, Data[2][4][1], '--',
         x, Data[2][4][2], '--',
         x, Data[2][4][3], '--',
         x, Data[2][4][4], '--',
         x, Data[2][4][5], '--')
plt.plot(x, Data[2][5][0], '--', 
         x, Data[2][5][1], '--',
         x, Data[2][5][2], '--',
         x, Data[2][5][3], '--',
         x, Data[2][5][4], '--',
         x, Data[2][5][5], '--')
              
plt.plot(x, means[3][1][0], '--', 
         x, means[3][1][1], '--',
         x, means[3][1][2], '--',
         x, means[3][1][3], '--',
         x, means[3][1][4], '--',
         x, means[3][1][5], '--')
'''  
plt.show()
