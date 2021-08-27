import os
from datetime import datetime
import time
import re
import pandas as pd
import numpy as np

import sys
path_main='/Users/xiaopupeng/dropbox/workspace/cqsim-redux/'
path_data=path_main+'data/'
redux_src=path_main+'srcREDUX/'
cqsim_src=path_main+'srcCQSim/'
sys.path.append(path_main)
# sys.path.append(redux_src)
# sys.path.append(cqsim_src)

### CQSim modules ###
# preprocess
import srcCQSim.Filter.Filter_job_SWF as FilterJob
import srcCQSim.CqSim.Job_trace as JobTrace
import srcCQSim.Filter.Filter_node_SWF as FilterNode
import srcCQSim.CqSim.Node_struc as NodeStruc
# algorithms
import srcCQSim.CqSim.Start_window as StartWindow
# record the results
import srcCQSim.CqSim.Info_collect as InfoCollect
# import srcCQSim.Output_log as OutputLog

# new module of renewable energy aware
import srcCQSim.CqSim.power as Power
# simulator
import srcCQSim.ReCqsim_sim as CqsimSim

### REDUX modules ###
import srcREDUX.REDUX.DataIO as dataIO
import srcREDUX.REDUX.Update as update
import srcREDUX.REDUX.Predict_Smooth as predict_smooth
import srcREDUX.REDUX.Results as results
import srcREDUX.ReduxSim as ReduxSim

import ReCqSim

# assign default value to all parameters
def initCQ():
    inputCQ = {
    ### job trace name and save file names ###
    # 'job_trace': 'test2.swf',
    # 'node_struc': 'test2.swf',
    # 'output': 'output_test2',
    # 'job_save': 'jobSave_test2',
    # 'node_save': 'nodeSave_test2',
    'job_trace': 'SDSC-SP2-1998-4.2-cln.swf',
    'node_struc': 'SDSC-SP2-1998-4.2-cln.swf',
    'output': 'output_SDSC-SP2-1998-4.2-cln',
    'job_save': 'jobSave_SDSC-SP2-1998-4.2-cln',
    'node_save': 'nodeSave_SDSC-SP2-1998-4.2-cln',
    ### system config ###
    'cluster_fraction': 1.0,
    'start': 0.0,
    'start_date': 'None',
    'anchor': 0,
    'read_num': 8000,
    ### algorithm config ###
    # w:job wait time s: submit time t: requested time n: requested processors q:priority queue
    'win': 1, # =1 for window_check mode, other for no check
    'win_para': ['5', '0', '0'],
    #start window module parameter: [window size],[check size],[max start size],[max window size]
    ### config of names ###
    'config': 'config.set',
    'pre_name': "CQSIM_",
    'path_in': path_data+'InputCQSim/',
    'path_out': path_data+'Results/',
    'path_fmt': path_data+'Fmt/',
    # 'ext_jr': '.rst',
    # 'ext_si': '.ult',
    # 'ext_ai': '.adp',
    #### 0:Read original file  1:Read formatted file ###
    'resource_job': 0,
    'resource_node': 0
    }
    return inputCQ

def initRE():
    inputRE = {
    # ### CONSTANT ###
    # ratio of stats count when start the arithmetic average estimate
    'scaleRatio': 0.01,
    # ability of ups devise, could be more sophisticated in future (kWh)
    'upsCapability': 500,
    # the workload processing capability of data center (in processors)
    # 'dataCenterCap': 2500,
    'nodNum': 1152,
    'procPerNode': 8,
    # ups and renewable energy price ($)
    'upsPrice': 0.02,
    'solarPrice': 0.09,
    'windPrice': 0.15,
    # ### INITIALIZE ###
    # the initialized threshold of grid price ($)
    'initGridpriceThreshold': 1.0,
    # initialized high and low ratio of current workload for workload shaving
    'initCurWorkloadRatio': 0.2,
    # initialized stable renewable supply level
    'initStableRenSupply': 500,
    ### config of names ###
    'path_in': path_data+'InputREDUX/',
    'path_out': path_data+'REDUXResults/'
    }
    return inputRE

#this method is for jupyter exp
def showInputAndSetName(inputCQ, inputRE):
    print( "...................." )
    for item in inputCQ:
        print( str(item) + ": " + str(inputCQ[item]) )
    print( "...................." )
    for item in inputRE:
        print( str(item) + ": " + str(inputRE[item]) )
    print( "...................." )
    return


def recq_main(inputCQ, inputRE):
    print( "...................." )
    for item in inputCQ:
        print( str(item) + ": " + str(inputCQ[item]) )
    print( "...................." )
    for item in inputRE:
        print( str(item) + ": " + str(inputRE[item]) )
    print( "...................." )

    # if not os.path.exists(para_list['path_fmt']):
    #     os.makedirs(para_list['path_fmt'])
    # if not os.path.exists(para_list['path_out']):
    #     os.makedirs(para_list['path_out'])

    # all the names
    trace_name = inputCQ['path_in'] + inputCQ['job_trace']
    # struc_name = inputCQ['path_in'] + inputCQ['node_struc']
    save_name_j = inputCQ['path_fmt'] + inputCQ['job_save'] + '.csv'
    # save_name_n = inputCQ['path_fmt'] + inputCQ['node_save'] + '.csv'
    config_name_j = inputCQ['path_fmt'] + inputCQ['job_save'] + '.txt'
    # config_name_n = inputCQ['path_fmt'] + inputCQ['node_save'] + '.txt'

    # output para list
    # output_sys = inputCQ['path_out'] + inputCQ['output'] + inputCQ['ext_si']
    # output_adapt = inputCQ['path_out'] + inputCQ['output'] + inputCQ['ext_ai']
    # output_result = inputCQ['path_out'] + inputCQ['output'] + inputCQ['ext_jr']
    # output_fn = {'sys':output_sys, 'adapt':output_adapt, 'result':output_result}

    ### CQSim modules ###
    print( ".................... Job Filter" )
    module_filter_job = FilterJob.Filter_job_SWF(trace=trace_name, save=save_name_j, config=config_name_j)
    module_filter_job.read_job_trace()
    module_filter_job.output_job_data()
    module_filter_job.output_job_config()

    print( ".................... Job Trace" )
    module_job_trace = JobTrace.Job_trace(start=inputCQ['start'],num=inputCQ['read_num'],anchor=inputCQ['anchor'],density=inputCQ['cluster_fraction'])
    module_job_trace.import_job_file(save_name_j)
    module_job_trace.import_job_config(config_name_j)

    print("................ Power Profile")
    module_pow = Power.Power(job_module=module_job_trace)
    # power profile input: 1.processors 2.runtime
    # power supply input:

    print( ".................... Start Window" )
    module_win = StartWindow.Start_window(mode=inputCQ['win'],power_module=module_pow,para_list=inputCQ['win_para'])

    print( ".................... Information Collect" )
    module_info_collect = InfoCollect.Info_collect()

    # # Output Log
    # print( ".................... Output Log" )
    # module_output_log = OutputLog.Output_log (output=output_fn)

    ### REDUX modules ###
    print(".................... Data Input")
    input_module = dataIO.DataIO(inputPara = inputRE)
    input_module.loadData()
    inputRE['dataSize'] = input_module.data_size
    print('data size:', inputRE['dataSize'])

    print(".................... Update")
    update_module = update.Update(inputPara=inputRE)

    print(".................... Predict&Smooth")
    predict_smooth_module = predict_smooth.Predict_Smooth(inputRE, update_module)

    print(".................... Smooth")
    results_module = results.Results()

    # print(".................... Print Output")
    # output_module = dataIO.DataIO(inputRE)

    # Cqsim Simulator
    print( ".................... Cqsim Simulator" )
    module_list_cq = {
    'job':module_job_trace,
    'win':module_win,
    'pow':module_pow,
    'info':module_info_collect
    # 'output':module_output_log
    }
    module_CQsim = CqsimSim.Cqsim_sim(module_list=module_list_cq)
    module_list_cq['CQsim']=module_CQsim

    # REDUX Simulator
    print(".................... Redux Simulator")
    module_list_re = {
    'input':input_module,
    'update': update_module,
    'predsmoo': predict_smooth_module,
    'results': results_module
    # 'output':output_module
    }
    module_REsim = ReduxSim.Redux_Sim(module_list=module_list_re)
    module_list_re['REsim']=module_REsim

    # Integraded Simulator
    print(".................... ReCq Simulator")
    module_sim = ReCqSim.ReCqSim(module_list_cq=module_list_cq, module_list_re=module_list_re)
    ### Call simulator ###
    print('\n','\n','\n')
    print('======================','StartSim','======================')
    module_sim.ReCqSim()

if __name__ == "__main__":
    inputCQ=initCQ()
    inputRE=initRE()
    recq_main(inputCQ, inputRE)
