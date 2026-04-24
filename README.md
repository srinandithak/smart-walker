# How to run it on jetson
On the Jetson (two separate terminals, or use tmux):



python3 vision.py                       # terminal 1
On the nearby computer:

python3 force_sensors/plot_force.py <JETSON_IP>
e.g. python3 plot_force.py 192.168.1.42

Make sure port 5005 is open on the Jetson's firewall (sudo ufw allow 5005 if using ufw). You can find the Jetson's IP with hostname -I on the Jetson.

