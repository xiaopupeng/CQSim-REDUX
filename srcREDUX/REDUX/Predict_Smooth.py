import numpy as np
import pandas as pd

class Predict_Smooth:
    def __init__(self, inputPara, update_module=None):
        self.myInfo = 'Predict_Smooth'
        self.updateMod = update_module
        self.scaleRatio = inputPara['scaleRatio']
        self.dataSize = inputPara['dataSize']
        self.upsCapability = inputPara['upsCapability']
        self.dataCenterCap = self.updateMod.data_center_cap()
        self.WINDOW = round(self.scaleRatio * self.dataSize)

    def reset(self):
        pass

    # use workload shaving to defer extra workload to next time slot
    # self.dataCenterCap the capacity of the most workload executable of data center
    def workloadDefer(self, curWorkload, workloadBuffer,renState):
        dyDataCenterCap(renState)
        if curWorkload + workloadBuffer <= self.dataCenterCap:
            updateCurWorkload = curWorkload + workloadBuffer
            updateworkloadBuffer = 0
        else:
            updateCurWorkload = self.dataCenterCap
            updateworkloadBuffer = workloadBuffer + curWorkload - self.dataCenterCap
        return round(updateCurWorkload,3), round(updateworkloadBuffer,3)

    def dyDataCenterCap(self,renState):
        dataCenterCapScaleRatio = 0.5
        if renState == 'available':
            self.dataCenterCap = round(dataCenterCap * (1+dataCenterCapScaleRatio))
        else:
            self.dataCenterCap = round(dataCenterCap * (1-dataCenterCapScaleRatio))
        return

    # smoothing the current workload by exponential windowed avarage
    def workloadSmoothing(self, curWorkload, workloadBuffer, workloadStat):
        if len(workloadStat) > self.WINDOW:
            curSmoothedWorload = pd.Series(workloadStat).ewm(span=self.WINDOW, min_periods=10).mean().values[-1]
        else:
            curSmoothedWorload = curWorkload

        if curSmoothedWorload <= curWorkload:
            updateworkloadBuffer = workloadBuffer + curWorkload - curSmoothedWorload
            updateCurWorkload = curSmoothedWorload
        else:
            if workloadBuffer < curSmoothedWorload - curWorkload:
                updateworkloadBuffer = 0
                updateCurWorkload = curSmoothedWorload + workloadBuffer
            else:
                updateworkloadBuffer = workloadBuffer - curSmoothedWorload + curWorkload
                updateCurWorkload = curSmoothedWorload
        return round(updateCurWorkload,3), round(updateworkloadBuffer,3)


    # we need to figure out how to define fluctuate and tell why we still use grid as much as possible when grid price is low(by always set a low price), otherwise we lost our motivation
    def defineRenState(self, renSupply, renSupplyStat, renSupplyData):
        smoothedRenSupply = pd.Series(renSupplyStat).ewm(span=self.WINDOW * 0.1, min_periods=10).mean()
        curSmoothedRenSupply = smoothedRenSupply.values[-1]
        if renSupply < max(renSupplyData) * 0.1:  # or renSupplyCapability?
            renState = 'outage'
        elif renSupply >= max(renSupplyData) * 0.9:
            renState = 'stable'
        else:
            if renSupply > curSmoothedRenSupply * 0.9 and renSupply < curSmoothedRenSupply * 1.1:
                renState = "stable"
            else:
                renState = 'fluctuate'
        return renState

    # update the stable renewable supply level by historical fluctuate renewable supply stat
    def getStableRenSupply(self, fluRenSupplyStat):
        stableRenSupply = 0
        stableRenSupply = pd.Series(fluRenSupplyStat).ewm(span=self.WINDOW, min_periods=1).mean().values[-1]
        print('stableRenSupply=',round(stableRenSupply,3))
        return round(stableRenSupply,3)

    def renSupplySmooth(self, gridpriceState, gridPrice, renSupply, renPrice, stableRenSupply, upsAbility, upsStorage):
        upsSupplyFlu = 0
        stableGridSupply = 0
        updatedUpsStorage = 0
        # if renewable power is sufficient
        if renSupply - (upsAbility - upsStorage) >= stableRenSupply:
            renSupply -= (upsAbility - upsStorage)
            updatedUpsStorage = upsAbility
        if stableRenSupply <= renSupply and renSupply - (upsAbility - upsStorage) < stableRenSupply:
            updatedUpsStorage = upsStorage + (renSupply - stableRenSupply)
            renSupply = stableRenSupply
        # if renewable power is not sufficient
        if stableRenSupply - upsStorage <= renSupply and renSupply < stableRenSupply:
            updatedUpsStorage = upsStorage - (stableRenSupply - renSupply)
            renSupply = stableRenSupply
            if gridPrice <= renPrice:  # only grid price is lower than renPrice  then charge ups
                stableGridSupply = stableRenSupply - renSupply + upsAbility - upsStorage
                renSupply = stableRenSupply
                updatedUpsStorage = upsAbility
        if renSupply < stableRenSupply - upsStorage:
            if gridpriceState == 'high':  # do not use grid power
                renSupply += upsStorage
                updatedUpsStorage = 0
            else:  # charge ups even grid price is only 'low' (not lower than renewable price)
                stableGridSupply = stableRenSupply - renSupply + upsAbility - upsStorage
                renSupply = stableRenSupply
                updatedUpsStorage = upsAbility
        upsSupplyFlu = upsStorage - updatedUpsStorage
        return renSupply, updatedUpsStorage, stableGridSupply, upsSupplyFlu
