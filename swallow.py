import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

from src.app_routines import import_data

def main():
    st.title('Visualization of a swallow')

    with st.sidebar:
        sub_id = st.number_input(
            label='Select subject ID:',
            min_value=1,
            max_value=8,
            value=7,
            step=1,
            # format='%d',
        )
        sw = st.number_input(
            label='Select swallow of interest:',
            min_value=1,
            max_value=30,
            value=10,
            step=1,
        )
        chs = st.multiselect(
            label='Channels to plot',
            options=range(1,21),
            default=[10, 11]
        )
    sw-=1   # indexing at zero
    chs = np.array(chs) - 1

    #Import data
    fs, x, tc = import_data(sub_id, out=True) 
    t = np.arange(x.shape[-1])/fs

    #Create figure
    start, stop = tc[sw]
    slice_sw = np.s_[start:stop]
    fig, ax = plt.subplots(1, 1, figsize=(10,7))
    for i, signal in enumerate(x[chs]):
        ax.plot(t[slice_sw], signal[slice_sw]-20*i)
    st.pyplot(fig)

if __name__ == "__main__":
    main()