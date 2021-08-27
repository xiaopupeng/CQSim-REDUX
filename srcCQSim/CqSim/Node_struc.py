from datetime import datetime
import time
import re

__metaclass__ = type

class Node_struc:
    def __init__(self):
        self.myInfo = "Node Structure"
        self.nodeStruc = []
        self.job_list = []
        self.predict_node = []
        self.predict_job = []
        self.tot = -1
        self.idle = -1
        self.avail = -1

    ##################
    # functional methods
    def reset(self):
        self.nodeStruc = []
        self.job_list = []
        self.predict_node = []
        self.tot = -1
        self.idle = -1
        self.avail = -1

    def get_tot(self):
        return self.tot

    def get_idle(self):
        return self.idle

    def get_avail(self):
        return self.avail

    def read_list(self,source_str):
        result_list=[]
        regex_str = "[\[,]([^,\[\]]*)"
        result_list=re.findall(regex_str,source_str)
        for item in result_list:
            item=int(item)
        return result_list

    ##############
    # import node info
    def import_node_file(self, node_file):
        regex_str = "([^;\\n]*)[;\\n]"
        nodeFile = open(node_file,'r')
        self.nodeStruc = []

        i = 0
        while (1):
            tempStr = nodeFile.readline()
            if not tempStr :    # break when no more line
                break
            temp_dataList=re.findall(regex_str,tempStr)
            # print(temp_dataList)
            tempInfo = {"id": int(temp_dataList[0]), \
                          "location": self.read_list(temp_dataList[1]), \
                          "group": int(temp_dataList[2]), \
                          "state": int(temp_dataList[3]), \
                          "proc": int(temp_dataList[4]), \
                          "start": -1, \
                          "end": -1, \
                          "extend": None}
            self.nodeStruc.append(tempInfo)
            i += 1
        nodeFile.close()
        self.tot = len(self.nodeStruc)
        self.idle = self.tot
        self.avail = self.tot
        return

    def import_node_config (self, config_file):
        regex_str = "([^=\\n]*)[=\\n]"
        nodeFile = open(config_file,'r')
        config_data={}

        while (1):
            tempStr = nodeFile.readline()
            if not tempStr :    # break when no more line
                break
            temp_dataList=re.findall(regex_str,tempStr)
            print(temp_dataList)
            config_data[temp_dataList[0]]=temp_dataList[1]
        nodeFile.close()

    # expecting this method works for output
    def import_node_data(self, node_data):
        self.nodeStruc = []

        temp_len = len(node_data)
        i=0
        while (i<temp_len):
            temp_dataList = node_data[i]

            tempInfo = {"id": temp_dataList[0], \
                          "location": temp_dataList[1], \
                          "group": temp_dataList[2], \
                          "state": temp_dataList[3], \
                          "proc": temp_dataList[4], \
                          "start": -1, \
                          "end": -1, \
                          "extend": None}
            self.nodeStruc.append(tempInfo)
            i += 1
        self.tot = len(self.nodeStruc)
        self.idle = self.tot
        self.avail = self.tot


    ########################
    # node control methods for simulating
    def is_available(self, proc_num):
        result = 0
        if self.avail >= proc_num:
            result = 1
        return result

    def node_allocate(self, proc_num, job_index, start, end):
        if self.is_available(proc_num) == 0:
            return 0
        self.idle -= proc_num
        self.avail = self.idle
        temp_job_info = {'job':job_index, 'end': end, 'node': proc_num}
        j = 0
        is_done = 0
        while (j<len(self.job_list)):
            if (temp_job_info['end']<self.job_list[j]['end']):
                self.job_list.insert(j,temp_job_info)
                is_done = 1
                break
            j += 1

        if (is_done == 0):
            self.job_list.append(temp_job_info)
        return 1

    def node_allocate_backup(self, proc_num, job_index, start, end):
        if self.is_available(proc_num) == 0:
            return 0
        # update node status
        i = 0
        for node in self.nodeStruc:
            if node['state'] < 0:
                node['state'] = job_index
                node['start'] = start
                node['end'] = end
                i += 1
            if (i >= proc_num):
                break
        self.idle -= proc_num
        self.avail = self.idle
        # job info relate to node
        temp_job_info = {'job':job_index, 'end': end, 'node': proc_num}
        j = 0
        is_done = 0
        while (j<len(self.job_list)):
            if(temp_job_info['end']<self.job_list[j]['end']):
                self.job_list.insert(j,temp_job_info)
                is_done = 1
            j += 1
        if (is_done == 0):
            self.job_list.append(temp_job_info)
        return 1

    def node_release(self, job_index, end):
        temp_node = 0
        j = 0
        # print('job_index=',job_index,'job_list=',self.job_list)
        while (j<len(self.job_list)):
            if (job_index==self.job_list[j]['job']):
                temp_node = self.job_list[j]['node']
                break
            j += 1

        self.idle += temp_node
        self.avail = self.idle
        self.job_list.pop(j)
        return 1

    def node_release_backup(self, job_index, end):
        # update node status
        i = 0
        for node in self.nodeStruc:
            if node['state'] == job_index:
                node['state'] = -1
                node['start'] = -1
                node['end'] = -1
                i += 1
        # release node
        temp_node = 0
        j = 0
        while (j<len(self.job_list)):
            if (job_index==self.job_list[j]['job']):
                temp_node = self.job_list[j]['node']
                break
            j += 1
        self.idle += temp_node
        self.avail = self.idle
        self.job_list.pop(j)
        return 1
