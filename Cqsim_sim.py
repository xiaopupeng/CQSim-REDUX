import srcCQSim.IOModule.Log_print as Log_print
# import IOModule.Log_print as Log_print

__metaclass__ = type

class Cqsim_sim:
    def __init__(self, module_list, monitor = None, mode=None):
        self.myInfo = "Cqsim Sim"
        self.module = module_list
        self.monitor = monitor
        self.mode = mode
        self.event_seq = []
        self.event_pointer = 0
        self.monitor_start = 0
        self.current_event = None
        self.job_num = len(self.module['job'].job_info())
        self.currentTime = 0
        self.realTime = 0

        for module_name in self.module:
            temp_name = self.module[module_name].myInfo
            print(temp_name+" ................... Load")

    def reset(self, module_list = None, monitor = None):
        if module:
            self.module = module_list
        if monitor:
            self.monitor = monitor
        self.event_seq = []
        self.event_pointer = 0
        self.monitor_start = 0
        self.current_event = None
        self.job_num = len(self.module['job'].job_info())
        self.currentTime = 0
        self.realTime = 0

    ### main method ###
    def cqsim_sim(self):
        self.insert_event_job()
        self.scan_event()
        self.print_result()
        print("------ Simulating Done!")
        return

    ### self.insert_event_job() ###
    def insert_event_job(self):
        i = 0
        while (i < self.job_num):
            self.insert_event(
            time=self.module['job'].job_info(i)['submit'],
            priority=self.module['job'].job_info(i)['num_queue'],
            para=[1,i])
            i += 1
        # print('event_seq = ',self.event_seq)
        return

    def insert_event(self, time, priority, para = None):
        temp_index = -1
        # time = submit time
        new_event = {"time":time, "prio":priority, "para":para}
        if (type == 1): # job
        # set for the monitor, always =0 for the first insert round
        i = self.event_pointer
        ### locate the insert index or not ###
        # compare every job in event_seq with new job
        while(i < len(self.event_seq)):
            # if ith job submit time = new job submit time
            if (self.event_seq[i]['time']==time):
                # if ith job priority > new job priority
                if (self.event_seq[i]['prio']>priority):
                    temp_index = i
                    break
            # if ith job submit time > new job submit time
            elif (self.event_seq[i]['time']>time):
                temp_index = i
                break
            i += 1

        # insert the event at the end of event_seq
        if (temp_index >= len(self.event_seq) or temp_index == -1):
            self.event_seq.append(new_event)
        # if the insert locate is decided
        else:
            self.event_seq.insert(temp_index,new_event)

    ########################

    ### self.scan_event() ###
    def scan_event(self):
        self.current_event = None
        # event_pointer remains 0 when first scan starts

        while (self.event_pointer < len(self.event_seq)):
            self.current_event = self.event_seq[self.event_pointer]
            ###################
            # current time = the submit time of a new job
            self.currentTime = self.current_event['time']
            ###################
            ### event start ###
            self.event_job(self.current_event['para'])
            #################
            self.sys_collect()
            self.interface()
            self.event_pointer += 1
        return
    ##########################

        ### self.event_job / self.event_monitor / self.event_extend ###
    # Deal with the job event (submit/finish).
    # Calculate the scores of the waiting job after the event is done.
    # Call the start scan method group: window - start new job - backfill
    # Store the system information.
    # Insert monitor event from current time to time of the next event.
    # Call the user interface module to show the current system state.
    def event_job(self, para_in = None):
        # para:[1,i][2,i] 0: submit one hour event 1: submit event 2: finish event
        # if (self.curret_event['para'][0] == 0):
        #     self.submit_onehour(self.current_event['para'][1])
        if (self.current_event['para'][0] == 1):
            print('start current_event=',self.current_event)
            self.submit(self.current_event['para'][1])
        elif (self.current_event['para'][0] == 2):
            print('finish current_event=',self.current_event)
            self.finish(self.current_event['para'][1])
        # get the score from Basic_algorithm
        ############
        # self.score_calculate()
        ############
        # reorder wait list
        self.start_scan()
        if (self.event_pointer < len(self.event_seq)-1):
            self.insert_event_monitor(self.currentTime, self.event_seq[self.event_pointer+1]['time'])
        return

        #########################

    def submit(self, job_index):
        self.module['job'].job_submit(job_index)
        return

    def finish(self, job_index):
        self.module['node'].node_release(job_index,self.currentTime)
        self.module['job'].job_finish(job_index)
        return

    # Calculate the score for all jobs in waiting list.
    # Reorder the waiting list depending on the score list.
    def score_calculate(self):
        wait_list = self.module['job'].wait_list()
        temp_wait=[]
        i = 0
        while(i < len(wait_list)):
            temp_job = self.module['job'].job_info(wait_list[i])
            temp_wait.append(temp_job)
            i += 1
        # print(temp_wait)
        # currentTime = submit time of current event
        score_list = self.module['alg'].get_score(temp_wait, self.currentTime)
        # update score list to job trace and sort the wait list
        self.module['job'].refresh_score(score_list)
        return

    # Scan the jobs in waiting list till no job can be start or backfill.
    # Window function will be used before job start.
    # Backfill function will be used when no job can be started.
    def start_scan(self):
        start_max = self.module['win'].start_num() # window size
        temp_wait = self.module['job'].wait_list() # list of waiting jobs
        win_count = start_max
        i = 0
        while (i < len(temp_wait)):
            # only win_count >= start_win_size, then call window algo
            if(win_count >= start_max):
                win_count = 0
                print('wait list before window=',temp_wait)
                temp_wait = self.start_window(temp_wait)
                print('wait list after window=',temp_wait)

            temp_job = self.module['job'].job_info(temp_wait[i])
            print('current running job=',temp_wait[i])
            # if available # of processors > requested processors
            if(self.module['node'].is_available(temp_job['reqProc'])):
                # get the job started
                print('the job is available')
                self.start(temp_wait[i])
            ################################
            # Needs DeBug
            # if available # of processors is not enough try backfill
            # else:
            #     print('try backfill')
            #     temp_wait = self.module['job'].wait_list()
            #     self.backfill(temp_wait)
            #     break
            ################################
            win_count += 1
            i += 1
        return

                ### self.start_scan ###
    # Call the window function to modify the order of the waiting job.
    # Return the new reorderred list.
    def start_window(self, temp_wait):
        win_size = self.module['win'].window_size()
        # split the wait list into window and rest list
        if (len(temp_wait) > win_size):
            window_job = temp_wait[0:win_size]
            temp_wait = temp_wait[win_size:]
        else:
            window_job = temp_wait
            temp_wait = []
        # collect job info in window
        window_job_info = []
        i = 0
        while (i < len(window_job)):
            temp_job = self.module['job'].job_info(window_job[i])
            window_job_info.append({
            "index":window_job[i],
            "proc":temp_job['reqProc'],
            # "time":temp_job[i]['reqTime'],
            # "node":temp_job[i]['usedProc'],
            # "cpuTime":temp_job[i]['usedAveCPU'],
            "run":temp_job['run'],
            "score":temp_job['score'],
            "powProfile":self.module['pow'].power_profile(window_job[i])
            })
            i += 1
        # reorder the window
        window_job = self.module['win'].start_window(window_job_info,{"time":self.currentTime})
        # insert reorderred window at the biginning of wait list
        temp_wait[0:0] = window_job
        return temp_wait

    def start(self, job_index):
        # 1. node allocate (need a return of 1?)
        self.module['node'].node_allocate(self.module['job'].job_info(job_index)['usedProc'], job_index, self.currentTime, self.currentTime + self.module['job'].job_info(job_index)['usedAveCPU'])
        # 2.job start (need a return of 1?)
        self.module['job'].job_start(job_index, self.currentTime)
        # 3. insert job finish event
        self.insert_event(1,self.currentTime+self.module['job'].job_info(job_index)['run'],1,[2,job_index]) # 2 in [2,job_index] indicate finish event from event_job
        return

    def backfill(self, temp_wait):
        temp_wait_info = []
        max_num = len(temp_wait)
        i = 0
        while (i < max_num):
            temp_job = self.module['job'].job_info(temp_wait[i])
            temp_wait_info.append({"index":temp_wait[i],"proc":temp_job['reqProc'],"node":temp_job['reqProc'],"run":temp_job['run'],"score":temp_job['score']})
            i += 1
        backfill_list = self.module['backfill'].backfill(temp_wait_info, {'time':self.currentTime})
        if not backfill_list:
            return 0

        for job in backfill_list:
            self.start(job)
        return 1
                ####################

    ### self.sys_collect() ###
    def sys_collect(self):
        temp_inter = 0
        if (self.event_pointer+1<len(self.event_seq)):
            temp_inter = self.event_seq[self.event_pointer+1]['time'] - self.currentTime
        temp_size = 0

        event_code=None
        if (self.event_seq[self.event_pointer]['type'] == 1):
            if (self.event_seq[self.event_pointer]['para'][0] == 1):
                event_code='S' #job start
            elif(self.event_seq[self.event_pointer]['para'][0] == 2):
                event_code='E' #job end
        elif (self.event_seq[self.event_pointer]['type'] == 2):
            event_code='Q' #submit

        self.module['info'].info_collect(time=self.currentTime, event=event_code, uti=(self.module['node'].get_tot()-self.module['node'].get_idle())*1.0/self.module['node'].get_tot(), waitNum=len(self.module['job'].wait_list()), waitSize=self.module['job'].wait_size(), inter=temp_inter)
        self.module['output'].print_sys_info(self.module['info'].get_info(self.module['info'].get_len()-1))
        return

    def print_result(self):
        self.module['output'].print_result(self.module['job'])
