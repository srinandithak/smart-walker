#How to run it
On the Jetson (two separate terminals, or use tmux):


python3 force_sensors/read_forces.py   # terminal 1
python3 vision.py                       # terminal 2
On the nearby computer:


python3 plot_force.py <jetson-ip>
e.g. python3 plot_force.py 192.168.1.42
