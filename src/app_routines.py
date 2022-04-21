import numpy as np
from streamlit import experimental_memo     # Caching functions

from src.database import mats2dict
@experimental_memo(max_entries=2)
def import_data(sub, out=True, **kwargs):
    '''IMPORT DATA. Connects with mat files in data folder                         *****************
                    and pre-process the signals with filters 
                    and standardization procedure.    

    INPUT 
    sub - subject identification
    out - if signals are pre-processed (Default: True)
    kwargs - {standardize: True/False} see pre_process()

    OUTPUT
    fs  - sampling frequency of experiment
    x   - signals indexed by time (..., time)
    t_c - time of clicks in experiment (2, 30) or ([start, end], sw_num)
    '''
    # Import mat files as a dictionary
    subject = mats2dict(sub_load=[sub])
    # Import sampling frequency, recording, timestamps
    fs = subject['Sampling Frequency']
    x = subject['Recording']
    t_c = (subject['Timestamps'].reshape(-1, 2)*fs).astype(int)
    # Test for pre-processing step
    if out:
        x = pre_process(x, fs, **kwargs)
    # Return sampling frequency, recording, timestamps
    return fs, x, t_c

from scipy.signal import butter, sosfiltfilt
def pre_process(x, fs, standardize=True):
    '''PRE-PROCESSING WORKFLOW filter to apply to data prior to handling.

    INPUT 
    x   - signals indexed by time (..., time)
    fs  - sampling frequency of signal
    out - if output is standardized or not

    OUTPUT
    x  - filtered and z-scored signals
    '''
    # Construct filters
    sos_notch = butter(N=8, Wn=(57.5, 62.5), btype='bandstop', output='sos', fs=fs)
    sos_emg = butter(N=8, Wn=(40, 500), btype='bandpass', output='sos', fs=fs)
    
    # Apply filter
    x = sosfiltfilt(sos_emg, x=sosfiltfilt(sos_notch, x)) # double filter

    # Standardize (optional)
    if standardize:
        x = zscore_independent_special(x, fs=fs)
    
    return x

def zscore_independent_special(x, fs, rest_domain = [5, 120]):
    '''ZSCORE INDEPENDENT SPECIAL returns the z-score of each channel where 
                    the rest period of the experiment occured during 'rest_domain'

    INPUT 
    x - data with time in the last axis
    fs - sampling frequency of experiment
    rest_domain - time (in seconds) at which resting occured; input as the inclusive domain [a,b].
                    default is the first 2 minutes of data, with 5 seconds of settle time.

    OUTPUT
    xo - z-scored datacube
    '''
    # Compute channel statistics within the time domain [a,b]
    a,b = [int(x*fs) for x in rest_domain]
    x_mu = x[...,a:b].mean(axis=-1)
    x_std = x[...,a:b].std(axis=-1)

    # Standardize every channel
    for ij in np.ndindex(x.shape[:-1]):
        x[ij] = (x[ij] - x_mu[ij])/(x_std[ij])
    return x    # X[a, b] ~ N(mu=[0, 0, ..., 0], std=I)