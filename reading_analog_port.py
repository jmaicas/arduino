import pyfirmata
import numpy as np
#from seaborn.palettes import cubehelix_palette

pin = 1 # analog pin to receive the obstacle info
pin_out = 12 # digital pin to send the trigger info
time_min = 10 # time in minutes to run the experiment
total_time = time_min*60 # in seconds
delay_time = 0  # delay after stimulus 0 is not delay


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
count_betw_interv = 0
delay_after_stimulus = delay_time
delay_stimulus = False
keep_stimulus = False
took_nose_out = True

# todo the rat should not get another stimulation before 0.5 s

for i in np.arange(0, total_time, sampling_time):
    #print("\n Checking state at second %f" % i)
    #print("Pin %i : %s" % (pin, board.analog[pin].read()))
    if board.analog[pin].read() is not None:
      
      if (board.analog[pin].read() > 0.75):
        
        if counter < stim_len and took_nose_out and count_betw_interv > 0.5:
          board.digital[pin_out].write(1)
          keep_stimulus = True    
          count_betw_interv = 0
        elif counter > stim_len:
          took_nose_out = False
          board.digital[pin_out].write(0)
          count_betw_interv = count_betw_interv + sampling_time
          counter = 0
          keep_stimulus = False
        elif count_betw_interv <= 0.5:
          count_betw_interv = count_betw_interv + sampling_time

          
        counter = counter + sampling_time

      else:
        took_nose_out = True
        count_betw_interv = count_betw_interv + 1
        if counter < stim_len and keep_stimulus:
          board.digital[pin_out].write(1)
          counter = counter + sampling_time
        else:
          counter = 0
          board.digital[pin_out].write(0)
          keep_stimulus = False
    else:
      print("Pin with no value")

    board.pass_time(sampling_time)
 
board.exit()