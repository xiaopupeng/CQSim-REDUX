from datetime import datetime
import time
import re

__metaclass__ = type

class Job_trace:
    def __init__(self, start=-1, num=-1, anchor=-1, density=1.0):
        self.myInfo = "Job Trace"
        self.start = start
        self.start_offset_A = 0.0
        self.start_offset_B = 0.0
        self.start_date = ""
        self.anchor = anchor
        self.read_num = num
        self.density = density
        self.jobTrace=[]

        self.reset_data()

    ##################
    # functional methods
    def reset_data(self):
        self.job_wait_size = 0
        self.job_submit_list=[]
        self.job_wait_list=[]
        self.job_run_list=[]
        self.job_done_list=[]

    def wait_size (self):
        return self.job_wait_size

    def submit_list (self):
        return self.job_submit_list

    def wait_list (self):
        return self.job_wait_list

    def run_list (self):
        return self.job_run_list

    def done_list (self):
        return self.job_done_list

    def reset(self, start=None, num=None, anchor=None, density=None):
        if start:
            self.anchor = start
            self.start_offset_A = 0.0
            self.start_offset_B = 0.0
        if num:
            self.read_num = num
        if anchor:
            self.anchor = anchor
        if density:
            self.density = density
        self.jobTrace=[]
        self.reset_data()


    ################
    # main methods
    def import_job_file (self, job_file):
        temp_start = self.start
        regex_str = "([^;\\n]*)[;\\n]"
        jobFile = open(job_file,'r')
        min_sub = -1 # Original submit time, or minimal submission
        self.jobTrace=[]
        self.reset_data()

        i = 0
        j = 0
        while (i<self.read_num or self.read_num<=0):
            tempStr = jobFile.readline()
            if not tempStr :    # break when no more line
                break
            # print(tempStr)
            if (j>=self.anchor):
                temp_dataList=re.findall(regex_str,tempStr)
                if (min_sub<0):
                    min_sub=float(temp_dataList[1])
                    if (temp_start < 0):
                        temp_start = min_sub
                    self.start_offset_B = min_sub-temp_start

                tempInfo = {'id':int(temp_dataList[0]),\
                            'submit':self.density*(float(temp_dataList[1])-min_sub)+temp_start,\
                            'wait':float(temp_dataList[2]),\
                            'run':float(temp_dataList[3]),\
                            'usedProc':int(temp_dataList[4]),\
                            'usedAveCPU':float(temp_dataList[5]),\
                            'usedMem':float(temp_dataList[6]),\
                            'reqProc':int(temp_dataList[7]),\
                            'reqTime':float(temp_dataList[8]),\
                            'reqMem':float(temp_dataList[9]),\
                            'status':int(temp_dataList[10]),\
                            'userID':int(temp_dataList[11]),\
                            'groupID':int(temp_dataList[12]),\
                            'num_exe':int(temp_dataList[13]),\
                            'num_queue':int(temp_dataList[14]),\
                            'num_part':int(temp_dataList[15]),\
                            'num_pre':int(temp_dataList[16]),\
                            'thinkTime':int(temp_dataList[17]),\
                            'start':-1,\
                            'end':-1,\
                            'score':0,\
                            'state':0,\
                            'happy':-1,\
                            'estStart':-1}
                # print(tempInfo)
                self.jobTrace.append(tempInfo)
                self.job_submit_list.append(i)
                i += 1
            j += 1
        jobFile.close()

    def import_job_config (self, config_file):
        regex_str = "([^=\\n]*)[=\\n]"
        jobFile = open(config_file,'r')
        config_data={}

        while (1):
            tempStr = jobFile.readline()
            if not tempStr :    # break when no more line
                break
            temp_dataList=re.findall(regex_str,tempStr)
            config_data[temp_dataList[0]]=temp_dataList[1]
        print(config_data)
        jobFile.close()
        self.start_offset_A = config_data['start_offset']
        self.start_date = config_data['date']

    # # See again the difference between import_job_file
    # # Store the income job data into the local list.
    # def import_job_data (self, job_data):
    #     temp_start=self.anchor
    #     min_sub = -1
    #     self.jobTrace=[]
    #     self.reset_list()
    #     data_len = len(job_data)
    #
    #     i = 0
    #     j = 0
    #     while ((i < data_len) and (i<self.read_num or self.read_num<=0)):
    #         if (j>=self.anchor):
    #             temp_dataList=job_data[i]
    #
    #             if (min_sub<0):
    #                 min_sub=float(temp_dataList[1])
    #                 if (temp_start < 0):
    #                     temp_start = min_sub
    #
    #             tempInfo = {'id':int(temp_dataList[0]),\
    #                         'submit':self.density*(float(temp_dataList[1])-min_sub)+temp_start,\
    #                         'wait':float(temp_dataList[2]),\
    #                         'run':float(temp_dataList[3]),\
    #                         'usedProc':int(temp_dataList[4]),\
    #                         'usedAveCPU':float(temp_dataList[5]),\
    #                         'usedMem':float(temp_dataList[6]),\
    #                         'reqProc':int(temp_dataList[7]),\
    #                         'reqTime':float(temp_dataList[8]),\
    #                         'reqMem':float(temp_dataList[9]),\
    #                         'status':int(temp_dataList[10]),\
    #                         'userID':int(temp_dataList[11]),\
    #                         'groupID':int(temp_dataList[12]),\
    #                         'num_exe':int(temp_dataList[13]),\
    #                         'num_queue':int(temp_dataList[14]),\
    #                         'num_part':int(temp_dataList[15]),\
    #                         'num_pre':int(temp_dataList[16]),\
    #                         'thinkTime':int(temp_dataList[17]),\
    #                         'start':-1,\
    #                         'end':-1,\
    #                         'score':0,\
    #                         'state':0,\
    #                         'happy':-1,\
    #                         'estStart':-1}
    #             self.jobTrace=[].append(tempInfo)
    #             self.job_submit_list.append(i)
    #             i += 1
    #         j += 1
    #     return

    ########################
    # job control methods for simulating
    def job_info (self, job_index = -1):
        if job_index == -1:
            return self.jobTrace
        return self.jobTrace[job_index]

    def get_jobTrace(self):
        return self.jobTrace

    def job_submit (self, job_index, job_est_start = -1):
        self.jobTrace[job_index]["state"]=1
        self.jobTrace[job_index]["estStart"]=job_est_start
        self.job_submit_list.remove(job_index)
        self.job_wait_list.append(job_index)
        self.job_wait_size += self.jobTrace[job_index]["reqProc"]
        return 1

    def job_submit_onehour (self, job_index, job_est_start = -1):
        self.jobTrace[job_index]["state"]=1
        self.jobTrace[job_index]["estStart"]=job_est_start
        self.job_submit_list.remove(job_index)
        self.job_wait_list.append(job_index)
        self.job_wait_size += self.jobTrace[job_index]["reqProc"]
        return 1

    def job_start (self, job_index, time):
        self.jobTrace[job_index]["state"]=2
        self.jobTrace[job_index]['start']=time
        self.jobTrace[job_index]['wait']=time - self.jobTrace[job_index]['submit']
        self.jobTrace[job_index]['end']=time + self.jobTrace[job_index]['run']
        self.job_wait_list.remove(job_index)
        self.job_run_list.append(job_index)
        self.job_wait_size -= self.jobTrace[job_index]["reqProc"]
        return 1

    def job_finish (self, job_index, time=None):
        self.jobTrace[job_index]["state"]=3
        if time:
            self.jobTrace[job_index]['end'] = time
        self.job_run_list.remove(job_index)
        self.job_done_list.append(job_index)
        return 1

    def job_fail (self, job_index, time=None):
        self.jobTrace[job_index]["state"]=4
        if  time:
            self.jobTrace[job_index]['end'] = time
        self.job_run_list.remove(job_index)
        self.fail_list.append(job_index)
        return 1
        
