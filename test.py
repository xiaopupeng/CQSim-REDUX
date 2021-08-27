removeList = [12, 13, 14, 15, 16, 17, 18, 19, 20]
waitQueue = [{'id': 11, 'time': 0.0, 'run': 7200.0, 'proc': 1, 'priority': 3, 'para': [1, 0]}, {'id': 12, 'time': 161.0, 'run': 7200.0, 'proc': 1, 'priority': 3, 'para': [1, 1]}, {'id': 13, 'time': 1185.0, 'run': 43200.0, 'proc': 8, 'priority': 4, 'para': [1, 2]}, {'id': 14, 'time': 5035.0, 'run': 46800.0, 'proc': 32, 'priority': 3, 'para': [1, 3]}, {'id': 15, 'time': 8165.0, 'run': 50400.0, 'proc': 7, 'priority': 3, 'para': [1, 4]}, {'id': 16, 'time': 9971.0, 'run': 28800.0, 'proc': 1, 'priority': 3, 'para': [1, 5]}, {'id': 17, 'time': 11556.0, 'run': 162000.0, 'proc': 5, 'priority': 3, 'para': [1, 6]}, {'id': 18, 'time': 12717.0, 'run': 18000.0, 'proc': 1, 'priority': 3, 'para': [1, 7]}, {'id': 20, 'time': 14905.0, 'run': 10800.0, 'proc': 1, 'priority': 4, 'para': [1, 8]}, {'id': 21, 'time': 15305.0, 'run': 28800.0, 'proc': 11, 'priority': 3, 'para': [1, 9]}, {'id': 22, 'time': 16712.0, 'run': 7200.0, 'proc': 32, 'priority': 2, 'para': [1, 10]}, {'id': 23, 'time': 17403.0, 'run': 28800.0, 'proc': 11, 'priority': 3, 'para': [1, 11]}, {'id': 24, 'time': 18036.0, 'run': 3600.0, 'proc': 24, 'priority': 3, 'para': [1, 12]}, {'id': 25, 'time': 18656.0, 'run': 1200.0, 'proc': 2, 'priority': 3, 'para': [1, 13]}, {'id': 26, 'time': 18672.0, 'run': 3600.0, 'proc': 16, 'priority': 3, 'para': [1, 14]}, {'id': 27, 'time': 18697.0, 'run': 1200.0, 'proc': 8, 'priority': 3, 'para': [1, 15]}, {'id': 28, 'time': 18703.0, 'run': 2400.0, 'proc': 8, 'priority': 3, 'para': [1, 16]}, {'id': 29, 'time': 18709.0, 'run': 1200.0, 'proc': 8, 'priority': 3, 'para': [1, 17]}, {'id': 30, 'time': 18746.0, 'run': 1200.0, 'proc': 16, 'priority': 3, 'para': [1, 18]}, {'id': 31, 'time': 18790.0, 'run': 1200.0, 'proc': 16, 'priority': 3, 'para': [1, 19]}, {'id': 32, 'time': 18799.0, 'run': 1200.0, 'proc': 16, 'priority': 3, 'para': [1, 20]}, {'id': 33, 'time': 19657.0, 'run': 61200.0, 'proc': 1, 'priority': 3, 'para': [1, 21]}, {'id': 34, 'time': 20367.0, 'run': 3600.0, 'proc': 2, 'priority': 3, 'para': [1, 22]}]

print('waitQueueLen = ', len(waitQueue))

for i in reversed(removeList):
    print("i=====",i)
    waitQueue.remove(waitQueue[i])



print('waitQueueLen = ', len(waitQueue))
