#!/bin/bash

# Check if an argument is provided
# Check if an argument is provided
if [ -z "$1" ]; then
  echo "are you using 2 wheels or 4 wheels"
  echo "Usage: $0 use_2_wheels # for two wheeled MoboBot"
  echo "Usage: $0 use_4_wheels # for four wheeled MoboBot"
  exit 1
fi

WHEEL_NUM_STR=$1

if [ -z "$2" ]; then
  echo "map name required"
  echo "Usage: $0 $1 <map_name>"
  exit 1
fi

MAP_NAME=$2

echo "Launching Mobobot AMCL Navigation Bringup ROS2 Node"

# Source ROS2 workspace
source ~/mobo_bot_ws/install/setup.bash

# Launch ROS2 node with provided map name
if [[ $WHEEL_NUM_STR == "use_2_wheels" ]]; then
  ros2 launch mobo_bot_bringup sim_navigation.launch.py map_name:=$MAP_NAME
elif [[ $WHEEL_NUM_STR == "use_4_wheels" ]]; then
  ros2 launch mobo_bot_bringup sim_navigation.launch.py use_4_wheels:=true map_name:=$MAP_NAME
fi