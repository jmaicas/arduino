import pyfirmata
import numpy as np
from seaborn.palettes import cubehelix_palette

pin = 1 # analog pin to receive the obstacle info
pin_out = 12 # digital pin to send the trigger info
time_min = 60 # time in minutes to run the experiment
total_time = time_min*60 # in seconds
delay_time = 0  # delay after stimulus 0 is not delay


# Parameters to follow the protocol in Carlezon & Chartoff (2007)
stim_len = 0.5
sampling_freq = 4 # 141 # Hz
sampling_time = 1/sampling_freq # in seconds

# Creates a new board 
board = pyfirmata.Arduino('/dev/ttyACM0')
print("Setting up the connection to the board ...")
it = pyfirmata.util.Iterator(board)
it.start()
 
# Start reporting for define pin
board.analog[pin].enable_reporting()
 
# Run until the total time is reached
counter = 0
delay_after_stimulus = # delay_time
delay_stimulus = False

for i in np.arange(0, total_time, sampling_time):
    #print("\n Checking state at second %f" % i)
    #print("Pin %i : %s" % (pin, board.analog[pin].read()))
    if board.analog[pin].read() is not None:
      # Delay stimulus is 
      if (delay_stimulus is True) and (delay_after_stimulus > 0):
        delay_after_stimulus = delay_after_stimulus - sampling_time
      elif (delay_stimulus is True) and (delay_after_stimulus <= 0):
        delay_after_stimulus = delay_time
        delay_stimulus = False

      if (board.analog[pin].read() > 0.75) and (delay_stimulus is False):
        if counter < stim_len:
          board.digital[pin_out].write(1)
          print('obstacle and signal!')        
        #elif counter > stim_len:
        #  board.digital[pin_out].write(0)
        #  print('    obstacle')
        else:
          delay_stimulus = True
        counter = counter + sampling_time

      else:
        board.digital[pin_out].write(0)
        counter = 0
        if (board.analog[pin].read() > 0.75) and (delay_stimulus == True):
          print('Obstacle but delaying stimulus')
        elif (board.analog[pin].read() > 0.75) and (delay_stimulus == False):
          print('Alarm!!!!!!!!! Obstacle without delay that is not used')
        else:
          print('')
    else:
      print("Pin with no value")

    board.pass_time(sampling_time)
 
board.exit()