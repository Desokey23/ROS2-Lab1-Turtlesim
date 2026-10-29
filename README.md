# Design of Mechatronics Systems - Lab 1: ROS 2 & Turtlesim

## Team Members
1. [Mohamed Desokey] - [ID 9386]
2. [Adham Yousri] - [ID 9766]
3. [Hassan Mohamed] - [9274]

## Packages Description
This repository contains two ROS 2 packages developed for controlling the turtlesim simulator:
1. **`turtlesim_interfaces`**: A custom interface package containing the message (`TargetPoint.msg`), services (`SetSpeeds.srv`), and actions (`GoToPose.action`, `Square.action`) definitions.
2. **`turtlesim_assignment`**: The main Python package containing the action servers, service servers, and the launch file to execute the complete system.

## Build Steps
To build the project from scratch in a new workspace, run the following commands:
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
# Clone this repository here
git clone <your_github_repo_link> .
cd ~/ros2_ws
colcon build --packages-select turtlesim_interfaces
source install/setup.bash
colcon build --packages-select turtlesim_assignment
source install/setup.bash

## Commands to move
launch: ros2 launch turtlesim_assignment main.launch.py
Manual Control: ros2 run turtlesim turtle_teleop_key
Reset:  ros2 service call /reset_turtle_custom std_srvs/srv/Empty
go to point:  ros2 action send_goal /go_to_pose turtlesim_interfaces/action/GoToPose "{target: {x: (x position), y: (y position), yaw: (angle in radian)}}" -f
Draw Square:  ros2 action send_goal /draw_square turtlesim_interfaces/action/Square "{side_length: (length)}" -f
Change Speed:  ros2 service call /set_speeds turtlesim_interfaces/srv/SetSpeeds "{max_linear_speed: 1.0, max_angular_speed: 1.0}"
Read the position:  ros2 topic echo /turtle1/pose
Show Parameters in system:  ros2 param list
Read the Speed:  ros2 param get /go_to_pose_server max_linear_speed
Bag Record:  ros2 bag record /turtle1/cmd_vel /turtle1/pose
to run the record:  ros2 bag play (file name)

