import numpy

file = 'calibration_data.txt'
with open(file) as f:
   lines = f.readlines()

t1 = []
t2 = []
t3 = []
t4 = []

s14 = []
s23 = []

rd = []
rs = []
#test = numpy.array([11.37, 7.289])
#test = numpy.array([9.618, -2.015, -111.676, 50.515])
test = numpy.array([33.46, -6.96, -141.92, 50.37])
true = numpy.array([15, 20, 20, 25, 30, 30, 40, 30, 30, 15, 15, 25, 25, 40, 40, 20, 20, 30, 20, 20])
count = 0
for l in lines:
    if count % 2 == 1:
        s = l.split(" ")
        t1.append(float(s[0]))
        t2.append(float(s[1]))
        t3.append(float(s[2]))
        t4.append(float(s[3].strip('\n')))
    else:
        s = l.split("_")
        rd.append(s[1])
        rs.append(s[2])
    count+=1
    
at = numpy.zeros((len(t1), 4))
st = numpy.zeros((len(t1), 3))
ad = numpy.zeros((len(t1), 1))
for i in range(0, len(t1)):
    at[i][0] = t1[i]
    at[i][1] = t2[i]
    at[i][2] = t3[i]
    at[i][3] = t4[i]
    #st[i][0] = s14[i]
    #st[i][1] = s23[i]
    ad[i] = rd[i]

#solve for 4 coefficients
atT = numpy.transpose(at)
mult = atT.dot(at)
left = numpy.linalg.inv(mult)
right = atT.dot(true)

final = left.dot(right)
#print left
#print right
#print final
#mult = at.dot(test)
mult = at.dot(test)


for i in range(0, len(t1)):
    st[i][0] = mult[i]
    st[i][1] = ad[i]
    st[i][2] = abs(mult[i] - ad[i])

print "estimate, truth, error"
print st
