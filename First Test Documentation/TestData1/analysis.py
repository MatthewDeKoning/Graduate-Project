import numpy as np
import matplotlib.pyplot as plt

with open('AllTestGood.txt') as f:
   lines = f.readlines()

Data = np.zeros((4,6,6,153))
means = np.zeros((4, 6, 6, 153))
alert = np.zeros((4, 6, 6, 153))
std = np.zeros((4, 6, 6, 153))
x = range(0, 153)
count = 0
index = 0
for line in lines:
   exploded = line.split(' ')
   if exploded[0] == 'Camera':
      value = 0
      camera = int(exploded[1])
      if len(exploded) > 10:
         i = int(exploded[3])
         j = int(exploded[4])
         value = int(exploded[6])
         mean = float(exploded[8])
         std[camera][i][j][index] = float(exploded[10])
         means[camera][i][j][index] = mean
      #print camera, i, j, value
      #print , , , , stats float(exploded[8]), int(exploded[9]), float(exploded[10])
         Data[camera][i][j][index] = value
      count+=1
      if count == 36*4:
         index+= 1
         count = 0
print std[3][3][3]  
plt.figure(1)
#plt.subplot(221)      
plt.plot(x, Data[3][3][3], 'r--', x, means[3][3][3], 'r')
#plt.subplot(222)  
#plt.plot(x, alert[3][3][3])
'''         
plt.plot(x, Data[3][0][0], 'r--', 
         x, Data[3][0][1], 'g--',
         x, Data[3][0][2], 'b--',
         x, Data[3][0][3], 'm--',
         x, Data[3][0][4], 'c--',
         x, Data[3][0][5], '--')
plt.plot(x, means[3][1][0], 'r' 
         x, means[3][1][1], 'g',
         x, means[3][1][2], 'b',
         x, means[3][1][3], 'm',
         x, means[3][1][4], 'c',
         x, means[3][1][5], '')

plt.plot(x, Data[3][1][0], '--', 
         x, Data[3][1][1], '--',
         x, Data[3][1][2], '--',
         x, Data[3][1][3], '--',
         x, Data[3][1][4], '--',
         x, Data[3][1][5], '--')
plt.plot(x, Data[3][2][0], '--', 
         x, Data[3][2][1], '--',
         x, Data[3][2][2], '--',
         x, Data[3][2][3], '--',
         x, Data[3][2][4], '--',
         x, Data[3][2][5], '--')
plt.plot(x, Data[3][3][0], '--', 
         x, Data[3][3][1], '--',
         x, Data[3][3][2], '--',
         x, Data[3][3][3], '--',
         x, Data[3][3][4], '--',
         x, Data[3][3][5], '--')
plt.plot(x, Data[3][4][0], '--', 
         x, Data[3][4][1], '--',
         x, Data[3][4][2], '--',
         x, Data[3][4][3], '--',
         x, Data[3][4][4], '--',
         x, Data[3][4][5], '--')
plt.plot(x, Data[3][5][0], '--', 
         x, Data[3][5][1], '--',
         x, Data[3][5][2], '--',
         x, Data[3][5][3], '--',
         x, Data[3][5][4], '--',
         x, Data[3][5][5], '--')
'''
         
plt.show()
