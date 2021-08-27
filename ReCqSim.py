
class ReCqSim:
    def __init__(self, module_list_cq, module_list_re):
        self.myInfo = "ReCqSim"
        self.CQmod = module_list_cq
        self.REmod = module_list_re
        self.timeInterval = 3600 # interval of time slot in seconds
        self.curTime = self.CQmod['job'].jobTrace[0]['submit'] # first job submit time

        # REDUX variables
        self.renSupplyStat = []

        # CQSim variables
        self.waitQueue = []

        # workloadList
        self.workloadList = []

        print('>>>>>>>>>>>>>> ReCqSim modules list:')
        for module_name in self.CQmod:
            temp_name = self.CQmod[module_name].myInfo
            print(temp_name+" ................... Load")

        for module_name in self.REmod:
            temp_name = self.REmod[module_name].myInfo
            print(temp_name+" ................... Load")

    def reset(self):
        pass


    ### main method ###
    ### NEED TO CONSIDER: after job profiling, the workload in kW/h is submitted to the REDUX, then the workload simulator is REDUX. REDUX then send the smoothed workload back to cqsim, which then decide how much job can be executed during this time slot, and put extra job back into the waiting queue(at the first places)
    def ReCqSim(self):
        print('======================','StartSim','======================')
        curHour = 0
        dataSize = self.REmod['input'].get_data_size()
        print('data size >>>>>>>>>>>>>>>>>>>>', dataSize)
        ###### need to be updated
        dataCenterCap = self.REmod['update'].data_center_cap()
        print('data center Capabiliy >>>>>>>>>>>>>>>>>>>>', dataCenterCap)
        #########################
        self.CQmod['CQsim'].fill_jobList()
        while curHour < dataSize:
            print('>>>>>>>>>>>>>>>>> current time (in hours):', curHour)
            renState = self.get_renState(curHour)
            dataCenterCap = self.CQmod['CQsim'].dataCenterCap(renState, dataCenterCap)
            workload, self.workloadList = self.CQmod['CQsim'].renaware_workload(self.curTime, renState, dataCenterCap)
            self.curTime += self.timeInterval
            self.REmod['REsim'].redux_sim(curHour, workload, renState)
            # pausedJob = self.REmod['REsim'].redux_sim(curHour, workload)
            curHour += 1
        self.print_result()
        return

    def get_renState(self, curHour):
        renSupply = self.REmod['input'].get_renewable(curHour)
        self.renSupplyStat.append(renSupply)
        ########################
        # define renewable state
        # we need to figure out how to define fluctuate and tell why we still use grid as much as possible when grid price is low(by always set a low price)
        renState = self.REmod['predsmoo'].defineRenState(renSupply, self.renSupplyStat, self.REmod['input'].get_renewableData())
        ##############################
        if renState == 'stable' or renState == 'fluctuate':
            renState = 'available'
        ##############################
        return renState



    def print_result(self):
        pass
