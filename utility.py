import numpy as np

# generate float levels
def generate_float_levels(min_val, max_val, step):
    return list(np.arange(min_val,max_val + step,step))

# generate integer levels
def generate_levels(min_val, max_val, step):
    return list(range(min_val, max_val + step, step))