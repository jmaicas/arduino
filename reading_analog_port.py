import pyfirmata
import numpy as np
import pandas as pd
import xlsxwriter
import datetime
#from seaborn.palettes import cubehelix_palette

pin = 1 # analog pin to receive the obstacle info
pin2 = 2 # analog pin to receive the second obstacle info
pin_out = 12 # digital pin to send the trigger info
pin_outduplicated = 10
pin2_out = 8 # digital pin to send the trigger info
pin2_outduplicated = 6 # digital pin to send the trigger info

time_min = 5 # time in minutes to run the experiment
total_time = time_min*60 # in seconds
delay_time = 0  # delay after stimulus 0 is not delay
thres_betw_interv = 1 # delay before allowing another stimulation

# Parameters to follow the protocol in Carlezon & Chartoff (2007)
stim_len = 0.44
sampling_freq = 20 #141 # Hz
sampling_time = 1/sampling_freq # in seconds
half_sampling = sampling_time/2

# Creating an input for tests
# random 
#n = 100000
#m = 100000
#a = np.hstack((np.ones(n), np.zeros(m)))
#np.random.shuffle(a)

# Creates a new board 
board = pyfirmata.Arduino('COM7') # Windows
#board = pyfirmata.Arduino('/dev/ttyACM0') # Linux
print("Setting up the connection to the board ...")
it = pyfirmata.util.Iterator(board)
it.start()
 
# Start reporting for define pin
board.analog[pin].enable_reporting()
board.analog[pin2].enable_reporting()

recordings_number = 10

for rec in np.arange(recordings_number):
    
  # Run until the total time is reached
  counter = 0
  counter2 = 0
  count_betw_interv = 5
  count_betw_interv2 = 5

  delay_after_stimulus = delay_time
  delay_stimulus = False
  keep_stimulus = False
  took_nose_out = True
  delay_stimulus2 = False
  keep_stimulus2 = False
  took_nose_out2 = True
  stim_times = np.zeros(int(total_time/sampling_time))
  stim_times2 = np.zeros(int(total_time/sampling_time))
  poke_times = np.zeros(int(total_time/sampling_time))
  poke_times2 = np.zeros(int(total_time/sampling_time))
  time = np.arange(0, total_time, sampling_time)

  c = 0

  # todo the rat should not get another stimulation before 0.5 s

  for i in np.arange(0, total_time, sampling_time):
      
      #print("\n Checking state at second %f" % i)
      #print("Pin %i : %s" % (pin, board.analog[pin].read()))
      if board.analog[pin].read() is not None:
        
        if (board.analog[pin].read() > 0.75):

          poke_times[c] = 1
          
          if counter < stim_len and took_nose_out and count_betw_interv > thres_betw_interv:
            board.digital[pin_out].write(1)
            board.digital[pin_outduplicated].write(1)
            keep_stimulus = True    
            count_betw_interv = 0
          elif counter > stim_len:
            took_nose_out = False
            board.digital[pin_out].write(0)
            board.digital[pin_outduplicated].write(0)
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
            board.digital[pin_outduplicated].write(1)
            counter = counter + sampling_time
          else:
            took_nose_out = True
            counter = 0
            board.digital[pin_out].write(0)
            board.digital[pin_outduplicated].write(0)
            keep_stimulus = False
        
        stim_times[c] = int(keep_stimulus)

      else:
        print("Pin with no value")

      # Analysis for the detector that does not give reinforcement
      if board.analog[pin2].read() is not None:
        
        if (board.analog[pin2].read() > 0.75):
          poke_times2[c] = 1
          
          if counter2 < stim_len and took_nose_out2 and count_betw_interv2 > thres_betw_interv:
            board.digital[pin2_out].write(1)
            board.digital[pin2_outduplicated].write(1)
            keep_stimulus2 = True    
            count_betw_interv2 = 0
          elif counter2 > stim_len:
            took_nose_out2 = False
            board.digital[pin2_out].write(0)
            board.digital[pin2_outduplicated].write(0)
            count_betw_interv2 = count_betw_interv2 + sampling_time
            counter2 = 0
            keep_stimulus2 = False
          elif count_betw_interv2 <= thres_betw_interv:
            took_nose_out2 = False
            count_betw_interv2 = count_betw_interv2 + sampling_time

            
          counter2 = counter2 + sampling_time

        else:
          count_betw_interv2 = count_betw_interv2 + sampling_time
          if counter2 < stim_len and keep_stimulus2:
            board.digital[pin2_out].write(1)
            board.digital[pin2_outduplicated].write(0)
            counter2 = counter2 + sampling_time
          else:
            took_nose_out2 = True
            counter2 = 0
            board.digital[pin2_out].write(0)
            board.digital[pin2_outduplicated].write(0)
            keep_stimulus2 = False
      else:
        print("Pin 2 with no value")
      
      stim_times2[c] = int(keep_stimulus2)

      board.pass_time(sampling_time)

      c = c + 1

  # Setting the outputs to 0 so the animal does not receive anything once the experiment is finished
  board.digital[pin_out].write(0)
  board.digital[pin_outduplicated].write(0)
  board.digital[pin2_out].write(0)
  board.digital[pin2_outduplicated].write(0)

  df_stim = pd.DataFrame({'Time': time, 'Poke in 1': poke_times, 'Stim from 1': stim_times, 'Poke in 2': poke_times2, 'Stim from 2': stim_times2})
  filename = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")

  df_stim.to_excel(filename + '.xlsx')
  print('Recording finished')
  
board.exit()