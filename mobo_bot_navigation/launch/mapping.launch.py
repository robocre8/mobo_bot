import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
  DeclareLaunchArgument,
  IncludeLaunchDescription)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
  # Set the path to this package.
  mobo_bot_navigation_pkg_path = get_package_share_directory('mobo_bot_navigation')
  slam_toolbox_pkg_path = get_package_share_directory('slam_toolbox')
  nav2_bringup_pkg_path = get_package_share_directory('nav2_bringup')

  # Set the path to the nav params file
  slam_params_file_name = 'slam_toolbox_mapping_params.yaml'
  slam_params_file = os.path.join(mobo_bot_navigation_pkg_path, 'config', slam_params_file_name)

  # Set the path to the nav params file
  nav_params_file_name = 'nav2_params.yaml'
  nav_params_file = os.path.join(mobo_bot_navigation_pkg_path, 'config', nav_params_file_name)
 
  #--------------------------------------------------------------------------

  # Launch configuration variables specific to simulation
  use_sim_time = LaunchConfiguration('use_sim_time')
  slam_params = LaunchConfiguration('slam_params')
  nav_params = LaunchConfiguration('nav_params')
  use_nav = LaunchConfiguration('use_nav')

  declare_use_sim_time_cmd = DeclareLaunchArgument(
      name='use_sim_time', 
      default_value='True',
      description='Flag to enable use_sim_time'
    )
  
  declare_slam_params_cmd = DeclareLaunchArgument(
      name='slam_params',
      default_value=slam_params_file,
      description='file path to the parameter file'
    )
  
  declare_use_nav_cmd = DeclareLaunchArgument(
      name='use_nav', 
      default_value='False',
      description='Flag to enable navigation while mapping'
    )
  
  declare_nav_params_cmd = DeclareLaunchArgument(
      name='nav_params',
      default_value=nav_params_file,
      description='file path to the parameter file'
    )

  #-----------------------------------------------------------------------------

  # Path to the Slam Toolbox launch file
  slam_toolbox_launch_path = os.path.join(slam_toolbox_pkg_path, 'launch', 'online_async_launch.py')

  slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_toolbox_launch_path),
        launch_arguments={
                'use_sim_time': use_sim_time,
                'slam_params_file': slam_params,
        }.items()
    )
  
  navigation_launch_path = os.path.join(nav2_bringup_pkg_path, 'launch', 'navigation_launch.py')

  navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(navigation_launch_path),
        launch_arguments={
                'use_sim_time': use_sim_time,
                'params_file': nav_params,
        }.items(),
        condition=IfCondition(use_nav)
    )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_slam_params_cmd)
  ld.add_action(declare_use_nav_cmd)
  ld.add_action(declare_nav_params_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(slam_toolbox_launch)
  ld.add_action(navigation_launch)

  return ld
