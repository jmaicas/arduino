import pyfirmata
import numpy as np
import pandas as pd
import xlsxwriter
import datetime

###############################################
### Parameters to change between recordings ###
###############################################
recordings_number = 10 
# folder to store the recordings. It needs a double \ to separate folders
folder = 'C:\\Users\\thoma\\'

# time in minutes to run the experiment
time_min = 5 # in minutes
# delay before allowing another stimulation
thres_betw_interv = 1 # in seconds

# Arduino pins to write to or read from
pin = 1 # analog pin to receive the obstacle info
pin2 = 2 # analog pin to receive the second obstacle info
pin_out = 12 # digital pin to send the trigger info
pin_outduplicated = 10 # to light the led #1
pin2_out = 8 # digital pin to send the trigger info
pin2_outduplicated = 6 # to light the led #2

total_time = time_min*60 # in seconds

# Parameters to follow the protocol in Carlezon & Chartoff (2007)
stim_len = 0.44  # it should be 0.5s but the TTL hardware that receives the arduino signal 
                 # produces a 0.5s pulse when receives an slightly shorter pulse
sampling_freq = 20 #141 # Hz
sampling_time = 1/sampling_freq # in seconds
half_sampling = sampling_time/2

for rec in np.arange(recordings_number):
    
  # Run until the total time is reached
  poke_times = np.zeros(int(total_time/sampling_time))
  time = np.arange(0, total_time, sampling_time)

  c = 0

  
  for i in np.arange(0, total_time, sampling_time):
      a = np.random.random(1)[0]
      
      if a > 0.75:

          poke_times[c] = 1
          
      
      c = c + 1

  df_stim = pd.DataFrame({'Time': time, 'Poke in 1': poke_times})
  
  filename = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
  df_stim.to_excel(folder + 'record_' + str(rec+1) + '_' + filename + '.xlsx')
  print('Recording finished')