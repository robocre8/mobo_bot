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
  sim_pkg_path = get_package_share_directory('mobo_bot_sim')
  rviz_pkg_path = get_package_share_directory('mobo_bot_rviz')
  navigation_pkg_path = get_package_share_directory('mobo_bot_navigation')
 
  #--------------------------------------------------------------------------

  # Launch configuration variables specific to simulation
  world_name = LaunchConfiguration('world_name')
  params_name = LaunchConfiguration('params_name')
 
  declare_world_name_cmd = DeclareLaunchArgument(
    name='world_name',
    default_value='room_with_walls',
    description='name of the world file')
  
  world_path = PathJoinSubstitution([
          sim_pkg_path,
          "worlds",
          PythonExpression(expression=["'", world_name, "'", " + '.sdf'"])
      ]
  )

  declare_params_name_cmd = DeclareLaunchArgument(
    name='params_name',
    default_value='nav2_bringup_params',
    description='name of the slam toolbox parameter file')
  
  params_file = PathJoinSubstitution([
          navigation_pkg_path,
          "config",
          PythonExpression(expression=["'", params_name, "'", " + '.yaml'"])
      ]
  )

  #-----------------------------------------------------------------------------
  
  sim_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(sim_pkg_path,'launch','sim.launch.py')]
            ), 
            launch_arguments={
              'use_sim_time': 'True',
              'world_path': world_path,
            }.items(),
  )

  rviz_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(rviz_pkg_path,'launch','robot_mapping.launch.py')]
            )
  )

  slam_mapping_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(navigation_pkg_path,'launch','mapping.launch.py')]
            ), 
            launch_arguments={
              'params_file': params_file
            }.items()
  )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_world_name_cmd)
  ld.add_action(declare_params_name_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(sim_launch)
  ld.add_action(rviz_launch)
  ld.add_action(slam_mapping_launch)

  return ld
