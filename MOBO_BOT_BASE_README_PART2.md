## Working with the Physical MoboBot (PART 2) | Running and Testing MoboBot

![mobo_bot_base_drive](./docs/mobo_bot_drive_test.gif)

### Make the robot launch script files executables (Only Once)

> [!NOTE]
> if you did the USB RESET section in PART 1 then tyou have to do this part once.

```shell
cd ~/mobo_bot_ws/src/mobo_bot/scripts/ && sudo chmod +x ros2_launch_robot.sh ros2_launch_robot_mapping.sh ros2_launch_robot_mapping_with_navigation.sh ros2_launch_robot_navigation.sh
```

#

### Set MoboBot Wheel Type Environment Variable  
- If you are using the **two wheel** differntial drive base
  ```shell
  export MOBOBOT_WHEEL_TYPE=2wheel
  echo "export MOBOBOT_WHEEL_TYPE=2wheel" >> ~/.bashrc
  ```

- if you are using the **four wheel** differntial drive base
  ```shell
  export MOBOBOT_WHEEL_TYPE=4wheel
  echo "export MOBOBOT_WHEEL_TYPE=4wheel" >> ~/.bashrc
  ```

#

### View Robot and Transform Tree
this shows the transformation between the differnt robot parts. it uses the **robot_state_publisher** the transforms, **RVIZ** to view the actual robot, and the **rqt_tf_tree** to view the transform graph.

##### On The Raspberry Pi
- open a new terminal and start the mobobot robot base bringup
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 launch mobo_bot_bringup robot.launch.py
  ```
  > [!NOTE]
  > If any error occurs, you might need to unplug and plug back the hardwares.

  OR
- preferably run the mobobot robot bringup bash script
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/scripts/
  ./ros2_launch_robot.sh
  
  ```
  > [!NOTE]
  > this would software reset the Hardware USB before launching to avoid error form the hardwares

##### On The Dev PC
- on your dev-PC, open a new terminal and launch the **tf_view** to view the transform
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 launch mobo_bot_bringup tf_view.launch.py use_hardware:=true
  ```

#

### Launch the Physical MoboBot

##### On The Raspberry Pi
- open a new terminal and start the mobobot robot base bringup
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 launch mobo_bot_bringup robot.launch.py # use_ekf:=true
  ```
  OR
- preferably run the mobobot robot bringup bash script
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/scripts/
  ./ros2_launch_robot.sh
  ```

##### On The Dev PC
- open a new terminal and start the mobo_bot_rviz by running
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 launch mobo_bot_rviz robot.launch.py
  ```
  >NOTE: You should now see the robot visuals on your dev-PC

- In a different terminal, run the arrow_key_teleop to drive the robot around using the arrow keys on your keyboard
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 run arrow_key_teleop_drive arrow_key_teleop_drive 0.15 0.75 1
  ```
  >NOTE: feel free to use any other **teleop package** you want 

#

### Run the MoboBot Mapping (Drive robot with teleop) - SLAM

##### On The Raspberry Pi
- open a new terminal and start the mobobot robot mapping bringup
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 launch mobo_bot_bringup robot_mapping.launch.py # use_ekf:=true
  ```
  OR
- preferably run the mobobot robot mapping bringup bash script
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/scripts/
  ./ros2_launch_robot_mapping.sh
  ```

##### On The Dev PC
- open a new terminal and start the mobo_bot_rviz mapping Viz by running
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 launch mobo_bot_rviz robot_mapping.launch.py
  ```
- In a different terminal, run the arrow_key_teleop to drive the robot around using the arrow keys on your keyboard
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 run arrow_key_teleop_drive arrow_key_teleop_drive 0.15 0.75 1
  ```

##### On The Raspberry Pi
- save the map once you are done mapping. (map file would be saved in the `maps` folder inside the `mobo_bot_navigation` pakage folder)
  >NOTE: Whenever you build a new map you can save it using the command below: 
  >```shell
  >   ros2 run nav2_map_server map_saver_cli -f ~/mobo_bot_ws/src/mobo_bot/mobo_bot_navigation/maps/<map_name>  # Saves the current map to the mobo_bot map folder
  >```

#

### Run the MoboBot Mapping (Navigate with Nav2 while Mapping) - SLAM

##### On The Raspberry Pi
- open a new terminal and start the mobobot robot mapping with navigation bringup
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 launch mobo_bot_bringup robot_mapping_with_navigation.launch.py # use_ekf:=true
  ```
  OR
- preferably run the mobobot robot mapping with navigation bringup bash script
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/scripts/
  ./ros2_launch_robot_mapping_with_navigation.sh
  ```

##### On The Dev PC
- open a new terminal and start the mobo_bot_rviz mapping_with_navigation Viz by running
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 launch mobo_bot_rviz robot_mapping_with_navigation.launch.py
  ```

- Now use the Nav2Goal button from RVIZ to move the robot from point to point on the known area of the currently created map and see how the robot both navigates and simultaneously create the map.

##### On The Raspberry Pi
- save the map once you are done mapping. (map file would be saved in the `maps` folder inside the `mobo_bot_navigation` pakage folder)
  >NOTE: Whenever you build a new map you can save it using the command below: 
  >```shell
  >   ros2 run nav2_map_server map_saver_cli -f ~/mobo_bot_ws/src/mobo_bot/mobo_bot_navigation/maps/<map_name>  # Saves the current map to the mobo_bot map folder
  >```

#

### Run the MoboBot Navigation (With an already created Map) - AMCL
The robot is able to autonomously navigate using the map of the environment created in the previous step. The Adaptive Monte Carlo Localization (AMCL) algorithm from Nav2 is use to localize the robot (i.e know the where the robot is located) in the already created Map being used. With this information of the robot location, the robot is able to autonomously navigate to different goal pose on the map.
>NOTE: the AMCL is configured to use the initial position of the robot (x = 0.0, y = 0.0, yaw = 0.0)
>you can change the robot initial starting pose as needed

##### On The Raspberry Pi
- open a new terminal and start the mobobot robot navigation bringup
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 launch mobo_bot_bringup robot_navigation.launch.py map_name:=<enter the name of the map> # use_ekf:=true
  ```
  OR
- preferably run the mobobot robot navigation bringup bash script
  ```shell
  cd ~/mobo_bot_ws/src/mobo_bot/scripts/
  ./ros2_launch_robot_navigation.sh <enter the name of the map>
  ```

##### On The Dev PC
- open a new terminal and start the mobo_bot_rviz navigation Viz by running
  ```shell
  source ~/mobo_bot_ws/install/setup.bash
  ros2 launch mobo_bot_rviz robot_navigation.launch.py
  ```

- Now use the Nav2Goal button to move the robot to any Goal pose on the map.

#