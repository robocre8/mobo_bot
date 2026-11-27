## Working with the Physical MoboBot (PART 2) | Running and Testing MoboBot

![mobo_bot_hardware_drive](./docs/mobo_bot_in_action_2.gif)

### Set MoboBot Base Type Environment Variable  
- Depending on the base chassis type you are using run any of the command below:

```shell
export MOBOBOT_BASE_TYPE=2WD
```

- add to your `.bashrc` file for auto sourcing 

```shell
echo "export MOBOBOT_BASE_TYPE=2WD" >> ~/.bashrc
```

#

### View Robot and Transform Tree
this shows the transformation between the differnt robot parts. it uses the **robot_state_publisher** the transforms, **RVIZ** to view the actual robot, and the **rqt_tf_tree** to view the transform graph.

##### On The Raspberry Pi
- open a new terminal and start the mobobot robot base bringup
```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch mobo_bot_description rsp.launch.py \
use_joint_state_pub:=true
```

##### On The Dev PC
- on your dev-PC, open a new terminal and launch the **tf_view** to view the transform
```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch mobo_bot_bringup tf_view.launch.py \
use_hardware:=true
```

#

### Launch the Physical MoboBot

##### On The Raspberry Pi
- start the mobobot robot base package for partial launch (no lidar or camera)
```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch mobo_bot_bringup robot.launch.py \
use_lidar:=False \
use_camera:=False

```
  OR
- start the mobobot robot bringup for full robot launch with lidar
```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch mobo_bot_bringup robot.launch.py \
use_lidar:=True \
# use_camera:=True
```

##### On The Dev PC
- open a new terminal and start the mobo_bot_rviz by running
```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch mobo_bot_rviz robot.launch.py
```
  >NOTE: You should now see the robot visuals on your dev-PC

- In a different terminal, run the arrow_key_telop to drive the robot around using the arrow keys on your keyboard

```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch arrow_key_teleop_drive arrow_key_teleop_drive.launch.py \
speed:=0.2 \
turn:=0.8 \
topic:=cmd_vel_teleop \
stamped:=True \
frame_id:=odom
```

  >NOTE: you would need to click into the rviz or simulation for the 
  > arrow_key_teleop drive to start woking. because it uses pynput
  >
  >NOTE: also feel free to use any other **teleop package** you want 

#

### Run the MoboBot Mapping (Drive robot with teleop) - slam-toolbox

##### On The Raspberry Pi
- open a new terminal and start the mobobot robot mapping bringup
```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch mobo_bot_bringup robot_mapping.launch.py \ 
use_lidar:=True \
# use_camera:=True
```

##### On The Dev PC
- open a new terminal and start the mobo_bot_rviz mapping_and_naviagion Vizualization by running
```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch mobo_bot_rviz mapping_and_navigation.launch.py
```
- In a different terminal, run the arrow_key_teleop to drive the robot around using the arrow keys on your keyboard
```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch arrow_key_teleop_drive arrow_key_teleop_drive.launch.py \
speed:=0.2 \
turn:=0.8 \
topic:=cmd_vel_teleop \
stamped:=True \
frame_id:=odom
```

##### On The Raspberry Pi (Save EasyNav SimpleMap or CostMap)

run the command below to save the `occupancy grid` map to be used later with AMCL for localization
</br>(map file would be saved in the `maps/hardware` folder inside the `mobo_bot_navigation` package folder)

- save simple map with easynav
```shell
ros2 service call /maps_manager_node/simple/savemap std_srvs/srv/Trigger
```
```shell
mv /tmp/default.map /home/$USER/mobo_bot_ws/src/mobo_bot/mobo_bot_navigation/maps/hardware/<map_name>.map
```

- save costmap map in easynav with slamtoolbox
```shell
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: '/home/$USER/mobo_bot_ws/src/mobo_bot/mobo_bot_navigation/maps/hardware/<map_name>'}}"
```

#


### Run the MoboBot Navigation (With an already created Map) - AMCL
The robot is able to autonomously navigate using the map of the environment created in the previous step. The Adaptive Monte Carlo Localization (AMCL) algorithm from EasyNav is use to localize the robot (i.e know the where the robot is located) in the already created Map being used. With this information of the robot location, the robot is able to autonomously navigate to different goal pose on the map.
>NOTE: the AMCL and SLAM are configured to use the initial position of the robot (x = 0.0, y = 0.0, yaw = 0.0)
>you can change the robot initial starting pose as needed

##### On The Raspberry Pi
- start the mobobot robot navigation bringup (with AMCL Localization)
```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch mobo_bot_bringup robot_navigation.launch.py \
map_name:=<name_of_saved_map> \
use_costmap:=False \
use_lidar:=True \
# use_camera:=True
```

##### On The Dev PC
- open a new terminal and start the mobo_bot_rviz mapping_and_naviagion Vizualization by running
```shell
source ~/mobo_bot_ws/install/setup.bash && ros2 launch mobo_bot_rviz mapping_and_navigation.launch.py
```

- Now use the Nav2Goal button from RVIZ to move the robot from point to point on the known area of the currently created map and see how the robot both navigates and simultaneously create the map.

#
