import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
  DeclareLaunchArgument,
  IncludeLaunchDescription)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression


def generate_launch_description():
  # Set the path to this package.
  hardware_pkg_path = get_package_share_directory('mobo_bot_hardware')
  navigation_pkg_path = get_package_share_directory('mobo_bot_navigation')
 
  #--------------------------------------------------------------------------

  # Launch configuration variables specific to simulation
  use_sim_time = LaunchConfiguration('use_sim_time')
  use_costmap = LaunchConfiguration('use_costmap')
  use_lidar = LaunchConfiguration('use_lidar')
  use_camera = LaunchConfiguration('use_camera')

  declare_use_sim_time_cmd = DeclareLaunchArgument(
    name='use_sim_time',
    default_value='False',
    description='whether to use simulation clock or not'
  )

  declare_use_lidar_cmd = DeclareLaunchArgument(
    name='use_lidar',
    default_value='True',
    description='launch lidar node if true'
  )

  declare_use_camera_cmd = DeclareLaunchArgument(
    name='use_camera',
    default_value='False',
    description='launch camera node if true'
  )

  declare_use_costmap_cmd = DeclareLaunchArgument(
    name='use_costmap',
    default_value='False',
    description='whether to use easynav costmap or simple map'
  )

  #-----------------------------------------------------------------------------
  
  robot_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(hardware_pkg_path,'launch','robot.launch.py')]
            ),
            launch_arguments={
              'use_sim_time': use_sim_time,
              'use_lidar': use_lidar,
              'use_camera': use_camera,
            }.items(),
  )

  slam_mapping_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(navigation_pkg_path,'launch','mapping.launch.py')]
            ), 
            launch_arguments={
              'use_sim_time': use_sim_time,
              'use_costmap': use_costmap
            }.items()
  )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_use_costmap_cmd)
  ld.add_action(declare_use_lidar_cmd)
  ld.add_action(declare_use_camera_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(robot_launch)
  ld.add_action(slam_mapping_launch)

  return ld