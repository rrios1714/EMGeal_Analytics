from os import listdir
from json import load
from scipy.io import loadmat
from pandas import read_csv
import numpy as np

def mats2dict(dir = './data/', sub_load = [7], fVerbose = True):
    '''Get matlab files from the folder storing all raw data and import them as dictionaries.
    INPUT
    dir         - directory where data is stored in
    sub_load    - subject to load
    fVerbose    - prints subject imported along with some imformation

    OUTPUT
    subjects    - returns either a single dictionary or a nested dictionary of subjects - depends if sub_load is on len == 1 or len > 1.
    '''
    files = listdir(dir)   # List all files in the raw data dump.
    mat_files = [file for file in files if file[-4:] == '.mat'] # Get all files with the extension .mat
    with open(dir+'subject_information.txt', 'r') as json_file:
        subjects_fs = load(json_file)

    subjects = {}    # Initialize an empty dictionary.
    for filename in mat_files:  # Iterate across matlab files from our data/raw directory
        # Extract experiment information from filename.
        a,b,c = (filename.find(word) for word in ['S','E','.mat'])
        sub_id, expt_id = int(filename[a+1:b]), filename[b+1:c] 
        if sub_id not in sub_load:
            continue
        else:
            # Initialize a subject if it does not yet exist. (Still need to add an else case, but it's not a problem yet.)
            if not sub_id in subjects.keys():
                subjects[sub_id] = {}

            # Add experiment information to the subject dictionary.
            subjects[sub_id]['Information'] = expt_id

            # Assign recording data to the dictionary structure. Stored as a numpy array because it is handled better.
            mat_file = loadmat(dir+filename)
            variable_name = list(mat_file.keys())[-1]           # Some recordings have different variable names, but typically our data of interest is the last one.
            recording = np.array(mat_file[variable_name])
            mask = recording.any(axis=0)                        # Apply mask to recording to remove shorted segments that occur at the end of the signal.
            recording = recording[:,mask]  
            subjects[sub_id]['Recording'] = np.array(recording)
            
            # For now we will assume they are all 2000. But some are 4000.
            fs = subjects_fs[str(sub_id)]  # Quick fix: For some reason json stores objects as strings, not bytes.
            subjects[sub_id]['Sampling Frequency'] = fs

            # Add subject's clicker information to the subject dictionary. In samples.
            clicker_time = read_csv(dir+filename[:-4]+'_events.csv')['Seconds']
            sub_fixed = [3,5]
            if sub_id in sub_fixed:     # Fix subjects 3 and 5 whose experiments (rest/swallow) were appended.
                mask = np.logical_xor(mask[1:],mask[:-1])
                start_swallow_experiment = np.where(mask == 1)[0][1]
                clicker_time = clicker_time + start_swallow_experiment/fs
            subjects[sub_id]['Timestamps'] = np.array(clicker_time)
        
    # Print information about the subject structure.
    if fVerbose:
        print('Subjects imported: ', *subjects.keys())
        print('Subject information: ', *subjects[next(iter(subjects))].keys(), sep='\t')
        
    if len(subjects.keys()) == 1:
        return subjects[next(iter(subjects))]
    else:
        return subjects