import matplotlib.pyplot as plt

velocity = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
avg_err =  [12.129, 3.789, 2.081, 2.657, 1.33, 3.398, 1.635, 2.021, 2.373, 1.908, 3.178, 1.932, 2.205, 2.348, 2.381, 3.234, 2.416, 2.891, 2.706, 1.86, 2.756, 2.355, 2.816, 2.706, 1.596, 2.444, 2.033, 3.122, 2.568, 1.983, 2.464, 2.284, 3.184, 2.486, 2.247, 2.706, 2.164, 3.234, 2.416, 2.891, 2.706, 1.86, 2.756, 2.355, 2.816, 2.706, 1.596, 2.444, 2.033, 3.122]
max_err =  [23.0, 23.0, 3.577, 6.322, 3.577, 6.322, 3.083, 6.322, 6.322, 3.738, 6.322, 4.348, 6.322, 5.455, 4.92, 5.455, 5.455, 6.322, 5.455, 4.92, 5.455, 5.455, 6.322, 5.455, 2.993, 5.455, 4.92, 6.322, 5.455, 6.322, 5.455, 4.92, 4.88, 5.455, 6.322, 5.455, 4.92, 5.455, 5.455, 6.322, 5.455, 4.92, 5.455, 5.455, 6.322, 5.455, 2.993, 5.455, 4.92, 6.322]
min_err =  [1.622, 0.206, 1.182, 0.206, 0.206, 0.691, 0.206, 0.206, 0.206, 0.206, 0.691, 0.206, 0.206, 0.206, 0.206, 0.33, 0.206, 0.691, 0.206, 0.206, 0.33, 0.206, 0.33, 0.206, 0.206, 0.206, 0.206, 0.33, 0.206, 0.206, 0.206, 0.206, 0.33, 0.206, 0.206, 0.206, 0.206, 0.33, 0.206, 0.691, 0.206, 0.206, 0.33, 0.206, 0.33, 0.206, 0.206, 0.206, 0.206, 0.33]

#velocity = [x*0.681818 for x in velocity]
avg_err = [x*0.681818 for x in avg_err]
max_err = [x*0.681818 for x in max_err]
min_err = [x*0.681818 for x in min_err]
ten_percent = []
for v in velocity:
    ten_percent.append(0.1*15)
plt.figure(1)
avg = plt.plot(velocity, avg_err, 'b', label='average error')
max = plt.plot(velocity, max_err, 'r', label='max error')
min = plt.plot(velocity, min_err, 'g', label='min error')
tp = plt.plot(velocity, ten_percent, 'y--', label='10% error')
plt.xlabel('width in feet')
plt.ylabel('speed error of estimate, mph')
plt.title("Error vs Width\n Configuration 1, Distance 30, Speed 15 mph")
plt.legend()
plt.show();