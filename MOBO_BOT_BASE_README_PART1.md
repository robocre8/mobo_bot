## Working with the Physical MoboBot (PART 1) | Seting up the on-board Raspberry Pi

### Clone and Build The MoboBot packages on your dev-PC connected to the Raspberry PI on the MoboBot robot

- pls follow the [mobo_bot_sim tutorial](https://github.com/robocre8/mobo_bot/blob/jazzy/MOBO_BOT_SIM_README.md) for dev-PC
- you'll be using the **mobo_bot_rviz** package on your dev-PC to visualize the robot.
- you'll be using the **arrow_key_teleop** package on your dev-PC to drive the robot.

#

### Prerequisite Dependencies
- ensure your Dev-PC and the Raspberry Pi (both running ubuntu 24.04) can now communicate Via ssh
- you should have setup ros jazzy (prefarrably base and not desktop) on the raspberry pi
- install cyclone DDS (if you have not) on the Raspberry Pi 4b machine
  ```shell
  sudo apt update && sudo apt upgrade -y
  ```
  ```shell
  sudo apt install ros-jazzy-rmw-cyclonedds-cpp
  ```
  ```shell
  export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
  ```
  ```shell
  echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> ~/.bashrc
  ```
  
#

### Create ROS Workspace And Download the MoboBot packages

- create your mobo_bot_ws in the home dir.
  ```shell
  mkdir -p ~/mobo_bot_ws/src && cd ~/mobo_bot_ws && colcon build && source ~/mobo_bot_ws/install/setup.bash
  ```

- cd into the src folder of your mobo_bot_ws and download the mobo_bot packages
  ```shell
  cd ~/mobo_bot_ws/src && git clone -b jazzy https://github.com/robocre8/mobo_bot.git
  ```

- cd into the mobo_bot/mobo_bot_sim folder and add a `COLCON_IGNORE` file to the mobo_bot_sim package to prevent runnig simulation on the Raspberry Pi. 
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/mobo_bot_sim && touch COLCON_IGNORE
  ```

- cd into the mobo_bot/mobo_bot_rviz folder and add a `COLCON_IGNORE` file to the mobo_bot_rviz package to prevent running rviz visualization on the Raspberry Pi.
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/mobo_bot_rviz && touch COLCON_IGNORE
  ```
  
#

### Download the ROS2 packages and Drivers for the Sensor and Actuators Used by MoboBot

- create a folder called **hardware**
  ```shell
  cd ~/mobo_bot_ws/src && mkdir hardware
  ```

#### EPMC Motor Driver
- go to the `src/hardware` folder of your mobo_bot_ws and download and setup the `epmc_hardware_interface` ros2 plugin its serial comm library .deb package
  ```shell
  wget https://github.com/robocre8/epmc_serial_cpp/releases/download/v1.0.0/epmc-serial-dev_1.0.0_24.04_arm64.deb
  ```
  ```shell
  sudo apt install ./epmc-serial-dev_1.0.0_24.04_arm64.deb
  ```
  ```shell
  cd ~/mobo_bot_ws/src/hardware && git clone https://github.com/robocre8/epmc_hardware_interface.git
  ```

#### EIMU Module
- go to the `src/hardware` folder of your mobo_bot_ws and download and setup the `eimu_ros` ros2 package with its serial comm library .deb package
  ```shell
  wget https://github.com/robocre8/eimu_serial_cpp/releases/download/v1.0.0/eimu-serial-dev_1.0.0_24.04_arm64.deb
  ```
  ```shell
  sudo apt install ./eimu-serial-dev_1.0.0_24.04_arm64.deb
  ```
  ```shell
  cd ~/mobo_bot_ws/src/hardware && git clone https://github.com/robocre8/eimu_ros.git
  ```

#### RPLIDAR C1
- go to the `src/hardware` folder of your mobo_bot_ws and download sllidar ros2 for RPLIDAR C1
  ```shell
  cd ~/mobo_bot_ws/src/hardware && git clone https://github.com/Slamtec/sllidar_ros2.git
  ```

#### CAMERA (with OpenCV)
- install opencv on the Raspberry Pi 4b machine and download the opencv_ros_camera package for working with the USB camera
  ```shell
  sudo apt install libopencv-dev python3-opencv
  ```
  ```shell
  cd ~/mobo_bot_ws/src/hardware && git clone https://github.com/robocre8/opencv_ros_camera.git
  ```

#

### Install Necessary ROS2 dependencies and Build Mobobot Workspace

- cd into the root directory of your mobo_bot_ws and run rosdep to install all necessary ros package dependencies
  ```shell
  cd ~/mobo_bot_ws/ && rosdep install --from-paths src --ignore-src -r -y
  ```

- build your mobo_bot_ws
  ```shell
  cd ~/mobo_bot_ws/ && colcon build --parallel-workers 2 --symlink-install
  ```

- don't forget to source your mobo_bot_ws in any new terminal
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ```

> [!NOTE]
> You can further edit the parameters of the .yaml files in the mobo_bot_base package config folder

#

### Start/Run the udev rule scripts for the hardware communication
- edit the udev file in the `udev_sample_script` folder:
  > [!NOTE]
  > what you are mostly concerned about is the `ATTRS{serial}=="34:B7:DA:F7:B2:6C"`.
  > all you need to do is to check and change the epmc and eimu serial attribute
  > run this command:
  ```shell
  udevadm info --attribute-walk /dev/ttyACM0 | grep ATTRS{serial}
  ```

- copy the edited hardware udev rule file into the udev rule folder with the following command (depending on the wheel base you are using):
  ```shell
  sudo cp ~/mobo_bot_ws/src/mobo_bot/udev_sample_script/75-mobobot-hardware.rules /etc/udev/rules.d/
  ```
  or
  ```shell
  sudo cp ~/mobo_bot_ws/src/mobo_bot/udev_sample_script/75-mobobot-hardware-4wheel.rules /etc/udev/rules.d/
  ```

- get udev to recognize the newly addeed `75-mobobot-hardware.rules` or the `75-mobobot-hardware-4wheel.rules` rule
  > [!NOTE]
  > You only need to run this commands once. You do not need to run it again after a new restart.
  ```shell
  sudo udevadm control --reload-rules && sudo service udev restart && sudo udevadm trigger
  ```

- you can do a quick test to see if hardwares (epmc motor controller, eimu imu module, and rplidar c1) are recognized. run each line below:
</br> (for 2 wheel)
  ```shell
  ls /dev/eimu
  ls /dev/epmc
  ls /dev/rplidar_c1
  ```
  or (for 4 wheel)
  ```shell
  ls /dev/eimu
  ls /dev/epmc_front
  ls /dev/epmc_rear
  ls /dev/rplidar_c1
  ```

#

[**Working with the Physical MoboBot (PART 2) | Running and Testing MoboBot**](https://github.com/robocre8/mobo_bot/blob/jazzy/MOBO_BOT_BASE_README_PART2.md)
