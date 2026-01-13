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
from nav2_common.launch import ReplaceString, RewrittenYaml


def generate_launch_description():
  # Set the path to this package.
  navigation_pkg_path = get_package_share_directory('mobo_bot_navigation')
  slam_toolbox_pkg_path = get_package_share_directory('slam_toolbox')

  # Set the path to the nav params file
  slam_params_file_name = 'slam_toolbox_localization_params.yaml'
  slam_params_file = os.path.join(navigation_pkg_path, 'config', slam_params_file_name)
 
  #--------------------------------------------------------------------------

  # Launch configuration variables specific to simulation
  use_sim_time = LaunchConfiguration('use_sim_time')
  slam_params = LaunchConfiguration('slam_params')
  serialized_map_name = LaunchConfiguration('serialized_map_name')
  serialized_map_location = LaunchConfiguration('serialized_map_location')

  declare_use_sim_time_cmd = DeclareLaunchArgument(
      name='use_sim_time', 
      default_value='True',
      description='Flag to enable use_sim_time'
    )

  declare_serialized_map_name_cmd = DeclareLaunchArgument(
      name='serialized_map_name',
      default_value='room_with_walls',
      description='name of the serialized_map'
    )
  
  declare_serialized_map_location_cmd = DeclareLaunchArgument(
      name='serialized_map_location',
      default_value=os.path.join(navigation_pkg_path, 'maps'),
      description='location of the serialized_map'
    )
  
  declare_slam_params_cmd = DeclareLaunchArgument(
      name='slam_params',
      default_value=slam_params_file,
      description='file path to the parameter file'
    )
  
  rewritten_slam_params_file = ReplaceString(
      source_file=slam_params,
      replacements={
        '<map_file_location>': serialized_map_location,
        '<map_file_name>': serialized_map_name
      },
  )
  #-----------------------------------------------------------------------------

  # Path to the Slam Toolbox launch file
  slam_toolbox_launch_path = os.path.join(slam_toolbox_pkg_path, 'launch', 'localization_launch.py')

  slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_toolbox_launch_path),
        launch_arguments={
                'use_sim_time': use_sim_time,
                'slam_params_file': rewritten_slam_params_file,
        }.items()
    )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_slam_params_cmd)
  ld.add_action(declare_serialized_map_name_cmd)
  ld.add_action(declare_serialized_map_location_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(slam_toolbox_launch)

  return ld
