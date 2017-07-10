from Tkinter import *
fh = open("OUTPUT.txt", 'r')

nums = []
max = -1
min = 5000
for i in range(0, 19200):
   print i
   line = fh.readline()
   
   line_parts = line.split('.')
   line_parts[1].rstrip()
   num = (int(line_parts[1], 16) <<8) + int(line_parts[0], 16)
   nums.append(num)
   if num > max:
      max = num
   if num < min:
      min = num
      
print "Max: ", max, "Min: ", min

master = Tk()

main_canvas = Canvas(master, width=160*6, height=120*6)
main_canvas.pack()
x = 0
y = 0
for num in nums:
   eight_bit = int((num - min) / float(((max-min)))*255)
   #print (num-min), ', ', (max-min), ', ', eight_bit
   color = "#%02x%02x%02x" % (eight_bit, eight_bit, eight_bit)
   main_canvas.create_rectangle(6*x, 6*y , 6*x+6 , 6*y+6 , fill=color)
   x += 1
   if x == 160:
      x = 0
      y += 1
   

   
master.mainloop() 