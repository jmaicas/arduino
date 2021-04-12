import pyfirmata
import numpy as np
import pandas as pd
import xlsxwriter
#from seaborn.palettes import cubehelix_palette

pin = 1 # analog pin to receive the obstacle info
pin_out = 12 # digital pin to send the trigger info
time_min = 5 # time in minutes to run the experiment
total_time = time_min*60 # in seconds
delay_time = 0  # delay after stimulus 0 is not delay
thres_betw_interv = 1 # delay before allowing another stimulation

# Parameters to follow the protocol in Carlezon & Chartoff (2007)
stim_len = 0.44
sampling_freq = 20 #141 # Hz
sampling_time = 1/sampling_freq # in seconds
half_sampling = sampling_time/2

# Creates a new board 
board = pyfirmata.Arduino('COM7') # Windows
#board = pyfirmata.Arduino('/dev/ttyACM0') # Linux
print("Setting up the connection to the board ...")
it = pyfirmata.util.Iterator(board)
it.start()
 
# Start reporting for define pin
board.analog[pin].enable_reporting()
 
# Run until the total time is reached
counter = 0
count_betw_interv = 5

delay_after_stimulus = delay_time
delay_stimulus = False
keep_stimulus = False
took_nose_out = True
stim_times = np.zeros(int(total_time/sampling_time))
c = 0

# todo the rat should not get another stimulation before 0.5 s

for i in np.arange(0, total_time, sampling_time):
    c = c + 1
    #print("\n Checking state at second %f" % i)
    #print("Pin %i : %s" % (pin, board.analog[pin].read()))
    if board.analog[pin].read() is not None:
      
      if (board.analog[pin].read() > 0.75):
        
        if counter < stim_len and took_nose_out and count_betw_interv > thres_betw_interv:
          board.digital[pin_out].write(1)
          keep_stimulus = True    
          count_betw_interv = 0
          #stim_times[c] = 1
        elif counter > stim_len:
          took_nose_out = False
          board.digital[pin_out].write(0)
          count_betw_interv = count_betw_interv + sampling_time
          counter = 0
          keep_stimulus = False
        elif count_betw_interv <= thres_betw_interv:
          took_nose_out = False
          count_betw_interv = count_betw_interv + sampling_time

          
        counter = counter + sampling_time

      else:
        count_betw_interv = count_betw_interv + sampling_time
        if counter < stim_len and keep_stimulus:
          board.digital[pin_out].write(1)
          counter = counter + sampling_time
          #stim_times[c] = 1
        else:
          took_nose_out = True
          counter = 0
          board.digital[pin_out].write(0)
          keep_stimulus = False
    else:
      print("Pin with no value")

    board.pass_time(sampling_time)

#df_stim = pd.DataFrame({'Column1': stim_times})

#df_stim.to_excel('output.xlsx')
 
board.exit()