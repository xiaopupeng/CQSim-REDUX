import numpy as np
import pandas as pd
import copy

class DataIO:
    def __init__(self, inputPara):
        self.myInfo = 'DataIO'

        self.inputDir = inputPara['path_in']
        self.outputDir = inputPara['path_out']
        self.windPrice = inputPara['windPrice']
        self.solarPrice = inputPara['solarPrice']
        self.upsPrice = inputPara['upsPrice']
        self.node_num = inputPara['nodNum']
        self.proc_perNode = inputPara['procPerNode']
        self.upsCapability = inputPara['upsCapability']
        self.upsStorage = inputPara['upsCapability']

        self.data_size = 0

        self.workload = []
        self.gridprice = []
        self.solar = []
        self.wind = []
        self.renew = []


    def reset(self):
        self.workload = []
        self.gridprice = []
        self.solar = []
        self.wind = []
        self.renew = []

    def loadData(self):
        ##### workload trace for REDUX sim only #####
        # self.workload = np.loadtxt(open(self.inputDir + 'workload.csv', 'rb'), delimiter=',', skiprows=0)
        # for i in range(len(self.workload)):
        #     item = round(self.workload[i], 2)
        #     self.workload[i] = item

        # gridprice trace
        self.gridprice = np.ravel(np.loadtxt(open(self.inputDir + 'gridprice.csv', 'rb'), delimiter=',', skiprows=0))
        # solar trace
        self.solar = np.loadtxt(open(self.inputDir + 'solar.csv', 'rb'), delimiter=',', skiprows=0)
        # wind trace
        self.wind = np.loadtxt(open(self.inputDir + 'wind.csv', 'rb'), delimiter=',', skiprows=0)
        # print('workload:',len(self.workload),', gridprice:',len(self.gridprice),', wind energy:',len(self.wind),', solar:',len(self.solar))
        self.renew = self.wind + self.solar
        self.data_size = min(len(self.gridprice), len(self.wind), len(self.solar))

    def get_data_center_pow_cap_fixed(self):
        dataCenterPowCap = self.node_num * self.proc_perNode * 3.6
        return dataCenterPowCap

    def get_data_center_pow_cap_dynamic(self,renState):
        if renState == 'outage':
            dataCenterPowCap = self.node_num * self.proc_perNode * 0.6 * 3.6
        else:
            dataCenterPowCap = self.node_num * self.proc_perNode * 1.4 * 3.6
        return dataCenterPowCap


    # revision to get workload data from cqsim
    def get_workload(self,index):
        return self.workload[index]

    def cqsim_power_aware(self):
        pass


    def calculate_ren_price(self, index=0):
        renPrice = (self.wind[index] * self.windPrice + self.solar[index] * self.solarPrice) / (self.wind[index] + self.solar[index])
        return renPrice

    def get_gridprice(self,index):
        return self.gridprice[index]

    def get_renewable(self,index):
        return self.renew[index]

    def get_renewableData(self):
        return self.renew

    def get_data_size(self):
        return self.data_size

    def printResult(self):
        pass

    def printData(self):
        pass
