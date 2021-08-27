from datetime import datetime
import time
__metaclass__ = type

class Info_collect:
    def __init__(self, alg_module = None):
        self.myInfo = "Info Collect"
        self.alg_module = alg_module
        self.sys_info = []
        
    def info_analysis(self):
        return 1

    def get_info(self, index):
        if index>=len(self.sys_info):
            return None
        return self.sys_info[index]

    def get_len(self):
        return len(self.sys_info)

    def reset(self, alg_module = None):
        if alg_module:
            self.alg_module = alg_module
        self.sys_information = []

    def info_collect(self, time, event, uti, waitNum = -1, waitSize = -1, inter = -1.0, extend = None):
        event_date = time
        temp_info = {'date': event_date, 'time': time, 'event': event, 'uti': uti, 'waitNum': waitNum, 'waitSize': waitSize, 'inter': inter, 'extend': extend}
        self.sys_info.append(temp_info)
