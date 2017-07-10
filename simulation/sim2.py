import random
import math
import time
from Tkinter import *
import tkSimpleDialog
from fractions import Fraction
import thread
import processSim

#add an internal loop with incremental changes in start positions to show range for each test scenario

#set up default simulation parameters
length_1 = 10                                    #distances for the sensors on the X-axis from left to right
length_2 = 5
length_3 = 5
length_4 = 10
padding = 10                            #padding in x direction before sensor 1 is encountered

h_1 = 100                               #height of triangle made by sensor 1 and y axis
h_4 = 100
fov = 2.0*(2.0*math.pi)/360.0          #field of view (radians)

angle_1 = math.atan(h_1/length_1)       #angles toward y axis for each sensor
angle_2 = 88.0*(2.0*math.pi)/360.0
angle_3 = 88.0*(2.0*math.pi)/360.0
angle_4 = math.atan(h_4/length_4)


tan_1 = math.tan(angle_1)               #tangent values for each sensor angle
tan_2 = math.tan(angle_2)
tan_3 = math.tan(angle_3)
tan_4 = math.tan(angle_4)

h_3 = length_3*tan_3                    #height of triangle made by sensor 2
h_2 = length_4*tan_4
v_low = 10
v_high = 11
w_low = 5
w_high = 6
d_low = 15
d_high = 16
v_step = 1
d_step = 1
w_step = 1
NOISE_ENABLED = 0
LOG_ENABLED = 0
ANIMATION_ENABLED = 0
FPS_NUM = 9
file="sim.txt"
#The starting Dialogue
class MyDialog(tkSimpleDialog.Dialog):

    def body(self, master):
        #lengths
        Label(master, text="Length 1 (ft):").grid(row=0, sticky = 'e')
        Label(master, text="Length 2:").grid(row=1, sticky = 'e')
        Label(master, text="Length 3:").grid(row=2, sticky = 'e')
        Label(master, text="Length 4:").grid(row=3, sticky = 'e')

        self.L1 = Entry(master)
        self.L1.insert(END, '5')
        self.L2 = Entry(master)
        self.L2.insert(END, '1')
        self.L3 = Entry(master)
        self.L3.insert(END, '1')
        self.L4 = Entry(master)
        self.L4.insert(END, '5')

        self.L1.grid(row=0, column=1)
        self.L2.grid(row=1, column=1)
        self.L3.grid(row=2, column=1)
        self.L4.grid(row=3, column=1)
        
        #middle sensor angles
        Label(master, text="Angle 1/4 (deg):").grid(row=4, sticky = 'e')
        Label(master, text="Angle 2/3:").grid(row=5, sticky = 'e')
        Label(master, text="FOV (deg):").grid(row=6, sticky = 'e')
        
        self.A2 = Entry(master)
        self.A2.insert(END, 100)
        self.A3 = Entry(master)
        self.A3.insert(END, 140)
        self.FOV = Entry(master)
        self.FOV.insert(END, 2.0)
        
        self.A2.grid(row=4, column=1)
        self.A3.grid(row=5, column=1)
        self.FOV.grid(row=6, column=1)
        
        Label(master, text="Distance (min, max, step):").grid(row=7, sticky = 'e')
        Label(master, text="Velocity (min, max, step):").grid(row=8, sticky = 'e')
        Label(master, text="Width (min, max, step):").grid(row=9, sticky = 'e')
        Label(master, text="FPS:").grid(row=10, sticky='e')
        
        self.D1 = Entry(master)
        self.D1.insert(END, 20)
        self.D2 = Entry(master)
        self.D2.insert(END, 30)
        self.D3 = Entry(master)
        self.D3.insert(END, 1)
        self.V1 = Entry(master)
        self.V1.insert(END, 10)
        self.V2 = Entry(master)
        self.V2.insert(END, 58)
        self.V3 = Entry(master)
        self.V3.insert(END, 1)
        self.W1 = Entry(master)
        self.W1.insert(END, 1)
        self.W2 = Entry(master)
        self.W2.insert(END, 1)
        self.W3 = Entry(master)
        self.W3.insert(END, 1)
        self.FPS = Entry(master)
        self.FPS.insert(END, 60) #unlocked FLIR MUON
        
        self.D1.grid(row=7, column = 1)
        self.D2.grid(row=7, column = 2)
        self.D3.grid(row=7, column = 3)
        self.V1.grid(row=8, column = 1)
        self.V2.grid(row=8, column = 2)
        self.V3.grid(row=8, column = 3)
        self.W1.grid(row=9, column = 1)
        self.W2.grid(row=9, column = 2)
        self.W3.grid(row=9, column = 3)
        self.FPS.grid(row=10, column = 1)
        Label(master, text="Log file: ").grid(row=11, sticky = 'e')
        
        self.File = Entry(master)
        self.File.grid(row=11, column=1)
        self.File.insert(END, "V.txt")
        
        self.noise = IntVar()
        self.animation = IntVar()
        self.log = IntVar()
        self.log.set(1)
        self.CNoise = Checkbutton(master, text="Enable Noise", variable=self.noise)
        self.CNoise.grid(row = 12, column = 0, sticky = 'w')
        self.CAnimation = Checkbutton(master, text="Enable Animation", variable=self.animation)
        self.CAnimation.grid(row = 13, column = 0, sticky = 'w')
        self.CLog = Checkbutton(master, text="Enable Logging", variable=self.log)
        self.CLog.grid(row = 14, column = 0, sticky = 'w')
        
        #master.lift()
        
        return self.L1 # initial focus

    def apply(self):
      global length_1, length_2, length_3, length_4
      global angle_1, angle_2, angle_3, angle_4
      global tan_1, tan_2, tan_3, tan_4
      global h_3, h_2, fov
      global v_low, v_high, w_low, w_high, d_low, d_high
      global v_step, h_step, d_step, NOISE_ENABLED, ANIMATION_ENABLED, LOG_ENABLED, file, FPS_NUM, frame_time
      length_1 = float(self.L1.get())                                 #distances for the sensors on the X-axis from left to right
      length_2 = float(self.L2.get()) 
      length_3 = float(self.L3.get()) 
      length_4 = float(self.L4.get()) 
      
      fov = float(self.FOV.get())*(2.0*math.pi)/360.0          #field of view (radians)

      angle_1 = float(self.A2.get())*(2.0*math.pi)/360.0       #angles toward y axis for each sensor
      angle_2 = float(self.A3.get())*(2.0*math.pi)/360.0
      angle_3 = float(self.A3.get())*(2.0*math.pi)/360.0
      angle_4 = float(self.A2.get())*(2.0*math.pi)/360.0


      tan_1 = math.tan(angle_1)               #tangent values for each sensor angle
      tan_2 = math.tan(angle_2)
      tan_3 = math.tan(angle_3)
      tan_4 = math.tan(angle_4)

      h_3 = length_3*tan_3                    #height of triangle made by sensor 2
      h_2 = length_4*tan_4
      
      v_low = int(self.V1.get())
      v_high = int(self.V2.get())
      v_step = int(self.V3.get())
      w_low = int(self.W1.get())
      w_high = int(self.W2.get())
      w_step = int(self.W3.get())
      d_low = int(self.D1.get())
      d_high = int(self.D2.get())
      d_step = int(self.D3.get())
      
      NOISE_ENABLED = int(self.noise.get())
      LOG_ENABLED = int(self.log.get())
      ANIMATION_ENABLED = int(self.animation.get())
      
      FPS_NUM = int(self.FPS.get())
      frame_time = get_fps_float(FPS_NUM)
      file = self.File.get()
      print 'Simulation Starting'
      

#set up the GUI
####################################################################################################################

master = Tk()
master.withdraw()
main_canvas = None
#x locations of the sensors
s1_x = 0
s2_x = 0
s3_x = 0
s4_x = 0
#7 pixles per foot
ppf = 4
x_axis_y = 0
def quit():
   master.quit()
def create_gui(master):
   global main_canvas
   global s1_x, s2_x, s3_x, s4_x
   global x_axis_y
   global length_1, length_2, length_3, length_4
   global angle_1, angle_2, angle_3, angle_4
   global tan_1, tan_2, tan_3, tan_4
   global h_3, h_2, fov
   global v_low, v_high, w_low, w_high, d_low, d_high
   global v_step, h_step, d_step
   
   master.deiconify()
   
   menubar = Menu(master)
   menubar.add_command(label="Exit", command=quit)
   master.config(menu=menubar)
   
   canvas_width = 800
   canvas_height = 800

   x_axis_y = 750
   y_axis_x = canvas_width/2
   
   main_canvas = Canvas(master, width=canvas_width, height=canvas_height)
  
   main_canvas.pack()
   main_canvas.create_line(75, x_axis_y, 725, x_axis_y)
   main_canvas.create_line(y_axis_x, x_axis_y, y_axis_x, (x_axis_y - 100*ppf))
   #draw the sensors
   s1_x = canvas_width/2- ppf*length_1
   s2_x = canvas_width/2 - ppf*length_2
   s3_x = canvas_width/2 + ppf*length_3
   s4_x = canvas_width/2 + ppf*length_4 
   canvas_widgets = []
   canvas_widgets.append(main_canvas.create_line(s1_x, x_axis_y + 2, s1_x, x_axis_y - 2))
   canvas_widgets.append(main_canvas.create_line(s2_x, x_axis_y + 2, s2_x, x_axis_y - 2))
   canvas_widgets.append(main_canvas.create_line(s3_x, x_axis_y + 2, s3_x, x_axis_y - 2))
   canvas_widgets.append(main_canvas.create_line(s4_x, x_axis_y + 2, s4_x, x_axis_y - 2))

   #draw the fov lines
   s1_dx1 = s1_x + ppf*(100/math.tan(angle_1 - fov/2))
   s1_dx2 = s1_x + ppf*(100/math.tan(angle_1 + fov/2))
   s1_ideal = s1_x + ppf*(100/math.tan(angle_1))
   canvas_widgets.append(main_canvas.create_line(s1_x, x_axis_y, s1_dx1, (x_axis_y - 100*ppf), fill="orange"))
   canvas_widgets.append(main_canvas.create_line(s1_x, x_axis_y, s1_dx2, (x_axis_y - 100*ppf), fill="orange"))
   canvas_widgets.append(main_canvas.create_line(s1_x, x_axis_y, s1_ideal, (x_axis_y - 100*ppf), fill='gray80', dash =(2,6)))

   s2_dx1 = s2_x + ppf*(100/math.tan(angle_2 - fov/2))
   s2_dx2 = s2_x + ppf*(100/math.tan(angle_2 + fov/2))
   s2_ideal = s2_x + ppf*(100/math.tan(angle_2))
   canvas_widgets.append(main_canvas.create_line(s2_x, x_axis_y, s2_dx1, (x_axis_y - 100*ppf), fill="blue"))
   canvas_widgets.append(main_canvas.create_line(s2_x, x_axis_y, s2_dx2, (x_axis_y - 100*ppf), fill="blue"))
   canvas_widgets.append(main_canvas.create_line(s2_x, x_axis_y, s2_ideal, (x_axis_y - 100*ppf), fill='gray80', dash =(2,6)))

   s3_dx1 = s3_x - ppf*(100/math.tan(angle_3 - fov/2))
   s3_dx2 = s3_x - ppf*(100/math.tan(angle_3 + fov/2))
   s3_ideal = s3_x - ppf*(100/math.tan(angle_3))
   canvas_widgets.append(main_canvas.create_line(s3_x, x_axis_y, s3_dx1, (x_axis_y - 100*ppf), fill="green"))
   canvas_widgets.append(main_canvas.create_line(s3_x, x_axis_y, s3_dx2, (x_axis_y - 100*ppf), fill="green"))
   canvas_widgets.append(main_canvas.create_line(s3_x, x_axis_y, s3_ideal, (x_axis_y - 100*ppf), fill='gray80', dash =(2,6)))

   s4_dx1 = s4_x - ppf*(100/math.tan(angle_4 - fov/2))
   s4_dx2 = s4_x - ppf*(100/math.tan(angle_4 + fov/2))
   s4_ideal = s4_x - ppf*(100/math.tan(angle_4))
   canvas_widgets.append(main_canvas.create_line(s4_x, x_axis_y, s4_dx1, (x_axis_y - 100*ppf), fill="purple"))
   canvas_widgets.append(main_canvas.create_line(s4_x, x_axis_y, s4_dx2, (x_axis_y - 100*ppf), fill="purple"))
   canvas_widgets.append(main_canvas.create_line(s4_x, x_axis_y, s4_ideal, (x_axis_y - 100*ppf), fill='gray80', dash =(2,6)))
   canvas_widgets.append(main_canvas.create_text(50, 18, font="Times 10 underline", text="Simulation Parameters", anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 35, font="Times 10", text="L1: "+str(length_1)+" ft", anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 50, font="Times 10", text="L2: "+str(length_2)+" ft", anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 65, font="Times 10", text="L3: "+str(length_3)+" ft", anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 80, font="Times 10", text="L4: "+str(length_4)+" ft", anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 95, font="Times 10", text="A1: "+str(round(angle_1*360 / (2.0*math.pi), 3))+" degrees", anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 110, font="Times 10", text="A2: "+str(round(angle_2*360 / (2.0*math.pi), 3))+" degrees", anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 125, font="Times 10", text="A3: "+str(round(angle_3*360 / (2.0*math.pi), 3))+" degrees", anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 140, font="Times 10", text="A4: "+str(round(angle_4*360 / (2.0*math.pi), 3))+" degrees", anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 155, font="Times 10", text="Distance (ft): "+str(d_low) + "-"+str(d_high)+ " step "+str(d_step), anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 170, font="Times 10", text="Velocity (ft/s): "+str(v_low) + "-"+str(v_high)+ " step "+str(v_step), anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 185, font="Times 10", text="Width (ft): "+str(w_low) + "-"+str(w_high)+ " step "+str(w_step), anchor=W))
   canvas_widgets.append(main_canvas.create_text(50, 200, font="Times 10", text="FPS: "+str(FPS_NUM), anchor=W))
   thread.start_new_thread(test_func, (main_canvas, master))   
   master.mainloop() 



####################################################################################################################
#global functions

def get_fps_float(num):
   f = Fraction(int(round(1)), num)
   return float(f.numerator)/float(f.denominator)

def get_ninth(num):
   f = Fraction(int(round(num)), 9)
   return float(f.numerator)/float(f.denominator)
   
frame_time = get_fps_float(FPS_NUM)

def mean(numbers):
   return float(sum(numbers) / max(len(numbers), 1))
   
def convert_to_pixel(number):
   return 400 + ppf*number
#test object class
class test_obj:
   def __init__(self, canvas, dist, vel, wid):
      self.canvas = canvas
      self.distance = dist             #y value
      self.velocity = vel              #speed of the object
      self.width = wid                 #object width (in x direction)
      self.crossing_width = 2*length_1 - 2*(self.distance/tan_1)   #distance the object is within the sensor region (not taking into account sensor cones)
      self.canvas_cones = []
      self.velocity_estimate = []
      self.width_estimate = []
      self.sensor_misses = 0
      if angle_1 < (math.pi / 2):
        self.assign_cones_scenario_1()
      else:
        self.assign_cones_scenario_2()
        
      self.assign_times()
      
      
   #ADD ASSIGN CONES FOR SCENARIO 2   
   def assign_cones_scenario_1(self):
      global s1_x, s2_x, s3_x, s4_x, NOISE_ENABLED
      dist_square = self.distance*self.distance 
      #pythagorean theorem to get distances at which sensors detects object
      dist_1 = (dist_square + length_1*length_1)**(1/2.0)
      dist_2 = (dist_square + length_2*length_2)**(1/2.0)
      dist_3 = (dist_square + length_3*length_3)**(1/2.0)
      dist_4 = (dist_square + length_4*length_4)**(1/2.0)
      
      self.sensor_misses = 0
      
      #the spread of the sensor cone at distance given fov
      cone_width = 2.0*dist_1*math.sin(fov/2.0)
      self.cone_width_1 = cone_width
      
      #the x values for detection
      self.sensor_1_x1 = padding + self.distance/math.tan(angle_1 + (fov/2))
      self.sensor_1_x2 = padding + self.distance/math.tan(angle_1 - (fov/2))
      
      #determining the noise in the detection cone
      distance = self.sensor_1_x2 - self.sensor_1_x1
      print self.sensor_1_x1 , ', ', self.sensor_1_x2
      if(NOISE_ENABLED == 1):
         #the point of detection within this cone (exponential distribution - adjust number, currently ~1% miss, mean is 1/4 of cone)
         delay_1 = random.expovariate(6/distance)
         #the point the cameras no longer detect the object
         delay_2 = random.expovariate(6/distance)
      else:
         delay_1 = 0
         delay_2 = 0
         
      #adding in the noise 
      self.sensor_1_x1 += delay_1
      self.sensor_1_x2 -= delay_2
      
      #if x1 is now greater than x2, consider it a miss
      if self.sensor_1_x1 > self.sensor_1_x2:
         self.sensor_1_x1 = -1
         self.sensor_1_x2 = 100
         self.sensor_misses += 1
      else:
         #update the GUI
         self.canvas_cones.append(self.canvas.create_line(int(s1_x + (self.distance/math.tan(angle_1 + (fov/2)))*ppf + delay_1*ppf), int(x_axis_y - self.distance*ppf), int(s1_x + (self.distance/math.tan(angle_1 - (fov/2)))*ppf - delay_2*ppf), int(x_axis_y - self.distance*ppf), fill='red'))
       
      
      #repeat for sensors 2
      cone_width = 2.0*dist_2*math.sin(fov/2.0)
      self.cone_width_2 = cone_width
      self.sensor_2_x1 = padding + (length_1 - length_2) + self.distance/math.tan(angle_2 + (fov/2))
      self.sensor_2_x2 = padding + (length_1 - length_2) + self.distance/math.tan(angle_2 - (fov/2))
      distance = self.sensor_2_x2 - self.sensor_2_x1
      if(NOISE_ENABLED == 1):
         #the point of detection within this cone (exponential distribution - adjust number, currently ~1% miss, mean is 1/4 of cone)
         delay_1 = random.expovariate(6/distance)
         #the point the cameras no longer detect the object
         delay_2 = random.expovariate(6/distance)
      else:
         delay_1 = 0
         delay_2 = 0
      self.sensor_2_x1 += delay_1
      self.sensor_2_x2 -= delay_2
      if self.sensor_2_x1 > self.sensor_2_x2:
         self.sensor_2_x1 = -1
         self.sensor_2_x2 = 100
         self.sensor_misses += 1
      else:
         #update the GUI
         self.canvas_cones.append(self.canvas.create_line(int(s2_x + (self.distance/math.tan(angle_2 + (fov/2)))*ppf + delay_1*ppf), int(x_axis_y - self.distance*ppf), int(s2_x + (self.distance/math.tan(angle_2 - (fov/2)))*ppf - delay_1*ppf), int(x_axis_y - self.distance*ppf), fill='red'))
         
      
      #repeat for sensor 3
      cone_width = 2.0*dist_3*math.sin(fov/2.0)
      self.cone_width_3 = cone_width
      self.sensor_3_x1 = (padding + length_1 + length_3) - self.distance/math.tan(angle_3 - (fov/2))
      self.sensor_3_x2 = (padding + length_1 + length_3) - self.distance/math.tan(angle_3 + (fov/2))
      distance = self.sensor_3_x2 - self.sensor_3_x1
      if(NOISE_ENABLED == 1):
         #the point of detection within this cone (exponential distribution - adjust number, currently ~1% miss, mean is 1/4 of cone)
         delay_1 = random.expovariate(6/distance)
         #the point the cameras no longer detect the object
         delay_2 = random.expovariate(6/distance)
      else:
         delay_1 = 0
         delay_2 = 0
      self.sensor_3_x1 += delay_1
      self.sensor_3_x2 -= delay_2
      if self.sensor_3_x1 > self.sensor_3_x2:
         self.sensor_3_x1 = -1
         self.sensor_3_x2 = 100
         self.sensor_misses += 1
      else:
         #update GUI
         self.canvas_cones.append(self.canvas.create_line(int(s3_x - (self.distance/math.tan(angle_3 + (fov/2)))*ppf + delay_1*ppf), int(x_axis_y - self.distance*ppf), int(s3_x - (self.distance/math.tan(angle_3 - (fov/2)))*ppf - delay_1*ppf), int(x_axis_y - self.distance*ppf), fill='red'))
      
      #repeat for sensor 4
      cone_width = 2.0*dist_4*math.sin(fov/2.0)
      self.cone_width_4 = cone_width
      self.sensor_4_x1 = (padding + length_1 + length_4) - self.distance/math.tan(angle_4 - (fov/2))
      self.sensor_4_x2 = (padding + length_1 + length_4) - self.distance/math.tan(angle_4 + (fov/2))
      distance = self.sensor_2_x2 - self.sensor_2_x1
      if(NOISE_ENABLED == 1):
         #the point of detection within this cone (exponential distribution - adjust number, currently ~1% miss, mean is 1/4 of cone)
         delay_1 = random.expovariate(6/distance)
         #the point the cameras no longer detect the object
         delay_2 = random.expovariate(6/distance)
      else:
         delay_1 = 0
         delay_2 = 0   
      self.sensor_2_x1 += delay_1
      self.sensor_2_x2 -= delay_2
      if self.sensor_4_x1 > self.sensor_4_x2:
         self.sensor_4_x1 = -1
         self.sensor_4_x2 = 100
         self.sensor_misses += 1
      else: 
         #update GUI
         self.canvas_cones.append(self.canvas.create_line(int(s4_x - (self.distance/math.tan(angle_4 - (fov/2)))*ppf + delay_1*ppf), int(x_axis_y - self.distance*ppf), int(s4_x - (self.distance/math.tan(angle_4 + (fov/2)))*ppf - delay_1*ppf), int(x_axis_y - self.distance*ppf), fill='red'))

#ADD ASSIGN CONES FOR SCENARIO 2   
   def assign_cones_scenario_2(self):
      global length_1, length_2, length_3, length_4, NOISE_ENABLED
      
     
      #sensor 1
      self.sensor_1_x1 = -length_1 + (self.distance/math.tan(angle_1 + fov/2))
      self.sensor_1_x2 = -length_1 + (self.distance/math.tan(angle_1 - fov/2))
      
      #determining the noise in the detection cone
      distance = self.sensor_1_x2 - self.sensor_1_x1
      if(NOISE_ENABLED == 1):
         #the point of detection within this cone (exponential distribution - adjust number, currently ~1% miss, mean is 1/4 of cone)
         delay_1 = random.expovariate(6/distance)
         #the point the cameras no longer detect the object
         delay_2 = random.expovariate(6/distance)
      else:
         delay_1 = 0
         delay_2 = 0
         
      #adding in the noise 
      self.sensor_1_x1 += delay_1
      self.sensor_1_x2 -= delay_2
      #if x1 is now greater than x2, consider it a miss
      if self.sensor_1_x1 > self.sensor_1_x2:
         self.sensor_1_x1 = -1
         self.sensor_1_x2 = 100
         self.sensor_misses += 1
      else:
         #update the GUI
         #self.canvas_cones.append(self.canvas.create_line(convert_to_pixel(self.sensor_1_x1), int(x_axis_y - self.distance*ppf), convert_to_pixel(self.sensor_1_x2), int(x_axis_y - self.distance*ppf)))
         self.canvas.create_line(convert_to_pixel(self.sensor_1_x1), int(x_axis_y - self.distance*ppf), convert_to_pixel(self.sensor_1_x2), int(x_axis_y - self.distance*ppf))
      
      #repeat for sensor 2
      self.sensor_2_x1 = -length_2 + (self.distance/math.tan(angle_2 + fov/2))
      self.sensor_2_x2 = -length_2 + (self.distance/math.tan(angle_2 - fov/2))
      #determining the noise in the detection cone
      distance = self.sensor_2_x2 - self.sensor_2_x1
      if(NOISE_ENABLED == 1):
         #the point of detection within this cone (exponential distribution - adjust number, currently ~1% miss, mean is 1/4 of cone)
         delay_1 = random.expovariate(6/distance)
         #the point the cameras no longer detect the object
         delay_2 = random.expovariate(6/distance)
      else:
         delay_1 = 0
         delay_2 = 0
         
      #adding in the noise 
      self.sensor_2_x1 += delay_1
      self.sensor_2_x2 -= delay_2

      #if x1 is now greater than x2, consider it a miss
      if self.sensor_2_x1 > self.sensor_2_x2:
         self.sensor_2_x1 = -1
         self.sensor_2_x2 = 100
         self.sensor_misses += 1
      else:
         #update the GUI
         #self.canvas_cones.append(self.canvas.create_line(convert_to_pixel(self.sensor_2_x1), int(x_axis_y - self.distance*ppf), convert_to_pixel(self.sensor_2_x2), int(x_axis_y - self.distance*ppf)))
         self.canvas.create_line(convert_to_pixel(self.sensor_2_x1), int(x_axis_y - self.distance*ppf), convert_to_pixel(self.sensor_2_x2), int(x_axis_y - self.distance*ppf))
      
      #repeat for sensor 3
      self.sensor_3_x1 = length_3 - (self.distance/math.tan(angle_3 - fov/2))
      self.sensor_3_x2 = length_3 - (self.distance/math.tan(angle_3 + fov/2))
      #determining the noise in the detection cone
      distance = self.sensor_3_x2 - self.sensor_3_x1
      if(NOISE_ENABLED == 1):
         #the point of detection within this cone (exponential distribution - adjust number, currently ~1% miss, mean is 1/4 of cone)
         delay_1 = random.expovariate(6/distance)
         #the point the cameras no longer detect the object
         delay_2 = random.expovariate(6/distance)
      else:
         delay_1 = 0
         delay_2 = 0
         
      #adding in the noise 
      self.sensor_3_x1 += delay_1
      self.sensor_3_x2 -= delay_2
      #if x1 is now greater than x2, consider it a miss
      if self.sensor_3_x1 > self.sensor_3_x2:
         self.sensor_3_x1 = -1
         self.sensor_3_x2 = 100
         self.sensor_misses += 1
      else:
         #update the GUI
         #self.canvas_cones.append(self.canvas.create_line(convert_to_pixel(self.sensor_3_x1), int(x_axis_y - self.distance*ppf), convert_to_pixel(self.sensor_3_x2), int(x_axis_y - self.distance*ppf)))
         self.canvas.create_line(convert_to_pixel(self.sensor_3_x1), int(x_axis_y - self.distance*ppf), convert_to_pixel(self.sensor_3_x2), int(x_axis_y - self.distance*ppf))
         
      #repeat for sensor 4
      self.sensor_4_x1 = length_4 - (self.distance/math.tan(angle_4 - fov/2))
      self.sensor_4_x2 = length_4 - (self.distance/math.tan(angle_4 + fov/2))
      #determining the noise in the detection cone
      distance = self.sensor_4_x2 - self.sensor_4_x1
      if(NOISE_ENABLED == 1):
         #the point of detection within this cone (exponential distribution - adjust number, currently ~1% miss, mean is 1/4 of cone)
         delay_1 = random.expovariate(6/distance)
         #the point the cameras no longer detect the object
         delay_2 = random.expovariate(6/distance)
      else:
         delay_1 = 0
         delay_2 = 0
         
      #adding in the noise 
      self.sensor_4_x1 += delay_1
      self.sensor_4_x2 -= delay_2
      #if x1 is now greater than x2, consider it a miss
      if self.sensor_4_x1 > self.sensor_4_x2:
         self.sensor_4_x1 = -1
         self.sensor_4_x2 = 100
         self.sensor_misses += 1
      else:
         #update the GUI
         #self.canvas_cones.append(self.canvas.create_line(convert_to_pixel(self.sensor_4_x1), int(x_axis_y - self.distance*ppf), convert_to_pixel(self.sensor_4_x2), int(x_axis_y - self.distance*ppf)))
         self.canvas.create_line(convert_to_pixel(self.sensor_4_x1), int(x_axis_y - self.distance*ppf), convert_to_pixel(self.sensor_4_x2), int(x_axis_y - self.distance*ppf))

   def assign_times(self):
      global ANIMATION_ENABLED, frame_time
      for i in range(0, 10):
         self.sensor_1_times = []
         self.sensor_2_times = []
         self.sensor_3_times = []
         self.sensor_4_times = []
         sim_time = 0.0
         #GUI info
         START_X = min(self.sensor_1_x1, self.sensor_2_x1) - 5 + i*frame_time*self.velocity
         END_X = max(self.sensor_4_x2, self.sensor_3_x2) + 5 + self.width
         x_1 = int(START_X)
         x_2 = x_1 - self.width
         y_1 = x_axis_y - (self.distance*ppf)
         y_2 = x_axis_y - (self.distance+3)*ppf
         if ANIMATION_ENABLED == 1:
            self.rectangle = self.canvas.create_rectangle(convert_to_pixel(x_1), y_1 , convert_to_pixel(x_2), y_2 , fill ='black')
            main_canvas.tag_lower(self.rectangle)
         while x_2 < END_X:
            #if the object is in the desired location for this frame, record the sim_time as sensor data
            if not (x_1 < self.sensor_1_x1 or x_2 > self.sensor_1_x2):
               self.sensor_1_times.append(sim_time)
               
            if not (x_1 < self.sensor_2_x1 or x_2 > self.sensor_2_x2):
               self.sensor_2_times.append(sim_time)
               
            if not (x_1 < self.sensor_3_x1 or x_2 > self.sensor_3_x2):
               self.sensor_3_times.append(sim_time)
               
            if not (x_1 < self.sensor_4_x1 or x_2 > self.sensor_4_x2):
               self.sensor_4_times.append(sim_time)
               
            sim_time += frame_time
            x_1 += self.velocity*frame_time
            x_2 += self.velocity*frame_time
            
            #print x_1, ', ', x_2, ', ', frame_time
            if ANIMATION_ENABLED == 1:
               self.canvas.coords(self.rectangle, convert_to_pixel(x_1), y_1, convert_to_pixel(x_2), y_2)
               time.sleep(0.001)
         #use the times to estimate velocity      
         self.estimate_velocity()
         self.estimate_width(i)
            
   def remove(self):
      for cone in self.canvas_cones:
         self.canvas.delete(cone)
      self.canvas.delete(self.rectangle)
   
   def velocity_calc_1(self, avg_time_1, avg_time_2, avg_time_3, avg_time_4):
      #center convergence equations
      time_difference_1_4 = abs(avg_time_4 - avg_time_1)
      time_difference_2_3 = abs(avg_time_3 - avg_time_2)
      if time_difference_1_4 != 0 and time_difference_2_3 != 0:
         equation_1_left = (length_1 + length_4)/time_difference_1_4
         equation_2_left = (length_2 + length_3)/time_difference_2_3
         
         equation_1_coefficient = ((1/tan_1) + (1/tan_4))/time_difference_1_4
         equation_2_coefficient = ((1/tan_2) + (1/tan_3))/time_difference_2_3
         
         subtract_left = equation_1_left - equation_2_left
         subtract_coefficient = equation_1_coefficient - equation_2_coefficient
         if subtract_coefficient != 0:
            self.distance_estimate_1 = subtract_left/subtract_coefficient
            self.velocity_estimate_1 = equation_1_left - equation_1_coefficient*self.distance_estimate_1
            #self.velocity_estimate_1 = mean([equation_1_left - equation_1_coefficient*self.distance_estimate_1, equation_2_left - equation_2_coefficient*self.distance_estimate_1])
         
      #edge crossing equations - very inaccurate, currently does not use
      time_difference_1_2 = abs(avg_time_2 - avg_time_1)
      time_difference_3_4 = abs(avg_time_4 - avg_time_3)
      if time_difference_1_2 != 0 and time_difference_3_4 != 0:
         equation_1_left = (length_1 - length_2)/time_difference_1_2
         equation_2_left = (length_4 - length_3)/time_difference_3_4
         
         equation_1_coefficient = ((1/tan_2) - (1/tan_1))/time_difference_1_2
         equation_2_coefficient = ((1/tan_3) + (1/tan_4))/time_difference_3_4
         
         subtract_left = equation_1_left - equation_2_left
         subtract_coefficient = equation_1_coefficient - equation_2_coefficient
         if subtract_coefficient != 0:
            #self.distance_estimate_2 = subtract_left/subtract_coefficient
            subtract_left = subtract_left
            #self.velocity_estimate_2 = mean([equation_1_left - equation_1_coefficient*self.distance_estimate_2, equation_2_left - equation_2_coefficient*self.distance_estimate_2])
      
      #print self.velocity_estimate_1, ', ', self.velocity_estimate_2
      
      if self.velocity_estimate_1 > 0 and self.velocity_estimate_2 > 0:
         self.velocity_estimate.append(mean([self.velocity_estimate_1, self.velocity_estimate_2]))
      elif self.velocity_estimate_1 > 0:
         self.velocity_estimate.append(self.velocity_estimate_1)
      elif self.velocity_estimate_2 > 0:
         self.velocity_estimate.append(self.velocity_estimate_2)
      else:
         self.velocity_estimate.append(-1)
         
      
      if self.distance_estimate_1 > 0 and self.distance_estimate_2 > 0:
         self.distance_estimate.append(mean([self.distance_estimate_1, self.distance_estimate_2]))
      elif self.distance_estimate_1 > 0:
         self.distance_estimate.append(self.distance_estimate_1)
      elif self.distance_estimate_2 > 0:
         self.distance_estimate.append(self.distance_estimate_2)
      else:
         self.distance_estimate.append(-1)
         
         
   def velocity_calc_2(self, avg_time_1, avg_time_2, avg_time_3, avg_time_4):
      #center convergence equations
      time_difference_1_4 = abs(avg_time_4 - avg_time_1)
      time_difference_2_3 = abs(avg_time_3 - avg_time_2)
      tan_1 = math.tan(angle_1 - math.pi/2)
      tan_2 = math.tan(angle_2 - math.pi/2)
      if time_difference_1_4 != 0 and time_difference_2_3 != 0:
         equation_1_left = (length_1 + length_4)/time_difference_1_4
         equation_2_left = (length_2 + length_3)/time_difference_2_3
         equation_1_coefficient = (2*tan_1)/time_difference_1_4
         equation_2_coefficient = (2*tan_2)/time_difference_2_3
         difference_left = equation_1_left - equation_2_left
         difference_coefficient = equation_1_coefficient - equation_2_coefficient
         if difference_coefficient != 0:
            self.distance_estimate = abs(difference_left/difference_coefficient)
            #if self.distance_estimate < d_low:
            #   self.distance_estimate = d_low
            #elif self.distance_estimate > d_high:
            #   self.distance_estimate = d_high
            self.velocity_estimate.append((length_1 + length_4 + 2*tan_1*self.distance_estimate)/(time_difference_1_4))
            
   #if one sensor missed, guess the missing time based on the others
   def fix_times(self, flag):
      global avg_time_1, avg_time_2, avg_time_3, avg_time_4
      if flag == 1:
         avg_time_1 = avg_time_2 - (avg_time_4 - avg_time_3)
      elif flag == 2:
         avg_time_2 = avg_time_1 + (avg_time_4 - avg_time_3)
      elif flag == 3:
         avg_time_3 = avg_time_4 - (avg_time_2 - avg_time_1)
      else:
         avg_time_4 = avg_time_3 + (avg_time_2 - avg_time_1)
         
   def estimate_avg_distance(self, flag1, flag2):
      global avg_time_1, avg_time_2, avg_time_3, avg_time_4
      #use the "average" of distance range to guess with 2 sensors
      d = (d_high + d_low)>>1
      self.distance_estimate = d
      if flag1 == 3 and flag2 == 4:
         W = abs(length_1 - d/tan_1 - length_2 + d/tan_2)
         self.velocity_estimate.append(W/abs(avg_time_1 - avg_time_2))
      elif flag1 == 2 and flag2 == 4:
         W = abs(length_1 - d/tan_1 + length_3 - d/tan_3)
         self.velocity_estimate.append(W/abs(avg_time_1 - avg_time_3))
      elif flag1 == 2 and flag2 == 3:
         W = abs(length_1 - d/tan_1 + length_4 - d/tan_4)
         self.velocity_estimate.append(W/abs(avg_time_1 - avg_time_4))
      elif flag1 == 1 and flag2 == 4:
         W = abs(length_2 - d/tan_2 + length_3 - d/tan_3)
         self.velocity_estimate.append(W/abs(avg_time_2 - avg_time_3))
      elif flag1 == 1 and flag2 == 3:
         W = abs(length_2 - d/tan_2 + length_4 - d/tan_4)
         self.velocity_estimate.append(W/abs(avg_time_4 - avg_time_2))
      else:
         W = abs(length_4 - d/tan_4 - length_3 + d/tan_3)
         self.velocity_estimate.append(W/abs(avg_time_4 - avg_time_3))
         
   def estimate_velocity(self):
      #to estimate velocity it is best to try to get the time the object would have intersected with the ideal "one pixel" beam
      #thus an average is taken of the recorded times for each sensor
      global avg_time_1, avg_time_2, avg_time_3, avg_time_4
      avg_time_1 = mean(self.sensor_1_times)
      avg_time_2 = mean(self.sensor_2_times)
      avg_time_3 = mean(self.sensor_3_times)
      avg_time_4 = mean(self.sensor_4_times)
      self.velocity_estimate_1 = -1
      self.distance_estimate_1 = -1
      self.velocity_estimate_2 = -1
      self.distance_estimate_2 = -1
      if len(self.sensor_1_times) > 0 and len(self.sensor_2_times) > 0 and len(self.sensor_3_times) > 0 and len(self.sensor_4_times) > 0 :
         if (360*angle_1)/(2*math.pi) < 90:
           self.velocity_calc_1(avg_time_1, avg_time_2, avg_time_3, avg_time_4)
         else:
           self.velocity_calc_2(avg_time_1, avg_time_2, avg_time_3, avg_time_4)
      else:
         count = 0
         sum = 0
         flag = 0
         if len(self.sensor_1_times) ==  0:
            count += 1
            sum += 1
            flag = 1
         if len(self.sensor_2_times) ==  0:
            count += 1
            sum += 2
            flag = 2
         if len(self.sensor_3_times) ==  0:
            count += 1
            sum += 3
            flag = 3
         if len(self.sensor_4_times) ==  0:
            count += 1
            sum += 4
            flag = 4
         if count == 2:
            other = sum - flag
            self.estimate_avg_distance(other, flag)
         elif count == 1:
            self.fix_times(flag)
            if (360*angle_1)/(2*math.pi) < 90:
              self.velocity_calc_1(avg_time_1, avg_time_2, avg_time_3, avg_time_4)
            else:
              self.velocity_calc_2(avg_time_1, avg_time_2, avg_time_3, avg_time_4)
         else:
            print "Here ", self.velocity
            self.velocity_estimate.append(-1)
  
   def estimate_width(self, i):
      #estimate width using the velocity estimate and the longest time the object was detected by one cone
      time_dif_1 = 0
      deltas = []
      cones = []
      if len(self.sensor_1_times) > 1:
         time_dif_1 = self.sensor_1_times[-1] - self.sensor_1_times[0]
         deltas.append(time_dif_1)
      
      time_dif_2 = 0
      if len(self.sensor_2_times) > 1:
         time_dif_2 = self.sensor_2_times[-1] - self.sensor_2_times[0]
         deltas.append(time_dif_2)
         
      time_dif_3 = 0
      if len(self.sensor_3_times) > 1:
         time_dif_3 = self.sensor_3_times[-1] - self.sensor_3_times[0]
         deltas.append(time_dif_3)
         
      time_dif_4 = 0
      if len(self.sensor_4_times) > 1:
         time_dif_4 = self.sensor_4_times[-1] - self.sensor_4_times[0]
         deltas.append(time_dif_4)
      
      #print deltas, ', ', self.velocity_estimate[i]
      #use the smallest sensor, least error introduced by FOV spread
      width_guess = 0
      if len(deltas) >= 1:
         width_guess = min(deltas)*self.velocity_estimate[i]
      if self.velocity_estimate[i] == -1:
         self.width_estimate.append(-1)
      elif width_guess == 0:
         s1 = abs(self.distance_estimate/math.tan(angle_1 + (fov/2)) - self.distance_estimate/math.tan(angle_1 - (fov/2)))
         cones.append(s1)
         
         s2 = abs(self.distance_estimate/math.tan(angle_2 + (fov/2)) - self.distance_estimate/math.tan(angle_2 - (fov/2)))
         cones.append(s2)
         
         s3 = abs(self.distance_estimate/math.tan(angle_3 + (fov/2)) - self.distance_estimate/math.tan(angle_3 - (fov/2)))
         cones.append(s3)
         
         s4 = abs(self.distance_estimate/math.tan(angle_4 + (fov/2)) - self.distance_estimate/math.tan(angle_4 - (fov/2)))
         cones.append(s4)
         self.width_estimate.append(max(cones))
      else:
         self.width_estimate.append(width_guess)
def closest(value, values):
   delta = 10000
   ret = 0
   for v in values:
      if abs(v - value) < delta:
         delta = abs(v - value)
         ret = v
   return ret

def furthest(value, values):
   delta = 0
   ret = 0
   for v in values:
      if abs(v - value) > delta:
         delta = abs(v - value)
         ret = v
   return ret

def test_func(canvas, master):
   global v_low, v_high, w_low, w_high, d_low, d_high
   global v_step, h_step, d_step, file, LOG_ENABLED
   global length_1, length_2, length_3, length_4
   global angle_1, angle_2, angle_3, angle_4
   global FPS_NUM
   if LOG_ENABLED:
       f_h = open(file, 'w')
       f_h.write("Simulation Parameters\n")
       f_h.write("Distance Range (ft): " + str(d_low) + " min, " + str(d_high) + " max, " + str(d_step) + " step\n")
       f_h.write("Velocity Range (ft/s): " + str(v_low) + " min, " + str(v_high) + " max, " + str(v_step) + " step\n")
       f_h.write("Width Range (ft): " + str(w_low) + " min, " + str(w_high) + " max, " + str(w_step) + " step\n")
       f_h.write("L1 (ft): " + str(length_1) + " L2: " + str(length_2) + " L3: " + str(length_3) + " L4: " + str(length_4) + "\n")
       f_h.write("A1 (degrees): " + str(round(angle_1*360 / (2.0*math.pi), 3)) + " A2: " + str(round(angle_2*360 / (2.0*math.pi), 3)) + " A3: " + str(round(angle_3*360 / (2.0*math.pi), 3)) + " A4: " + str(round(angle_1*360 / (2.0*math.pi), 3)) + "\n") 
       f_h.write("FPS " + str(FPS_NUM) + "\n")
       f_h.write( '-----------------------------------------\n')
   w_err_max = 0
   v_err_max = 0
   for v in range(v_low, v_high+1, v_step):
      for w in range(w_low, w_high+1, w_step):
         for d in range(d_low, d_high+1, d_step):
            my_obj = test_obj(canvas, d, v, w)
            if ANIMATION_ENABLED == 1:
               my_obj.remove()
            v_err = abs(mean(my_obj.velocity_estimate) - my_obj.velocity)
            w_err = abs(mean(my_obj.width_estimate) - my_obj.width)
            #print 'Global Lists'
            #print my_obj.velocity_estimate
            #print my_obj.width_estimate
            if v_err > v_err_max:
               v_err_max = v_err
            if w_err > w_err_max:
               w_err_max = w_err
            if LOG_ENABLED:
               f_h.write( 'd = '+ str(my_obj.distance))
               f_h.write( '\nw = '+ str(my_obj.width) + '\nv = ' + str(my_obj.velocity))
               f_h.write( '\nw est = ' + str(round(mean(my_obj.width_estimate), 3)) 
                                       + ' avg w err = ' + str(round(w_err, 3)) 
                                       + ' w max error = ' + str(round(abs(furthest(my_obj.width, my_obj.width_estimate) - my_obj.width), 3))
                                       + ' w min error = ' + str(round(abs(closest(my_obj.width, my_obj.width_estimate) - my_obj.width), 3)))
               f_h.write( '\nv est = ' + str(round(mean(my_obj.velocity_estimate), 3)) 
                                       + ' avg v err = ' + str(round(v_err, 3)) 
                                       + ' v max error = ' + str(round(abs(furthest(my_obj.velocity, my_obj.velocity_estimate) - my_obj.velocity), 3))
                                       + ' v min error = ' + str(round(abs(closest(my_obj.velocity, my_obj.velocity_estimate) - my_obj.velocity), 3)))
               f_h.write( '\nmisses = ' + str(my_obj.sensor_misses))
               f_h.write('\n\n')
   if LOG_ENABLED:
      f_h.write( '-----------------------------------------\n')
      f_h.write( "Maximum error in velocity = " + str(v_err_max) + ' ft/s\n')
      f_h.write( "Maximum error in width = " + str(w_err_max) + ' ft')
   
   canvas.create_text(50, 228, font="Times 10 underline", text="Results", anchor=W)
   canvas.create_text(50, 245, font="Times 10", text="Velocity Error Max(ft/s): "+str(round(v_err_max, 3)), anchor=W)
   canvas.create_text(50, 260, font="Times 10", text="Width Error Max(ft/s): "+str(round(w_err_max, 3)), anchor=W)
   if LOG_ENABLED:
      f_h.close()
      processSim.process()
   thread.exit()
   
   
   
 
d = MyDialog(master)
create_gui(master)

   
'''
i = 5  
width = 5
distance = 4
flag = 1   
v_err_max = 0
w_err_max = 0 
debug = 0
while i < 30:         
   #dist, vel, wid       
   my_obj = test_obj(distance, i, width)
   v_err = abs(my_obj.velocity_estimate - my_obj.velocity)
   w_err = abs(my_obj.width_estimate - my_obj.width)
   if v_err > v_err_max:
      v_err_max = v_err
   if w_err > w_err_max:
      w_err_max = w_err
      
   if flag == 1:
      print 'sensor 1 range ', my_obj.sensor_1_x1, ' - ', my_obj.sensor_1_x2
      print 'sensor 2 range ', my_obj.sensor_2_x1, ' - ', my_obj.sensor_2_x2
      print 'sensor 3 range ', my_obj.sensor_3_x1, ' - ', my_obj.sensor_3_x2
      print 'sensor 4 range ', my_obj.sensor_4_x1, ' - ', my_obj.sensor_4_x2
      flag = 0
      print 
   if debug:
      print '======================================================================================='
      print 'width: ', my_obj.width, ' feet'
      print 'distance from sensors: ', my_obj.distance, ' feet'
      print 'velocity: ', my_obj.velocity, 'feet per second'
      print
      print 'sensor_1 times: ', my_obj.sensor_1_times
      print 'sensor_2 times: ', my_obj.sensor_2_times
      print 'sensor_3 times: ', my_obj.sensor_3_times
      print 'sensor_4 times: ', my_obj.sensor_4_times   

      print 'width estimate ' , my_obj.width_estimate, ' width error ', w_err
      print 'velocity estimate ', my_obj.velocity_estimate, ' velocity error ', v_err
      print '======================================================================================='
      print
   i += 1
   
print "V ", v_err_max
print "W ", w_err_max
'''
         
            