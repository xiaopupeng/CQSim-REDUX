from datetime import datetime
import time
import re

__metaclass__ = type

class Filter_job_SWF():
    def __init__(self, trace, save=None, config=None, sdate=None, start=-1, density=1.0, anchor=0, rnum=0):
        self.myInfo = "Filter Job"
        self.start = start
        self.sdate = sdate
        self.density = float(density)
        self.anchor = int(anchor)
        self.rnum = int(rnum)
        self.trace = str(trace)
        self.save = str(save)
        self.config = str(config)
        self.jobNum = -1
        self.jobList=[]
        self.reset_config_data()

    ################
    # functional methods
    def get_job_num(self):
        return self.jobNum

    def get_job_data(self):
        return self.jobList

    def reset(self, trace=None, save=None, config=None, sdate=None, start=None, density=None, anchor=None, rnum=None):
        if start:
            self.start = start
        if sdate:
            self.sdate = sdate
        if density:
            self.density = float(density)
        if anchor:
            self.anchor = int(anchor)
        if rnum:
            self.rnum = int(rnum)
        if trace:
            self.trace = str(trace)
        if save:
            self.save = str(save)
        if config:
            self.config = str(config)
        self.jobNum = -1
        self.jobList=[]

        self.reset_config_data()

    def reset_config_data(self):
        self.config_start=';'
        self.config_sep='\\n'
        self.config_equal=': '
        self.config_data=[]
        self.config_data.append({'name_config':'date','name':'StartTime','value':''})
        self.config_data.append({'name_config':'start_offset','name':None,'value':''})

    #############
    # main methods
    def read_job_trace(self):
        nr_sign =';'    # Not read sign. Mark the line not the job data
        sep_sign =' '   # The sign seperate data in a line

        jobFile = open(self.trace,'r')
        min_sub = -1
        temp_readNum=0
        temp_start=0
        while (temp_readNum<self.rnum or self.rnum<=0):
            #print temp_readNum,")(",temp_start
            tempStr = jobFile.readline()
            if not tempStr :    # break when no more line
                break
            if tempStr[0] != nr_sign:   # The job trace line
                if (temp_start>=self.anchor):
                    strNum = len(tempStr)
                    newWord = 1
                    k = 0
                    ID = ""     # 1
                    submit = ""    # 2
                    wait = ""    # 3
                    run = ""    # 4
                    usedProc = ""    # 5
                    usedAveCPU = ""    # 6
                    usedMem = ""    # 7
                    reqProc = ""    # 8
                    reqTime = ""    # 9
                    reqMem = ""    # 10
                    status = ""    # 11
                    userID = ""    # 12
                    groupID = ""    # 13
                    num_exe = ""    # 14
                    num_queue = ""    # 15
                    num_part = ""    # 16
                    num_pre = ""    # 17
                    thinkTime = ""    # 18

                    for i in range(strNum):
                        if (tempStr[i] == '\n'):
                            break
                        if (tempStr[i] == sep_sign):
                            if (newWord == 0):
                                newWord = 1
                                k = k+1
                        else:
                            newWord = 0
                            if k == 0:
                                ID=ID+ tempStr[i]
                            elif k == 1:
                                submit = submit + tempStr[i]
                            elif k == 2:
                                wait = wait + tempStr[i]
                            elif k == 3:
                                run = run + tempStr[i]
                            elif k == 4:
                            	usedProc = usedProc + tempStr[i]
                            elif k == 5:
                            	usedAveCPU = usedAveCPU + tempStr[i]
                            elif k == 6:
                            	usedMem = usedMem + tempStr[i]
                            elif k == 7:
                            	reqProc = reqProc + tempStr[i]
                            elif k == 8:
                            	reqTime = reqTime + tempStr[i]
                            elif k == 9:
                            	reqMem = reqMem + tempStr[i]
                            elif k == 10:
                            	status = status + tempStr[i]
                            elif k == 11:
                            	userID = userID + tempStr[i]
                            elif k == 12:
                            	groupID = groupID + tempStr[i]
                            elif k == 13:
                            	num_exe = num_exe + tempStr[i]
                            elif k == 14:
                            	num_queue = num_queue + tempStr[i]
                            elif k == 15:
                            	num_part = num_part + tempStr[i]
                            elif k == 16:
                            	num_pre = num_pre + tempStr[i]
                            elif k == 17:
                            	thinkTime = thinkTime + tempStr[i]

                    if (min_sub<0):
                        min_sub=float(submit)
                        if (self.start < 0):
                            self.start = min_sub
                        for con_data in self.config_data:
                            if not con_data['name'] and con_data['name_config'] == 'start_offset':
                                con_data['value'] = min_sub-self.start
                                break

                    tempInfo = {'id':int(ID),\
                                'submit':self.density*(float(submit)-min_sub)+self.start,\
                                'wait':float(wait),\
                                'run':float(run),\
                                'usedProc':int(usedProc),\
                                'usedAveCPU':float(usedAveCPU),\
                                'usedMem':float(usedMem),\
                                'reqProc':int(reqProc),\
                                'reqTime':float(reqTime),\
                                'reqMem':float(reqMem),\
                                'status':int(status),\
                                'userID':int(userID),\
                                'groupID':int(groupID),\
                                'num_exe':int(num_exe),\
                                'num_queue':int(num_queue),\
                                'num_part':int(num_part),\
                                'num_pre':int(num_pre),\
                                'thinkTime':int(thinkTime),\
                                'start':-1,\
                                'end':-1,\
                                'score':0,\
                                'state':0,\
                                'happy':-1,\
                                'estStart':-1}
                    # state: 0: not submit  1: waiting  2: running  3: done

                    if (self.input_check(tempInfo)>=0):
                        self.jobList.append(tempInfo)
                        temp_readNum+=1
                temp_start += 1
            else:
                for con_data in self.config_data:
                    if con_data['name']:
                        con_ex = con_data['name']+self.config_equal+"([^"+self.config_sep+"]*)"+self.config_sep
                        temp_con_List=re.findall(con_ex,tempStr)
                        if (len(temp_con_List)>=1):
                            con_data['value'] = temp_con_List[0]
                            break


        jobFile.close()
        self.jobNum = len(self.jobList)

    def input_check(self,jobInfo):
        if (int(jobInfo['run'])>int(jobInfo['reqTime'])):
            jobInfo['run']=jobInfo['reqTime']
        if (int(jobInfo['id'])<=0):
            return -2
        if (int(jobInfo['submit'])<0):
            return -3
        if (int(jobInfo['run'])<=0):
            return -4
        if (int(jobInfo['reqTime'])<=0):
            return -5
        if (int(jobInfo['reqProc'])<=0):
            return -6
        return 1

    ##################
    # fmt job output
    def output_job_data(self):
        if not self.save:
            print("Save file not set!")
            return

        sep_sign = ";"
        f2=open(self.save,"w")

        for jobResult_o in self.jobList:
            f2.write(str(jobResult_o['id']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['submit']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['wait']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['run']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['usedProc']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['usedAveCPU']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['usedMem']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['reqProc']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['reqTime']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['reqMem']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['status']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['userID']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['groupID']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['num_exe']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['num_queue']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['num_part']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['num_pre']))
            f2.write(sep_sign)
            f2.write(str(jobResult_o['thinkTime']))
            f2.write("\n")
        f2.close()

    def output_job_config(self):
        if not self.config:
            print("Config file not set!")
            return

        format_equal = '='
        f2=open(self.config,"w")

        for con_data in self.config_data:
            f2.write(str(con_data['name_config']))
            f2.write(format_equal)
            f2.write(str(con_data['value']))
            f2.write('\n')
        f2.close()
