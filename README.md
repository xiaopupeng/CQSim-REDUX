This is a integration project between the REDUX system we developed before and the CQSim simulator of workload scheduler. From this integration, we can build a solide foundation of power consumption of workload trace for the previous REDUX system.

## REDUX - A management system integrating distributed UPS units and renewable energy for workload requirements in data centers

...

## CQSim - A Trace-based Event-Driven Scheduling Simulator
The official site of documents and source code for this project can be found [here](http://bluesky.cs.iit.edu/cqsim/).

For a easier understanding of this project and future integrating of this project with REDUX system, I have made the following update:

- [x] Uninstalled the whole debug system from every where. I found it not very useful from developer's perspective, but makes the whole simulator complicated.
- [x] Deleted the command line option system from cqsim.py to make everything more clear and easy to understand.
- [x] Got rid of the config file which may cause confusion, and keep a simple inputPara dictionary as the list of all parameters in need.
- [x] Reorder methods by catagories and add comments at all necessary place in each module.
- [X] Merged cqsim and cqsim_main
- [x] Other debug work

The testing data I use is also from the Parallel Workloads Archive, and the exact log can be found [here](http://www.cs.huji.ac.il/labs/parallel/workload/l_sdsc_sp2/index.html), and the simulating results are at [this folder](https://github.com/xiaopupeng/REDUX-CQSim/tree/master/data/Results)

I will cite the paper (_X. Yang et al., Proc. of SC'13, 2013_) as required when conducting experiments of in my future papers.

## CQSim-REDUX (temp name)
### milestone update (08/22/2019)
- [x] Went through simulation related modules carefully and made necessary revision
- [x] Rebuilt the scoring system in basic_algorithm() module (for the waiting list) depends on the priority queue where each job belongs to
- [x] Built the 1st version of Power module include:
	1. complete version of power_profile() method to fetch job power profile
	2. First version of power_aware() method for power supply status
- [x] Build simple greedy scheduling method for start_window module
- [x] combined Node_struc_SWF() into Node_struc() for reading convinience
- [x] other necessary change & debug

### plan of next steps
- [ ] update and integrate REDUX module into the system
- [ ] update power_aware() method with REDUX with more sophisticated algorithm
- [ ] revision power_profile() method for REDUX system(and new paper)
- [ ] 
