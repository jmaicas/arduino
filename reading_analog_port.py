import pyfirmata
import numpy as np

pin = 1
sampling_time = 0.1 # in seconds

# Creates a new board 
board = pyfirmata.Arduino('/dev/ttyACM0')
print("Setting up the connection to the board ...")
it = pyfirmata.util.Iterator(board)
it.start()
 
# Start reporting for define pin
board.analog[pin].enable_reporting()

 
# Loop for reading the input. Duration approx. 10 s
for i in np.arange(1, 1000, sampling_time):
    #print("\n Checking state at second %f" % i)
    #print("Pin %i : %s" % (pin, board.analog[pin].read()))
    if board.analog[1].read() is None:
      print("Pin with no value")
    else:
      if board.analog[1].read() > 0.75:        
        board.digital[12].write(1)
        print('obstacle!')
      else:
        board.digital[12].write(0)
        print('')
    board.pass_time(sampling_time)
 
board.exit()