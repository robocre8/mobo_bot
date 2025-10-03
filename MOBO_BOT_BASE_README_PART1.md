## Working with the Physical MoboBot (PART 1) | Seting up the on-board Raspberry Pi

### Prerequisite Dependencies
- ensure your Dev-PC and the Raspberry Pi (both running ubuntu 24.04) can now communicate Via ssh
- you should have setup ros jazzy (prefarrably base and not desktop) on the raspberry pi
- install the `libserial-dev` package on the Raspberry Pi 4b machine
  ```shell
  sudo apt-get update
  sudo apt install libserial-dev
  ```
- install cyclone DDS (if you have not) on the Raspberry Pi 4b machine
  ```shell
  sudo apt install ros-jazzy-rmw-cyclonedds-cpp
  export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
  echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> ~/.bashrc
  ```
  
#

### Create ROS Workspace And Download the MoboBot packages

- create your mobo_bot_ws in the home dir.
  ```shell
  mkdir -p ~/mobo_bot_ws/src
  cd ~/mobo_bot_ws
  colcon build
  source ~/mobo_bot_ws/install/setup.bash
  ```

- cd into the src folder of your mobo_bot_ws and download the mobo_bot packages
  ```shell
  cd ~/mobo_bot_ws/src
  git clone -b jazzy https://github.com/robocre8/mobo_bot.git
  ```

- cd into the mobo_bot/mobo_bot_sim folder and add a `COLCON_IGNORE` file to the mobo_bot_sim package to prevent runnig simulation on the Raspberry Pi. 
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/mobo_bot_sim
  touch COLCON_IGNORE
  ```

- cd into the mobo_bot/mobo_bot_rviz folder and add a `COLCON_IGNORE` file to the mobo_bot_rviz package to prevent running rviz visualization on the Raspberry Pi.
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/mobo_bot_rviz
  touch COLCON_IGNORE
  ```
  
#

### Download the ROS2 packages and Drivers for the Sensor and Actuators Used by MoboBot

- create a folder called **hardware**
  ```shell
  cd ~/mobo_bot_ws/src
  mkdir hardware
  ```

#### EPMC V2 Motor Driver
- go to the `src/hardware` folder of your mobo_bot_ws and download and setup the `epmc_v2_hardware_interface` ros2 plugin package
  ```shell
  cd ~/mobo_bot_ws/src/hardware
  git clone https://github.com/robocre8/epmc_v2_hardware_interface.git
  ```

#### EIMU V2 Module
- go to the `src/hardware` folder of your mobo_bot_ws and download and setup the `eimu_v2_ros` ros2 package
  ```shell
  cd ~/mobo_bot_ws/src/hardware
  git clone https://github.com/robocre8/eimu_v2_ros.git
  ```

#### RPLIDAR C1
- go to the `src/hardware` folder of your mobo_bot_ws and download sllidar ros2 for RPLIDAR C1
  ```shell
  cd ~/mobo_bot_ws/src/hardware
  git clone https://github.com/Slamtec/sllidar_ros2.git
  ```

#### CAMERA (with OpenCV)
- install opencv on the Raspberry Pi 4b machine
  ```shell
  sudo apt install libopencv-dev python3-opencv
  pip3 install opencv-python
  ```

- go to the `src/hardware` folder of your mobo_bot_ws and download the opencv_ros_camera package, from *robocre8*, for working with the USB camera
  ```shell
  cd ~/mobo_bot_ws/src/hardware
  git clone https://github.com/robocre8/opencv_ros_camera.git
  ```

#

### Install Necessary ROS2 dependencies and Build Mobobot Workspace

- cd into the root directory of your mobo_bot_ws and run rosdep to install all necessary ros package dependencies
  ```shell
  cd ~/mobo_bot_ws/
  rosdep install --from-paths src --ignore-src -r -y
  ```

- build your mobo_bot_ws
  ```shell
  cd ~/mobo_bot_ws/
  colcon build --parallel-workers 2 --symlink-install
  ```

- don't forget to source your mobo_bot_ws in any new terminal
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ```

> [!NOTE]
> You can further edit the parameters of the .yaml files in the mobo_bot_base package config folder

#

### Start/Run the udev rule scripts for the hardware communication

- copy mobobot's hardware udev rule file into the udev rule folder with the following command:
  ```shell
  sudo cp ~/mobo_bot_ws/src/mobo_bot/scripts/75-mobobot-hardware.rules /etc/udev/rules.d/
  ```

- get udev to recognize the newly addeed `75-mobobot-hardware.rules` rule
  > [!NOTE]
  > You only need to run this commands once. You do not need to run it again after a new restart.
  ```shell
  sudo udevadm control --reload-rules && sudo service udev restart && sudo udevadm trigger
  ```

- you can do a quick test to see if hardwares (epmc_v2 motor controller, eimu_v2 imu module, and rplidar c1) are recognized. run each line below:
  ```shell
  ls /dev/eimu
  ls /dev/epmc
  ls /dev/rplidar_c1
  ```

#

### Optional (but Recommended) USB RESET SETUP

> [!NOTE]
> usb-reset allows you to reset USB via sofware (more like cleanup USB port incase the nodes do not exit well for the hardwares).

- install usb-reset package ubuntu:
  ```shell
  sudo apt update
  sudo apt install snapd
  sudo snap install core
  sudo snap install usb-reset
  ```

- make the `usb-reset-test-script.sh` executable to see if it is working:
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/scripts/
  sudo chmod +x usb-reset-test-script.sh
  ```

- run the `usb-reset-test-script.sh` to see if it is working:
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/scripts/
  ./usb-reset-test-script.sh
  ```

> [!NOTE]
> if all goes well the usb-reset is now working well for the hardwares.
> this would later be used while running the robot via scripts files

#

### Clone and Build The MoboBot packages on your dev-PC connected (via ssh) to the Raspberry PI on the MoboBot robot

- pls follow the [mobo_bot_sim tutorial](https://github.com/robocre8/mobo_bot/blob/jazzy/MOBO_BOT_SIM_README.md) for dev-PC
- you'll be using the **mobo_bot_rviz** package on your dev-PC to visualize the robot.

#

[**Working with the Physical MoboBot (PART 2) | Running and Testing MoboBot**](https://github.com/robocre8/mobo_bot/blob/jazzy/MOBO_BOT_BASE_README_PART2.md)