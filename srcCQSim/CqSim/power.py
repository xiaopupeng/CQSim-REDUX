

__metaclass__ = type

import random
import numpy as np

class Power:
    def __init__(self, job_module=None): # add para from redux later
        self.myInfo = "Power"
        self.power_status = []
        self.grid_status = []
        self.ren_status = []
        self.ups_status = []
        self.job_module = job_module
        self.timeslots = 1
        self.profileBase = 20

    def reset(self):
        self.grid_status = []
        self.ren_status = []
        self.ups_status = []

    # get power status of each sources from redux
    def power_aware(self, renState, gridPriceState):
        grid_prices = ['on-peak', 'off-peak']
        self.grid_status = random.choice(grid_prices)

        result = {'grid':self.get_grid_state(), 'ren': renState}
        return result

    # get power profile of a job
    def power_profile(self, job_index=-1):
        temp_job = self.job_module.job_info(job_index)
        proc_num, req_time = temp_job['reqProc'], temp_job['reqTime']
        ########
        # get normal distributed power profile of each processor(node) between 20~60W
        ########
        proc_profile = np.random.normal(size=proc_num) * self.profileBase + self.profileBase*2
        proc_profile = np.round(proc_profile, decimals=2)
        i=0
        while(i<len(proc_profile)): # assign boundray value to outsiders
            if proc_profile[i] > self.profileBase*3:
                proc_profile[i] = self.profileBase*3
            elif proc_profile[i] < self.profileBase:
                proc_profile[i] = self.profileBase
            i+=1
        power_result = np.sum(proc_profile) * req_time # in Watt
        return round(power_result)

    # get power profile for each job in the window
    def window_powerProfile(self,window,renState):
        i=0
        while (i<len(window)):
            proc_num, req_time = window[i]['proc'], window[i]['run']
            #########
            # get normal distributed power profile of each processor(node) between 20~60W
            #########
            proc_profile = np.random.normal() * self.profileBase + self.profileBase*2
            proc_profile = round(proc_profile, 2)
            if proc_profile > self.profileBase*3:
                proc_profile = self.profileBase*3
            elif proc_profile < self.profileBase:
                proc_profile = self.profileBase
            power_result = proc_profile * req_time
            window[i]['power'] = round(power_result, 2)
            i+=1
        return window


    def get_grid_state(self): # add grid data para
        grid_prices = ['on-peak', 'off-peak']
        self.grid_status = random.choice(grid_prices)
        return self.grid_status

    def get_renewable_state(self): # add ren data para
        renewable_supply = ['max', 'medium', 'min']
        self.renewable_status = random.choice(renewable_supply)
        return self.renewable_status
