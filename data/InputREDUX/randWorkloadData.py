import numpy as np
import matplotlib.pyplot as plt

workloadData = np.ravel(np.random.randn(1, 2568))
workloadData += - min(workloadData)
workloadData *= (3000/max(workloadData))

np.savetxt('/Users/xiaopupeng/Dropbox/WorkSpace/Redux/data/workload.csv', workloadData, delimiter=',')

input = np.loadtxt(open('/Users/xiaopupeng/Dropbox/WorkSpace/Redux/data/workload.csv','rb'), delimiter = ',', skiprows=0)

print(input)
print(max(input), min(input))
timeLog = range(0,2568)
plt.plot(timeLog, input)
plt.show()





