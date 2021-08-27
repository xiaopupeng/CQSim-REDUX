
__metaclass__ = type

import copy

class Start_window:
    def __init__(self, mode = 0, ad_mode = 0, power_module = None, para_list = [5,0,0]):
        self.myInfo = "Start Window"
        self.mode = mode
        self.ad_mode = ad_mode
        self.power_module = power_module
        self.para_list = para_list

        if (len(self.para_list)>=1 and int(self.para_list[0]) > 0):
            self.win_size = int(self.para_list[0])
            #[5, 0, 0] will go here, win_size = 5
        else:
            self.win_size = 1
        if (len(self.para_list)>=2 and int(self.para_list[1]) > 0):
            self.check_size_in = int(self.para_list[1])
        else:
            self.check_size_in = self.win_size # =5
            #[5, 0, 0] will go here
        if (len(self.para_list)>=3 and int(self.para_list[2]) > 0):
            self.max_start_size = int(self.para_list[2])
        else:
            self.max_start_size = self.win_size # =5
            #[5, 0, 0] with go here
        self.temp_check_len = self.check_size_in

        self.current_para = []
        self.seq_list = []
        self.reset_list()

    ##################
    # functional methods
    def reset (self, mode = None,  ad_mode = None, node_module = None, para_list = None):
        if mode:
            self.mode = mode
        if ad_mode:
            self.ad_mode =ad_mode
        if node_module:
            self.node_module = node_module
        if power_module:
            self.power_module = power_module
        if para_list:
            self.para_list = para_list
            if (self.para_list[0] and self.para_list[0] > 0):
                self.win_size = self.para_list[0]
            else:
                self.win_size = 1
            if (self.para_list[1] and self.para_list[1] > 0):
                self.check_size_in = self.para_list[1]
            else:
                self.check_size_in = self.win_size
            if (self.para_list[2] and self.para_list[2] > 0):
                self.max_start_size = self.para_list[2]
            else:
                self.max_start_size = self.win_size
        self.current_para = []
        self.seq_list = []
        self.score_base = score_base
        self.reset_list()

    def window_adapt (self, para_in = None):
        return 0

    def window_size (self):
        return self.win_size

    def check_size (self):
        return self.check_size_in

    # Return the number of the jobs which are started before next window
    def start_num (self):
        return self.max_start_size

    def reset_list (self):
        self.seq_list = []
        self.temp_list=[]
        self.wait_job = []
        temp_seq=[]
        i = 0
        ele = []
        while (i<self.check_size_in):
            ele.append(i)
            self.temp_list.append(-1)
            i += 1
        self.build_seq_list(self.check_size_in, ele, self.check_size_in-1)

    def build_seq_list(self, seq_len, ele_pool, temp_index):
        if (seq_len<=1):
            self.temp_list[temp_index]=ele_pool[0]
            temp_seq_save = self.temp_list[:]
            self.seq_list.append(temp_seq_save)
        else:
            i = seq_len - 1
            while (i>=0):
                self.temp_list[temp_index] = ele_pool[i]
                temp_ele_pool = ele_pool[:]
                temp_ele_pool.pop(i)
                self.build_seq_list(seq_len-1,temp_ele_pool,temp_index-1)
                i -= 1

    ################
    # main methods
    def start_window (self, wait_job, para_in = None):
        self.current_para = para_in
        self.wait_job = []
        i = 0
        while (i < self.win_size and i < len(wait_job)):
            self.wait_job.append(wait_job[i])
            i += 1
        if i > self.check_size_in:
            i = self.check_size_in
        self.temp_check_len = i

        # Different window mode can be added by designing a new window method and build the relationship between mode number and window function here
        result = []
        # if self.mode == 0:
        #     result = self.window_greedy_noren()
        #     print(">>>>>>>>>>. ",result)
        if self.mode == 1:
            result = self.window_greedy()
            print(">>>>>>>>>>. ",result)
        elif self.mode == 2:
            result = self.window_check()
            print(">>>>>>>>>>. ",result)
        else: # no window
            i = 0
            temp_list=[]
            while (i < self.temp_check_len):
                temp_list.append(self.wait_job[i]['index'])
                i += 1
            return temp_list
        return result

    # need to rewrite
    def window_greedy(self):
        # get compare list of windonw
        profile_cmp_list = []
        i = 0
        while(i<len(self.wait_job)):
            profile_cmp_list.append([self.wait_job[i]['index'],self.wait_job[i]['score'],self.wait_job[i]['powProfile']])
            i+=1
        # sort the compare list under power supply status
        power_supply = self.power_module.power_aware()
        # print(power_supply)
        if power_supply['ren']=='available' or power_supply['grid']=='low':
            profile_cmp_list.sort(key=lambda x: x[-1]) # without ren
        elif power_supply['ren']=='outage':
            profile_cmp_list.sort(key=lambda x: x[-1], reverse=True) # with ren
        # put high priority job at the beginning of window list
        k = 0
        while(k<len(profile_cmp_list)):
            if profile_cmp_list[k][1] > self.score_base * 5:
                high_prio_job = profile_cmp_list.pop(k)
                profile_cmp_list.insert(0,high_prio_job)
            k+=1
        # assign sorted index to window_job_list
        j = 0
        win_job_list = []
        while(j < len(profile_cmp_list)):
            win_job_list.append(profile_cmp_list[j][0])
            j+=1
        return win_job_list


    # Do the window check and return the reordered sequence of the input job list.
    def window_check (self):
        temp_wait_list = []
        temp_wait_listB = []
        temp_last = -1
        print('self.temp_check_len=',self.temp_check_len)
        if (self.temp_check_len == 1):
            print([self.wait_job[0]['index']])
            return [self.wait_job[0]['index']]

        temp_max = 1
        i = 1
        while (i<=self.temp_check_len):
            temp_max = temp_max * i   # = (win_size)
            i += 1
        print('temp_max=',temp_max)

        i = 0
        while (i < temp_max):
            j = 0
            temp_index = 0
            self.node_module.pre_reset(self.current_para['time'])
            while (j < self.temp_check_len):
                temp_index =self.node_module.reserve(self.wait_job[self.seq_list[i][j]]['proc'], self.wait_job[self.seq_list[i][j]]['index'], self.wait_job[self.seq_list[i][j]]['run'], index = temp_index)
                j += 1

            if (temp_last == -1 or temp_last>self.node_module.pre_get_last()['end']):
                temp_last = self.node_module.pre_get_last()['end']
                temp_wait_list = self.seq_list[i]
            i += 1

        i = 0
        while (i<self.temp_check_len):
            temp_wait_listB.append(self.wait_job[temp_wait_list[i]]['index'])
            i += 1

        return temp_wait_listB
