#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
  echo "are you using 2 wheels or 4 wheels"
  echo "Usage: $0 use_2_wheels <map_name> # for two wheeled MoboBot"
  echo "Usage: $0 use_4_wheels <map_name> # for four wheeled MoboBot"
  exit 1
fi

WHEEL_NUM_STR=$1

if [ -z "$2" ]; then
  echo "map name required"
  echo "Usage: $0 $1 <map_name>"
  exit 1
fi

MAP_NAME=$2

# Reset USB Serial CH340 (EPMC_V2)
sudo usbreset 1a86:7523
echo "EPMC_V2 USB Reset Successful"

# Reset USB JTAG/serial debug unit (EIMU_V2)
sudo usbreset 303a:1001
echo "EIMU_V2 USB Reset Successful"

# Reset CP2102 USB to UART Bridge Controller (RPLIDAR)
sudo usbreset 10c4:ea60
echo "RPLIDAR USB Reset Successful"

echo "Launching Mobobot AMCL Navigation Bringup ROS2 Node"

# Source ROS2 workspace
source ~/mobo_bot_ws/install/setup.bash

# Launch ROS2 node with provided map name
if [[ $WHEEL_NUM_STR == "use_2_wheels" ]]; then
  ros2 launch mobo_bot_bringup robot_navigation.launch.py map_name:=$MAP_NAME
elif [[ $WHEEL_NUM_STR == "use_4_wheels" ]]; then
  ros2 launch mobo_bot_bringup robot_navigation.launch.py use_4_wheels:=true map_name:=$MAP_NAME
fi