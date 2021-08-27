import numpy as np
import matplotlib.pyplot as plt

inputOrigin = np.ravel(np.loadtxt(open('/Users/xiaopupeng/Dropbox/WorkSpace/Redux/data/workload.csv','rb'), delimiter = ',', skiprows=0))
input = sorted(inputOrigin)

finalPlot = []
for i in range(len(input)):
    if (495 < input[i] and input[i] < 505) or (999.8 < input[i] and input[i] < 1000.2) or (1500 < input[i] and input[i] < 1500.3)or (1999.9 < input[i] and input[i] < 2000.2):
       finalPlot.append([i, i+1, i+2])

print(finalPlot)

print(input)
print(sum(input)/len(input))
print(max(input), min(input))
print(range(len(input)))




# timeLog = range(0,2568)
# plt.plot(timeLog, input, label = 'grid price')
# plt.xlabel('hourly time slot')
# plt.ylabel('dollar price per kWh')
# plt.title('Grid Price')
# plt.legend()
# plt.show()

# for i in range(len(input)):
#     for j in range(i+1, len(input)):
#         if input[j] == input[i]:
#             print(input[i])
