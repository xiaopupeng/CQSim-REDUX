import itertools as it

class Redux_Sim:
    def __init__(self, module_list):
        self.myInfo = 'ReduxSim'
        self.mod = module_list

        self.curWorkload = 0
        self.curHour = 0

        self.renPrice = 0
        self.gridPrice = 0
        self.renSupply = 0
        self.gridSupply = 0
        self.upsSupply = 0
        self.upsAbility = 0
        self.upsStorage = self.mod['input'].upsStorage

        self.gridpriceState = None
        self.upsState = None
        self.renState = None

        self.gridpriceStat = []
        self.workloadStat = []
        self.renSupplyStat = []
        self.fluRenSupplyStat = []

        self.reduxCost = 0

        self.reduxStat = []
        # self.greenswitchStat = []
        self.noRenStat = [] # NEW DESIGN: all workloads are done by grid power
        self.specialCase = []
        self.reduxAccu = []
        self.noRenAccu = []
        # self.greenswitchAccu = []

        # change to self.workloadQueue:
        self.workloadBuffer = 0

        for module_name in self.mod:
            temp_name = self.mod[module_name].myInfo
            print(temp_name+" ................... Load")

    def reset(self):
        self.curWorkload = 0
        self.curHour = 0

        self.renPrice = 0
        self.gridPrice = 0
        self.renSupply = 0
        self.gridSupply = 0
        self.upsSupply = 0
        self.upsAbility = 0
        self.upsStorage = self.mod['input'].upsStorage

        self.gridpriceState = None
        self.upsState = None
        self.renState = None

        self.gridpriceStat = []
        self.workloadStat = []
        self.renSupplyStat = []
        self.fluRenSupplyStat = []

        self.reduxCost = 0

        self.reduxStat = []
        # self.greenswitchStat = []
        self.noRenStat = [] # NEW DESIGN: all workloads are done by grid power
        self.specialCase = []
        self.reduxAccu = []
        self.noRenAccu = []
        # self.greenswitchAccu = []

        # change to self.workloadQueue:
        self.workloadBuffer = 0
        return

    ### main method ###
    def redux_sim(self,curHour,workload,renState):
        self.curHour = curHour
        self.curWorkload = workload
        print('workload in redux>>>>>>>>>>>>>>>>>',self.curWorkload)
        self.get_data(self.curHour)
        self.preprocess(renState)
        self.updates(renState) # update states or thresholds
        if self.renState == 'fluctuate':
            stableGridSupply, upsSupplyFlu = self.ren_fluctuate()
        else:
            upsSupplyFlu = 0
            stableGridSupply = 0
        self.upsSupply = self.update_ups(upsSupplyFlu)
        # find gridSupply by supply constrain
        self.gridSupply = self.curWorkload - self.renSupply - self.upsSupply + stableGridSupply
        print('gridSupply=', self.gridSupply)
        self.reduxCost = self.calculate_costs()
        return 0
    ######################

    def get_data(self, curHour):
        self.renPrice = self.mod['input'].calculate_ren_price(curHour)
        self.gridPrice = self.mod['input'].get_gridprice(curHour)
        self.renSupply = self.mod['input'].get_renewable(curHour)
        self.gridpriceStat.append(self.gridPrice)
        self.renSupplyStat.append(self.renSupply)

    def preprocess(self,renState):
        # workload shaving to avoid over-capability load
        if self.workloadBuffer > 0:
            self.curWorkload, self.workloadBuffer = self.mod['predsmoo'].workloadDefer(self.curWorkload, self.workloadBuffer, renState)
        self.workloadStat.append(self.curWorkload)
        print('workload = ', self.curWorkload, 'workloadBuffer=', self.workloadBuffer, 'renSupply=', self.renSupply)

        # greenswitchCost = self.mod['results'].calculateGreenswitchCost(self.renSupply, self.curWorkload, self.workloadBuffer, self.gridPrice, self.renPrice)
        # self.greenswitchStat.append(greenswitchCost)
        # # print('greenswithCost = ', greenswitchCost)

        # self.curWorkload, self.workloadBuffer = self.mod['predsmoo'].workloadSmoothing(self.curWorkload, self.workloadBuffer, self.workloadStat)
        # print('smoothed workload=', self.curWorkload)
        return


    def updates(self,renState):
        # self.mod['update'].updateWorkloadRatio(self.workloadStat)
        self.gridpriceState = self.mod['update'].updateGridPriceState(self.gridpriceStat, self.gridPrice)
        # workloadState = self.mod['update'].updateWorkloadState(self.curWorkload,renState)
        # self.upsAbility, self.upsState = self.mod['update'].updateUpsUtilityLevel(workloadState)
        ########################
        # define renewable state
        # we need to figure out how to define fluctuate and tell why we still use grid as
        # much as possible when grid price is low(by always set a low price), otherwise we lost our motivation
        self.renState = self.mod['predsmoo'].defineRenState(self.renSupply, self.renSupplyStat, self.mod['input'].get_renewableData())
        ##############################
        return


    def ren_fluctuate(self):
        self.fluRenSupplyStat.append(self.renSupply)
        # print('fluRenSupplyStat = ',self.fluRenSupplyStat)
        stableRenSupply = self.mod['predsmoo'].getStableRenSupply(self.fluRenSupplyStat)
        # print('stableRenSupply = ', stableRenSupply)
        self.renSupply, self.upsStorage, stableGridSupply, upsSupplyFlu = self.mod['predsmoo'].renSupplySmooth(self.gridpriceState, self.gridPrice, self.renSupply, self.renPrice, stableRenSupply, self.upsAbility, self.upsStorage)
        # print('renSupply after smooth=', self.renSupply, 'stableGridSupply', stableGridSupply)
        return stableGridSupply, upsSupplyFlu


    def update_ups(self, upsSupplyFlu):
        # decide whether discharge or recharge UPS
        upsSupply, self.upsStorage = self.mod['update'].updateUpsSupply(self.gridpriceState, self.curWorkload, self.mod['input'].get_data_center_pow_cap_dynamic(self.renState), self.renState, self.upsStorage, upsSupplyFlu)
        print('upsSupply=', upsSupply, 'upsStorage=', self.upsStorage)
        # waste renSupply if it is still higher than curWorkload
        if self.renSupply + upsSupply > self.curWorkload:
            self.renSupply = self.curWorkload - upsSupply
            print('renSUpply is now ', self.renSupply)
        return round(upsSupply,3)

    def calculate_costs(self):
        # calculate redux cost
        reduxCost = self.gridPrice * self.gridSupply + self.renPrice * self.renSupply + self.mod['input'].upsPrice * abs(self.upsSupply)
        # reduxCost = reduxCost / 10000000
        reduxCost = round(reduxCost,2)
        print('reduxCost=', reduxCost, '\n', '\n')
        self.reduxStat.append(reduxCost)
        # # we need to notice there are cases when cost with redux is higer than cost without redux, due to recharge the UPS batteries.
        # costGapStat.append(noReduxCost - reduxCost)
        # if costGapStat[curTime] < 0:
        #     specialCase.append(curTime)
        # if greenswitchCost < reduxCost:
        #     self.specialCase.append(curTime)
        ###################
        # self.reduxAccu.append(sum(self.reduxStat))
        # self.noRenAccu.append(sum(self.noRenStat))
        ####################
        # self.greenswitchAccu.append(sum(self.greenswitchStat))
        return reduxCost
