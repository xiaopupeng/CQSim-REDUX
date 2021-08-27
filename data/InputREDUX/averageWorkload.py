import numpy as np
import matplotlib.pyplot as plt


input = np.loadtxt(open('/Users/xiaopupeng/Dropbox/WorkSpace/Redux/data/workload.csv','rb'), delimiter = ',', skiprows=0)





print(input)
print(max(input), min(input))
timeLog = range(0,2568)
plt.plot(timeLog, input)
plt.show()





