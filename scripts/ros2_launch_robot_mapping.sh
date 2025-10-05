#!/bin/bash

# Reset USB Serial CH340 (EPMC_V2)
sudo usbreset 1a86:7523
echo "EPMC_V2 USB Reset Successful"

# Reset USB JTAG/serial debug unit (EIMU_V2)
sudo usbreset 303a:1001
echo "EIMU_V2 USB Reset Successful"

# Reset CP2102 USB to UART Bridge Controller (RPLIDAR)
sudo usbreset 10c4:ea60
echo "RPLIDAR USB Reset Successful"

echo "Launching Mobobot SLAM Mapping Bringup ROS2 Node"

# Source ROS2 workspace
source ~/mobo_bot_ws/install/setup.bash

# Launch ROS2 node with provided map name
ros2 launch mobo_bot_bringup robot_mapping.launch.py