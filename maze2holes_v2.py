import pyfirmata
import numpy as np
import pandas as pd
import xlsxwriter
import datetime

###############################################
### Parameters to change between recordings ###
###############################################
recordings_number = 1 
# folder to store the recordings. It needs a double \ to separate folders
folder = 'C:\\MFB stim\\1935\\LinearTrack\\'

# time in minutes to run the experiment
time_min = 10 # in minutes
# delay before allowing another stimulation
thres_betw_interv = 1 # in seconds

# Arduino pins to write to or read from
pin = 1 # analog pin to receive the obstacle info
pin2 = 2 # analog pin to receive the second obstacle info
pin_out = 8 # digital pin to send the trigger info
pin_outled = 10 # to light the led #1
#pin2_out = 8 # digital pin to send the trigger info
#pin2_outled = 6 # to light the led #2

total_time = time_min*60 # in seconds

# Parameters to follow the protocol in Carlezon & Chartoff (2007)
stim_len = 0.44  # it should be 0.5s but the TTL hardware that receives the arduino signal 
                 # produces a 0.5s pulse when receives an slightly shorter pulse
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
board.analog[pin2].enable_reporting()



# Allows stimulation in an extreme only when an stimulation has been triggered in the other end
for rec in np.arange(recordings_number):
    
  # Run until the total time is reached
  counter = 0
  counter2 = 0
  
  keep_stimulus = False
  visited_hole_1 = True
  visited_hole_2 = True
  keep_stimulus2 = False
  stim_times1 = np.zeros(int(total_time/sampling_time))
  stim_times2 = np.zeros(int(total_time/sampling_time))
  poke_times1 = np.zeros(int(total_time/sampling_time))
  poke_times2 = np.zeros(int(total_time/sampling_time))
  time = np.arange(0, total_time, sampling_time)

  c = 0
  
  for i in np.arange(0, total_time, sampling_time):
      
      #print("\n Checking state at second %f" % i)
      #print("Pin %i : %s" % (pin, board.analog[pin].read()))
      if board.analog[pin].read() is not None and board.analog[pin2] is not None:
        
        if (board.analog[pin].read() > 0.75) or (board.analog[pin2].read() > 0.75):
          #print('poking in hole 1')

          if counter < stim_len:
            board.digital[pin_out].write(1)
            board.digital[pin_outled].write(1)
            print('stim 1')
            keep_stimulus = True

          elif counter >= stim_len:
            board.digital[pin_out].write(0)
            board.digital[pin_outled].write(0)
            counter = 0
            keep_stimulus = False
            
          counter = counter + sampling_time

        else:
          if counter < stim_len and keep_stimulus:
            board.digital[pin_out].write(1)
            board.digital[pin_outled].write(1)
            print('stim 1')
            counter = counter + sampling_time                        
          elif counter >= stim_len and keep_stimulus:
            counter = 0
            board.digital[pin_out].write(0)
            board.digital[pin_outled].write(0)
            keep_stimulus = False
          else:
            counter = 0
            board.digital[pin_out].write(0)
            board.digital[pin_outled].write(0)
            keep_stimulus = False
        
        stim_times1[c] = int(keep_stimulus)

      else:
        print("Pin with no value")

      board.pass_time(sampling_time)

      c = c + 1

  # Setting the outputs to 0 so the animal does not receive anything once the experiment is finished
  board.digital[pin_out].write(0)
  board.digital[pin_outled].write(0)
  
  total_number_stims1 = sum(stim_times1)/9
  print('Total number of rewards hole 1:', total_number_stims1)
  total_number_stims2 = sum(stim_times2)/9
  print('Total number of rewards hole 2:', total_number_stims2)

  df_stim = pd.DataFrame({'Time': time, 'Poke in 1': poke_times1, 'Stim from 1': stim_times1, 'Poke in 2': poke_times2, 'Stim from 2': stim_times2, 'Total_stim1': total_number_stims1, 'Total_stim2': total_number_stims2})
  
  filename = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
  df_stim.to_excel(folder + 'record_' + str(rec+1) + '_' + filename + '.xlsx')
  print('Recording number ' + str(rec + 1) + ' finished')
  print('')
  
board.exit()