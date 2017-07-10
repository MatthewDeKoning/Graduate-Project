def process():
   fh = open('V.txt', 'r')
   distance = []
   width = []
   velocity = []
   w_est = []
   w_err = []
   v_est = []
   v_err = []
   w_max = []
   v_max = []
   w_min = []
   v_min = []
   
   i = 0
   for line in fh:
      if i < 8:
         pass
      else:
         line_exploded = line.split('=')
         
         if line_exploded[0].lstrip().rstrip() == 'd':
            distance.append(line_exploded[1].lstrip().rstrip())
         elif line_exploded[0].lstrip().rstrip() == 'w':
            width.append(line_exploded[1].lstrip().rstrip())
         elif line_exploded[0].lstrip().rstrip() == 'v':
            velocity.append(line_exploded[1].lstrip().rstrip())
         elif line_exploded[0].lstrip().rstrip() == 'w est':
            w_est.append(line_exploded[1].split(' ')[1].lstrip().rstrip())
            w_err.append(line_exploded[2].lstrip().rstrip().split(' ')[0].lstrip().rstrip())
            w_max.append(line_exploded[3].lstrip().rstrip().split(' ')[0].lstrip().rstrip())
            w_min.append(line_exploded[4].lstrip().rstrip())
         elif line_exploded[0].lstrip().rstrip() == 'v est':
            v_est.append(line_exploded[1].split(' ')[1].lstrip().rstrip())
            v_err.append(line_exploded[2].lstrip().rstrip().split(' ')[0].lstrip().rstrip())
            v_max.append(line_exploded[3].lstrip().rstrip().split(' ')[0].lstrip().rstrip())
            v_min.append(line_exploded[4].lstrip().rstrip())
      i += 1


   distance_str = ','      
   distance_str = distance_str.join(distance)

   width_str = ','
   width_str = width_str.join(width)

   velocity_str = ','
   velocity_str = velocity_str.join(velocity)

   w_est_str = ','
   w_est_str = w_est_str.join(w_est)

   w_err_str = ','
   w_err_str = w_err_str.join(w_err)

   v_est_str = ','
   v_est_str = v_est_str.join(v_est)

   v_err_str = ','
   v_err_str = v_err_str.join(v_err)

   fh.close()

   fh = open('V.csv', 'w+')

   fh.write(distance_str)
   fh.write('\n')
   fh.write(width_str)
   fh.write('\n')
   fh.write(velocity_str)
   fh.write('\n')
   fh.write(w_est_str)
   fh.write('\n')
   fh.write(w_err_str)
   fh.write('\n')
   fh.write(v_est_str)
   fh.write('\n')
   fh.write(v_err_str)

   fh.close()
   
   count_1 = 0
   count_2 = 0
   total = 0
   M = 0
   V_M = 0
   V_S = 2000
   for v_e, v, v_m, v_s in zip(v_err, velocity, v_max, v_min):
      total += float(v_e)
      if float(v_e) > M:
        M = float(v_e)
      if float(v_m) > V_M:
         V_M = float(v_m)
      if float(v_s) < V_S:
         V_S = float(v_s)
      if float(v_m) > 0.2*int(v):
         count_2 += 1
   
   for v_e, v in zip(v_max, velocity):
      if float(v_e) > 0.1*int(v):
         count_1 += 1
   print "Velocity"
   print "Average Error: ", total / float(len(v_err))
   print "Minimum Error: ", V_S
   print "Max Average Error: ", M, '\nMax Error ', V_M
   print "Average Above 10% error: ", count_1 / float(len(v_err))
   print "Average Above 20% error: ", count_2 / float(len(v_err))
   
   count_1 = 0
   count_2 = 0
   total = 0
   M = 0
   W_M = 0
   W_S = 2000
   for w_e, w, w_m, w_s in zip(w_err, width, w_max, w_min):
      total += float(w_e)
      if float(w_e) > M:
        M = float(w_e)
      if float(w_m) > W_M:
         W_M = float(w_m)
      if float(w_s) < W_S:
         W_S = float(w_s)
      if float(w_e) > 0.25*int(w):
         count_1 += 1

   print "\nWidth"
   print "Average Error: ", total / float(len(w_err))
   print "Minimum Error: ", W_S
   print "Max Average Error: ", M, '\nMax Error ', W_M
   print "Average Above 25% error: ", count_1 / float(len(w_err))
   
