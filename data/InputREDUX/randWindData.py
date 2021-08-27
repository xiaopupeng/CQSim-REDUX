import numpy as np
import random
import matplotlib.pyplot as plt


windData1 = random.choices(list(range(50,250)), k=1500)
windData2 = random.choices(list(range(30,220)), k=1500)
windData3 = random.choices(list(range(0,280)), k=3000)
windData4 = random.choices(list(range(20,260)), k=1704)

windData = windData1 + windData2 + windData3 + windData4

print(len(windData))

# np.savetxt('/Users/xiaopupeng/Dropbox/WorkSpace/Redux/wind2.csv', windData, delimiter=',')
np.savetxt('C:/Users/xzp0007/Dropbox/Workspace/CQSim-REDUX/data/InputREDUX/wind2.csv', windData, delimiter=',')

input = np.loadtxt(open('C:/Users/xzp0007/Dropbox/Workspace/CQSim-REDUX/data/InputREDUX/wind2.csv','rb'), delimiter = ',', skiprows=0)

print(max(input), min(input))
timeLog = range(0,7704)
plt.plot(timeLog, input)
plt.show()
