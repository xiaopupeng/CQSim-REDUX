import numpy as np
import pandas as pd

class Update:
    # decide whether a current grid price is in high or low level
    # first use the initialized gridpriceThreshold
    # then if grid price statistic count percentage is larger than scaleRatio, then use arithmetic average
    def __init__(self, inputPara):
        self.myInfo = 'Update'
        self.dataSize = inputPara['dataSize']
        self.scaleRatio = inputPara['scaleRatio']
        self.node_num = inputPara['nodNum']
        self.proc_perNode = inputPara['procPerNode']
        self.upsCapability = inputPara['upsCapability']
        self.dataCenterCap = self.node_num * self.proc_perNode
        self.gridpriceThreshold = inputPara['initGridpriceThreshold']
        self.curWorkloadRatio = inputPara['initCurWorkloadRatio']
        self.workloadHighRatio = 0
        self.workloadLowRatio = 0

    def reset(self):
        pass

    def data_center_cap(self):
        return self.dataCenterCap


    # def power_profile(self, job_index=-1):
    #     PROFILE_BASE = 10
    #     temp_job = self.job_module.job_info(job_index)
    #     proc_num, req_time = temp_job['reqProc'], temp_job['reqTime']
    #     # get normal distributed power profile of each processor(node) between 20~60W
    #     proc_profile = np.random.normal(size=proc_num) * PROFILE_BASE + PROFILE_BASE*2
    #     proc_profile = np.round(proc_profile, decimals=2)
    #     i=0
    #     while(i<len(proc_profile)): # assign boundray value to outsiders
    #         if proc_profile[i] > PROFILE_BASE*3:
    #             proc_profile[i] = PROFILE_BASE*3
    #         elif proc_profile[i] < PROFILE_BASE:
    #             proc_profile[i] = PROFILE_BASE
    #         i+=1
    #     power_result = np.sum(proc_profile) * req_time # in Watt
    #     return round(power_result)

    # decide whether a current grid price is in high or low level
    # first use the initialized gridpriceThreshold
    # then if grid price statistic count percentage is larger than scaleRatio, then use arithmetic average
    def updateGridPriceState(self, gridpriceStat, gridPrice):
        # decide whether use average of previous gridprice threshold
        if len(gridpriceStat) >= self.dataSize * self.scaleRatio:
            self.gridpriceThreshold = np.average(gridpriceStat) * 0.666
        # decide whether gridprice is high or low
        if gridPrice >= self.gridpriceThreshold:
            gridpriceState = 'high'
        else:
            gridpriceState = 'low'
        return gridpriceState


    # update the high and low ratio of workload according to smoothed workload, will approach to 0.8 and 0.2 as when more workload recorded
    # after certain scale ratio, the high and low threshold of workload will updated by the historical stat of workload
    def updateWorkloadRatio(self, workloadStat):
        # hard copy and sort current workload stat
        curWorkloadStat = workloadStat.copy()
        curWorkloadStat.sort()
        # new ratio is decided by
        self.workloadLowRatio = self.curWorkloadRatio
        self.workloadHighRatio = 1 - self.curWorkloadRatio
        if len(curWorkloadStat) >= self.dataSize * self.scaleRatio:
            lowRatioPosition = round(len(curWorkloadStat) * self.curWorkloadRatio) - 1
            highRatioPosition = len(curWorkloadStat) - lowRatioPosition
            self.workloadLowRatio = curWorkloadStat[lowRatioPosition] / max(workloadStat)
            self.workloadHighRatio = curWorkloadStat[highRatioPosition] / max(workloadStat)

    def updateWorkloadState(self, curWorkload, renState):
        dataCenterPowCap = self.get_data_center_pow_cap_dynamic(renState)
        if curWorkload > dataCenterPowCap * self.workloadHighRatio:
            workloadState = 'high'
        elif curWorkload <= dataCenterPowCap * self.workloadHighRatio and curWorkload > dataCenterPowCap * self.workloadLowRatio:
            workloadState = 'medium'
        else:
            workloadState = 'low'
        return workloadState

    def get_data_center_pow_cap_dynamic(self, renState):
        if renState == 'outage':
            dataCenterPowCap = self.node_num * self.proc_perNode * 0.5 * 3.6
        else:
            dataCenterPowCap = self.node_num * self.proc_perNode * 1.5 * 3.6
        return dataCenterPowCap

    # decide utilization level of ups for current time spot
    # NEW DESIGN: need to consider grid price to decide ups utility level
    def updateUpsUtilityLevel(self, workloadState):
        if workloadState == 'high':
            upsAbility = self.upsCapability * 0.9
            upsState = 'max'
        if workloadState == 'medium':
            upsAbility = self.upsCapability * 0.8
            upsState = 'medium'
        if workloadState == 'low':
            upsAbility = self.upsCapability * 0.7
            upsState = 'low'
        return upsAbility, upsState


    def updateUpsSupply(self, gridpriceState, curWorkload, workloadOVR, renState, upsStorage, upsSupplyFlu):
        # there is no upsSupply and upsstorage change at first
        upsSupply = 0
        updatedUpsStorage = upsStorage
        if renState == 'outage':
            if curWorkload >= workloadOVR and gridpriceState == 'high':
                upsSupply = upsStorage
                updatedUpsStorage = 0
            elif curWorkload < workloadOVR and gridpriceState == 'low':
                upsSupply = - (self.upsCapability - upsStorage)
                updatedUpsStorage = self.upsCapability

        elif renState == 'fluctuate':
            if curWorkload < workloadOVR and gridpriceState == 'low':
                upsSupply = - (self.upsCapability - upsStorage)
                updatedUpsStorage = self.upsCapability

        else:
            if gridpriceState == 'low' or (curWorkload < workloadOVR and gridpriceState == 'high'):
                upsSupply = - (self.upsCapability - upsStorage)
                updatedUpsStorage = self.upsCapability
        # consider the upsSupply change in fluctuate
        upsSupply += upsSupplyFlu
        return round(upsSupply,3), round(updatedUpsStorage,3)
