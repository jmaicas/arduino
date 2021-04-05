import pyfirmata
import numpy as np

pin = 1 # analog pin to receive the obstacle info
pin_out = 12 # digital pin to send the trigger info
time_min = 60
total_time = time_min*60 # in seconds

# Parameters to follow the protocol in Carlezon & Chartoff (2007)
stim_len = 0.5
sampling_freq = 141 # Hz
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
for i in np.arange(0, total_time, sampling_time):
    #print("\n Checking state at second %f" % i)
    #print("Pin %i : %s" % (pin, board.analog[pin].read()))
    if board.analog[pin].read() is None:
      print("Pin with no value")
    else:
      if board.analog[pin].read() > 0.75:
        if counter < stim_len:        
          board.digital[pin_out].write(1)
          print('obstacle and signal!')
        else: 
          board.digital[pin_out].write(0)
          print('    obstacle')
        counter = counter + sampling_time
      else:
        board.digital[pin_out].write(0)
        counter = 0
        print('')
    board.pass_time(sampling_time)
 
board.exit()