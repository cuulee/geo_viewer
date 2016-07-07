import numpy as np
import matplotlib.pyplot as plt
import string

lat = []
lon = []

plt.figure()

f = open("sample.txt")

for line in f:
    lat.append(string.atof(line.split()[0]))
    lon.append(string.atof(line.split()[1]))

plt.plot(lat,lon,color="red",linewidth=2)    
plt.plot(lat,lon,'o',color="red")
plt.show()

#x = np.linspace(0, 10, 1000)
#y = np.sin(x)
#z = np.cos(x**2)

#plt.figure(figsize=(8,4))
#plt.plot(x,y,label="$sin(x)$",color="red",linewidth=2)
#plt.plot(x,z,"b--",label="$cos(x^2)$")
#plt.xlabel("Time(s)")
#plt.ylabel("Volt")
#plt.title("PyPlot First Example")
#plt.ylim(-1.2,1.2)
#plt.legend()
#plt.show()
