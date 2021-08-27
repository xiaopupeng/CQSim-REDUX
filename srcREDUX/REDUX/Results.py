import numpy as np
import pandas as pd

class Results:
    def __init__(self):
        self.myInfo = 'Results'
        pass

    def reset(self):
        pass


    # Need NEW DESIGN: all workloads are done by grid power
    def calculateNoRedux(self):
        pass


    # calculate greenswitchCost (noRedux, but with renewable energy)
    def calculateGreenswitchCost(self, renSupply, curWorkload, workloadPool, gridPrice, renPrice):
        if renSupply > curWorkload:
            renSupply = curWorkload
        greenswitchCost = gridPrice * (curWorkload + workloadPool - renSupply) + renPrice * renSupply
        return greenswitchCost
