from Tkinter import *
import serial
import threading
import time
import sys

port = ''
if len(sys.argv) <= 1:
  port = '/dev/tty.usbmodem1421'
else:
  port = sys.arv[1]

num_servos = 12

# Set up serial
ser = serial.Serial(port, 9600, timeout = 0)

joints = [None] * num_servos
commands = []
saves = [None] * num_servos
begin = [48, 33, 42, 48, 0, 50, 48, 33, 42, 48, 0, 50]
#servo_limits = [155, 550]
limits = [[155, 514], [155, 513], [155, 550], [250, 550], [155, 550], [352, 530], [155, 514], [155, 513], [155, 550], [250, 550], [155, 550], [352, 530]]
flip = [0,1,0,1,0,0,0,1,0,1,0,0]
slew_steps = 30  # per second
prog_lines = 10

original = [0] * len(joints)
delta = [0.0] * len(joints)
step = -1

running = False
cur_prog = 0
last_send = 0

send_count = 0

  

def send_all(event=None):
  global joints
  global last_send
  global send_count
  if time.time() - last_send < 0.07:  # Don't send instructions too fast!
    #print "Too soon!" + str(time.time())
    joints[0].after(1000, send_all)
    return 
  tosend = 's'
  for i in range(len(joints)):
    start = limits[i][0]
    range_m = limits[i][1] - start
    if flip[i] == 0:
      tosend +=str( int(start +  float(joints[i].get()) / 100.0  * range_m ))
    else:
      tosend +=str( int(start + float((joints[i].get()) / 100.0 * -1.0 + 1.0)  * range_m))
  print("Sending -> " + tosend)
  ser.write(tosend)
  send_count = send_count + 1
  last_send = time.time()
  #time.sleep(0.1)

def save_state(event=None):
  global joints
  global commands
  global saves
  #commands[event.widget.row][3] = commands[event.widget.row][3][:]
  for i in range(num_servos):
    print(saves[i])
  saves[event.widget.row] = [150] * num_servos
  for i in range(len(joints)):
    saves[event.widget.row][i] = joints[i].get()
  for i in range(num_servos):
    print(saves[i])
  commands[event.widget.row][1]["text"] = "-Goto-"

def run_this(event=None):
  global joints
  global commands
  global saves
  global dwell
  global original
  global delta
  global step

  if type(event) is NoneType:
    event = 0
  elif type(event) is not int:
    event = event.widget.row
  
  if step == -1:  # First time run
    print("row-run" + str(event))
    if saves[event] == None:
      print("nothing saved")
      return
    print("First")
    # Save current position
    for i in range(len(joints)):
      original[i] = float(joints[i].get())
    # we are going to : saves[event.widget.row][i]
      # assume slew_steps to get there
    for i in range(len(joints)):
      delta[i] = float(saves[event][i] - original[i] ) / (slew_steps * float(dwell.get()))
    step = step + 1
  if step > slew_steps * float(dwell.get()):
    print("done!")
    step = -1
    return
  else:
    print("step %d" % step)
    for i in range(len(joints)):
      joints[i].set( int(original[i] + step * delta[i]) )  # linear slew
    send_all()
    step = step + 1
    joints[i].after(int(  1000 / slew_steps) ,run_this)

def run_this_old(event=None):
  global joints
  global commands
  global saves
  print("row-run" + str(event.widget.row))
  if saves[event.widget.row] == None:
    print("nothing saved")
    return
  for i in range(len(joints)):
    print(saves[event.widget.row][i])
    joints[i].set( saves[event.widget.row][i] )
  send_all()

def clear_this(event=None):
  global commands
  commands[event.widget.row][3].delete(0,END)
  commands[event.widget.row][3].insert(0,'-')
  saves[event.widget.row] = None
  commands[event.widget.row][1]["text"] = "Goto"

def click_prog(event=None):
  global running
  running = True
  do_prog()

def do_prog(event=None):
  global running
  global cur_prog
  if not running:
    cur_prog = 0
    return
  # find next
  print("Find next")
  for i in range(cur_prog + 1, len(saves)):
    if saves[i] != None:
      print("running %d" % i)
      run_this(i)
      cur_prog = cur_prog + 1
      commands[0][0].after(int(  1500 * float(dwell.get())) ,do_prog)
      return
  # if you got here nothing ran!
  print("no find")
  if cur_prog == -1:
    return
  cur_prog = -1
  do_prog()

def stop_prog(event=None):
  global running
  running = False
  
def getSerial(event=None):
  global ser
  global joints
  joints[0].after(100, getSerial)
  line = ser.readline()
  while len(line) != 0:
    line = ser.readline()
    print "sent: ", send_count, " ",  line

master = Tk()

for i in range(len(joints)):
  joints[i] = Scale(master, from_=0, to=100)
  joints[i].set(begin[i])
  joints[i].secret = i
  joints[i].grid(column = i, rowspan=prog_lines, row = 0, ipady=150, ipadx=5)
  joints[i].bind('<Motion>', send_all)
  label = Label(master,text = "S%d" % (i + 1))
  label.grid(column = i, row = prog_lines +1)

for i in range(prog_lines):
  bob = []
  
  

  bob.append( Button(master, text="Save" ))
  bob[-1].bind('<Button>', save_state)
  bob[-1].row = i
  bob[-1].grid(column = num_servos + 3, row = i + 1)

  bob.append( Button(master, text="Goto") )
  bob[-1].bind('<Button>', run_this)
  bob[-1].row = i
  bob[-1].grid(column = num_servos + 4, row = i + 1)
  bob.append( Button(master, text="Clear") )

  bob[-1].bind('<Button>', clear_this)
  bob[-1].row = i
  bob[-1].grid(column = num_servos + 5, row = i + 1)
  
  bob.append( Entry(master) )
  bob[-1].insert(0,'-')
  bob[-1].row = i
  bob[-1].grid(column = num_servos + 2, row = i + 1)

  bob.append( Label(master, text = "Pos # %s" % (i + 1)) )
  bob[-1].grid(column = num_servos + 1, row = i + 1)

  commands.append(bob)

dwell = Entry(master)
dwell.insert(0,0.5)
dwell.grid(column = num_servos + 2, row = 0)
run = Button(master, text = "Run All", command = click_prog)
run.grid(column = num_servos + 3, row = 0)
run = Button(master, text = "STOP", command = stop_prog)
run.grid(column = num_servos + 4, row = 0)
text1 = Label(master, text="Dwell Time (s)")
text1.grid(column = num_servos + 1, row = 0)

time.sleep(2)
send_all()
getSerial()
mainloop()