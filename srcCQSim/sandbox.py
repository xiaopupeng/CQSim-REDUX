
wait_job = [{'index':5,'score':4356,'powProfile':100},{'index':8,'score':2345,'powProfile':200},{'index':2,'score':565,'powProfile':300}]

def window_greedy(wait_job):

    profile_cmp_list = []
    i = 0
    while(i<len(wait_job)):
        profile_cmp_list.append([wait_job[i]['index'],wait_job[i]['powProfile']])
        i+=1

    profile_cmp_list.sort(key=lambda x: x[1]) # with ren

    # profile_cmp_list.sort(key=lambda x: x[1], reverse=true) # without ren

    # assign sorted index to job_wait_list
    i = 0
    wait_job_list = []
    while(i < len(profile_cmp_list)):
        wait_job_list.append(profile_cmp_list[i][0])
        i+=1
    return wait_job_list

result = window_greedy(wait_job)
print(result)

# ===========================
# aaa= [1,2,3,4,5]
# bbb=['a','b','c']
# print(aaa)
# aaa[0:0]=bbb
# print(aaa)

#=============================
# import numpy as np
# power_profile = np.random.normal(size=12) * 20 + 40
# power_profile = np.round(power_profile, decimals=2)
# i=0
# while(i<len(power_profile)):
#     if power_profile[i]>60:
#         power_profile[i] = 60
#     if power_profile[i]<20:
#         power_profile[i] = 20
#     i+=1
# print(power_profile)
