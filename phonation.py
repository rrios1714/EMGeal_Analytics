import streamlit as st
import h5py
from numpy import sort, arange


def main():
    st.title('Pharyngeal EMG Experiment.')

    ##### Make sidebar
    with st.sidebar:
        uploaded_file = st.file_uploader(
                label   = 'Choose subject files',
                type    = ['hdf5'] 
        ) 
        if not uploaded_file:
            st.stop()
        f = h5py.File(uploaded_file, 'r')
        st.success('File received.')
        balloons()

        with st.form("my_form"):
            # Title
            st.write("Visualization Toolbox")

            # Subject information
            sub_id = st.radio(
                label   = 'Select subject',
                options = f.keys(),
            )
            task = st.radio(
                label       = 'Select phonation task',
                options     = ['lo', 'hi'],
                format_func = lambda str: 'low pitch' if str=='lo' else 'high pitch'
            )
            rep = st.number_input(
                label='Select repetition of interest:',
                min_value=1,
                max_value=10,
                value=10,
                step=1,
            )
            rep = int(rep-1)    # python indexing
            chs_semg = st.multiselect(
                label       = 'Channels to plot',
                options     = list(range(20)),
                default     = [9, 10],
                format_func = lambda x: x+1,
            )
            chs_nemg = st.multiselect(
                label       = 'Channels to plot',
                options     = list(range(3)),
                default     = 0,
                format_func = lambda x: x+1,
            )

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
        # Pre-process form outputs
        pointer     = f'{sub_id}/{task}/{rep}'
        chs_semg    = sort(chs_semg)
        chs_nemg    = sort(chs_nemg)

    ##### Create figures
    import matplotlib.pyplot as plt

    fig_audio = plt.figure(figsize=(15,2))
    time = arange(len(f[f'{pointer}/audio'][:]))/48000
    plt.plot(time, f[f'{pointer}/audio'][:])
    plt.xlabel('Time (sec)', fontsize=20)
    plt.yticks([])
    # plt.xticks([])
    plt.tight_layout()

    fig_semg = plt.figure(figsize=(15,5))
    for i, signal in enumerate(f[f'{pointer}/sEMG'][chs_semg]):
        time = arange(len(signal))/4000
        plt.plot(time, normalize(signal) - 3*i, label=f'Ch {chs_semg[i] + 1}')
    plt.xlabel('Time (sec)', fontsize=18)
    plt.yticks([])
    plt.legend()

    fig_nemg = plt.figure(figsize=(15,5))
    for i, signal in enumerate(f[f'{pointer}/nEMG'][chs_nemg]):
        time = arange(len(signal))/4000
        plt.plot(time, normalize(signal) - 6*i, label=f'Ch {chs_nemg[i] + 1}', color=f'C{chs_nemg[i]}')
    plt.xlabel('Time (sec)', fontsize=18)
    plt.yticks([])
    plt.legend()

    ##### Create additional files
    from scipy.io.wavfile import write
    write('audio.wav', rate=48000, data=f[f'{pointer}/audio'][:])

    ##### Create main screen
    st.header(f'Subject {sub_id[1]}. Repetition {rep+1}.')
    st.subheader('audio')
    st.audio(data='audio.wav', format='audio/wav')
    st.pyplot(fig_audio)
    
    
    st.subheader('surface-EMG')
    st.pyplot(fig_semg)

    st.subheader('needle-EMG')
    st.pyplot(fig_nemg)

@st.cache(suppress_st_warning=True)
def balloons():
    st.balloons()


def normalize(x):
    return (x-x.mean())/x.std()

if __name__ == "__main__":
    main()