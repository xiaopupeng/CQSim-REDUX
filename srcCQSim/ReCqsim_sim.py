import srcCQSim.IOModule.Log_print as Log_print
# import IOModule.Log_print as Log_print
import copy


__metaclass__ = type

class Cqsim_sim:
    def __init__(self, module_list):
        self.myInfo = "Cqsim Sim"
        self.module = module_list

        self.job_num = len(self.module['job'].job_info())
        self.currentTime = 0
        self.curTime = self.module['job'].jobTrace[0]['submit']
        self.timeInterval = 3600 # interval of time slot in seconds
        #########################
        self.HPCtoDC_scale = 4  #8
        #########################

        self.jobList = []
        self.waitQueue = []
        self.window = []
        self.notFilledProcList = []
        ######
        # maintain a started job list to keep started job running
        # OR: give started job a 0 priority and reorder to execute first every time
        self.startedJob = []
        ######

        self.newJob = 0
        self.oldWaitQueueLen = 0
        self.windowSize = 0
        self.jobPointer = 0
        self.currentJob = None

        self.workload = 0
        self.norWorkload = 0
        self.workloadList = []
        self.norWorkloadList = []

        for module_name in self.module:
            temp_name = self.module[module_name].myInfo
            print(temp_name+" ................... Load")

    def reset(self, module_list = None):
        pass

    def windowSize(self):
        return self.windowSize

    def fill_jobList(self):
        i = 0
        print('job_num = >>>>>>>>>>>>>>',self.job_num)
        while (i < self.job_num):
            self.insert_job(
            id = self.module['job'].job_info(i)['id'],
            time = self.module['job'].job_info(i)['submit'],
            run = self.module['job'].job_info(i)['reqTime'],
            proc = self.module['job'].job_info(i)['reqProc'],
            priority = self.module['job'].job_info(i)['num_queue'],
            para=[1,i])
            i += 1
        # print('init whole job list >>>>>>>>>>>>>>', self.jobList)
        return self.jobList


    def insert_job(self, id, time, run, proc, priority, para):
        new_job = {'id':id, 'time':time, 'run':run, 'proc':proc, 'priority':priority, 'para':para}
        temp_index = -1
        i = self.jobPointer
        ### locate the insert index or not ###
        # compare every job in jobList with new job
        while(i < len(self.jobList)):
            # if ith job submit time = new job submit time
            if (self.jobList[i]['time']==new_job['time']):
                # if ith job priority > new job priority
                if (self.jobList[i]['priority']>priority):
                    temp_index = i
                    break
            # if ith job submit time > new job submit time
            elif (self.jobList[i]['time']>new_job['time']):
                temp_index = i
                break
            i += 1
        # insert the event at the end of jobList
        if (temp_index >= len(self.jobList) or temp_index == -1):
            self.jobList.append(new_job)
        # if the insert locate is decided
        else:
            self.jobList.insert(temp_index,new_job)
        return


    ##############
    # no need in jupyter,  should be included if experimenting here
    def dataCenterCap(self, renState, dataCenterCap):
        if renState != 'available':
            dataCenterCap = dataCenterCap * 0.8
        return dataCenterCap
    ##############


    ### get the workload during one time slot ###
    ########
    # have to double check all started jobs won't be "stopped", but just "pasued"
    ########
    def renaware_workload(self, curTime, renState, dataCenterCap):
        curTime += self.timeInterval
        print('curTime>>>>>>>>>>>>>>>',curTime)
        print('dataCenterCap>>>>>>>>>>>>>>',dataCenterCap)
        # waitQueue = all the jobs arrived before curTime
        self.fill_waitQueue(curTime)
        # window = the actual ready-for-execute list of jobs
        self.fill_window(dataCenterCap)

        #############
        # 1. backfill the window (fill again) if renewable is available (only for batched trace data? NO:some jobs is arrived and run more than 1 hour)
        # 2. defer part of non-urgent job to the next slot if renewable is unavailalbe
        if renState == 'available':
            notFilledProc = dataCenterCap - self.windowSize
            print('notFilledProc = ', notFilledProc)
            self.backfill_window(dataCenterCap)
            notFilledProcBF = dataCenterCap - self.windowSize
            print('notFilledProc after backfill = ', notFilledProcBF)
            self.notFilledProcList.append([notFilledProc, notFilledProcBF])

        elif renState =='outage':
            notFilledProc = dataCenterCap - self.windowSize
            print('notFilledProc = ', notFilledProc)
            self.defer()
            notFilledProcDF = dataCenterCap - self.windowSize
            print('notFilledProc after defer = ', notFilledProcDF)

        else:
            Print('Error: no renState')
        #############
        self.windowSize = 0
        self.module['pow'].window_powerProfile(self.window,renState)
        ##########
        # did nothing if dataCenterCap is large enough
        self.reorder_window(renState)
        # non-greedy algorithm? 0-1 knapsack?
        # more renState state including grid price state?
        ##########

        self.workload = self.calculate_workload()
        self.workloadList.append(self.workload)
        self.window = []
        print('ren-aware workload>>>>>>>>>>>>>>>>>>>',self.workload)
        print("Start REDUX")
        return self.workload, self.workloadList

    def normal_workload(self, curTime, renState, dataCenterCap):
        curTime += self.timeInterval
        print('curTime>>>>>>>>>>>>>>>',curTime)
        # fill the waitQueue with all jobs
        self.fill_waitQueue(curTime)
        self.fill_window(dataCenterCap)
        self.windowSize = 0
        self.module['pow'].window_powerProfile(self.window,renState)
        self.norWorkload = self.calculate_workload()
        self.norWorkloadList.append(self.norWorkload)
        self.window = []
        print('normal workload>>>>>>>>>>>>>>>>>>>',self.norWorkload)
        print("Start REDUX")
        return self.norWorkload, self.norWorkloadList


    #########################################


    # waitQueue = all the jobs arrived before curTime
    def fill_waitQueue(self,curTime):
        self.oldWaitQueueLen = len(self.waitQueue)
        for i in range(len(self.jobList)):
            if self.jobList[i]['time'] < curTime:
                self.waitQueue.append(self.jobList[i])
            else:
                j = i
                break
        self.newJob = j
        while j > 0:
            self.jobList.remove(self.jobList[0])
            j -= 1
        return


    ########
    # maintain a started job list to keep started job running
    # OR: give started job a 0 priority and reorder to execute first every time
    ########
    # window = the actual ready-for-execute list of jobs
    def fill_window(self, dataCenterCap):
        # count window length under window size limit
        windowLen = self.oldWaitQueueLen
        i = self.oldWaitQueueLen
        while i < len(self.waitQueue):
            if self.windowSize + self.waitQueue[i]['proc'] <= dataCenterCap:
                self.windowSize += self.waitQueue[i]['proc']
                windowLen = i + 1
            else:
                windowLen = i
                break
            i += 1

        # fill window with window length
        removeList = []
        i = 0
        while i < windowLen:
            self.window.append(copy.deepcopy(self.waitQueue[i]))
            if self.window[-1]['run'] > 3600:
                self.window[-1]['run'] = 3600
                self.waitQueue[i]['run'] -= 3600
            else:
                self.windowSize -= self.waitQueue[i]['proc']
                removeList.append(i)
            i += 1

        ### should REVERSE remove the <3600sec jobs from waitQueue
        for i in reversed(removeList):
            self.waitQueue.remove(self.waitQueue[i])
        # print('waitQueue after remove >>>>>>>>>>',self.waitQueue)
        return


    ###############
    # backfill if renewable is available
    # need to interact with fill_window to fill middle finished jobs
    ###############
    def backfill_window(self, dataCenterCap):
        # count window length under window size limit
        i = 0
        while i < len(self.waitQueue):
            if self.windowSize + self.waitQueue[i]['proc'] <= dataCenterCap:
                self.windowSize += self.waitQueue[i]['proc']
                if self.waitQueue[i]['run'] < 3600:
                    removed = self.waitQueue.pop(i)
                    self.window.append(removed)
                else:
                    self.window.append(copy.deepcopy(self.waitQueue[i]))
                    self.window[-1]['run'] = 3600
                    self.waitQueue[i]['run'] -= 3600
            i += 1
        return

        # fill window with window length
        removeList = []
        i = 0
        while i < windowLen:
            self.window.append(copy.deepcopy(self.waitQueue[i]))
            if self.window[-1]['run'] > 3600:
                self.window[-1]['run'] = 3600
                self.waitQueue[i]['run'] -= 3600
            else:
                self.windowSize -= self.waitQueue[i]['proc']
                removeList.append(i)
            i += 1

        ### should REVERSE remove the <3600sec jobs from waitQueue
        for i in reversed(removeList):
            self.waitQueue.remove(self.waitQueue[i])
        # print('waitQueue after remove >>>>>>>>>>',self.waitQueue)
        return

    def defer(self):
        i = 0
        while i < len(self.window):
            if self.window[i]['priority'] >= 2:
                removed=self.window.pop(i)
                self.windowSize -= removed['proc']
                if removed['run'] <= 3600:
                    self.waitQueue.insert(0,removed)
                else:
                    j = 0
                    while j<len(waitQueue):
                        if removed['id'] == self.waitQueue[j]['id']:
                            self.waitQueue[j]['run']+=3600
                        j+=1
            i+=1
        return

    # maintain a started job list to keep started job running
    # OR: give started job a 0 priority and reorder to execute first every time
    def reorder_window(self, renState):
        # get compare list of windonw
        profile_cmp_list = []
        i = 0
        while(i<len(self.window)):
            profile_cmp_list.append([self.window[i]['id'], self.window[i]['time'], self.window[i]['run'], self.window[i]['proc'], self.window[i]['priority'],self.window[i]['para'], self.window[i]['power']])
            i+=1
        print('>>>>>>>>>>>>>>>>>>>>>renState=',renState)
        if renState == 'available':
            profile_cmp_list.sort(key=lambda x: x[-1], reverse=True)
        elif renState == 'outage':
            profile_cmp_list.sort(key=lambda x: x[-1])
        else:
            print('Error: no renState')
        # put high priority job at the beginning of window list
        k = 0
        while(k<len(profile_cmp_list)):
            if profile_cmp_list[k][-3] == 1:
                high_prio_job = profile_cmp_list.pop(k)
                profile_cmp_list.insert(0,high_prio_job)
            k+=1
        for i in range(len(self.window)):
            self.window[i]['id'] = profile_cmp_list[i][0]
            self.window[i]['time'] = profile_cmp_list[i][1]
            self.window[i]['run'] = profile_cmp_list[i][2]
            self.window[i]['proc'] = profile_cmp_list[i][3]
            self.window[i]['priority'] = profile_cmp_list[i][4]
            self.window[i]['para'] = profile_cmp_list[i][5]
            self.window[i]['power'] = profile_cmp_list[i][6]
        return


    def calculate_workload(self):
        accuWorkload = 0
        for i in range(len(self.window)):
            accuWorkload += self.window[i]['power']
        accuWorkload = self.HPCtoDC_scale * round(accuWorkload / 1000, 2) # kW/h
        return accuWorkload
    #     # for workload
    #     for i in range(len(self.window)):
    #         self.workload += self.window[i]['power']
    #     self.workload = self.HPCtoDC_scale * round(self.workload / 1000, 2)


    ### self.sys_collect() ###
    def sys_collect(self):
        temp_inter = 0
        if (self.jobPointer+1<len(self.waitQueue)):
            temp_inter = self.waitQueue[self.jobPointer+1]['time'] - self.currentTime
        temp_size = 0

        event_code=None
        if (self.waitQueue[self.jobPointer]['type'] == 1):
            if (self.waitQueue[self.jobPointer]['para'][0] == 1):
                event_code='S' #job start
            elif(self.waitQueue[self.jobPointer]['para'][0] == 2):
                event_code='E' #job end
        elif (self.waitQueue[self.jobPointer]['type'] == 2):
            event_code='Q' #submit

        self.module['info'].info_collect(time=self.currentTime, event=event_code, uti=(self.module['node'].get_tot()-self.module['node'].get_idle())*1.0/self.module['node'].get_tot(), waitNum=len(self.module['job'].wait_list()), waitSize=self.module['job'].wait_size(), inter=temp_inter)
        self.module['output'].print_sys_info(self.module['info'].get_info(self.module['info'].get_len()-1))
        return

    def print_result(self):
        self.module['output'].print_result(self.module['job'])
