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
  use_sim_time = LaunchConfiguration('use_sim_time')
  world_name = LaunchConfiguration('world_name')
  headless = LaunchConfiguration('headless')

  declare_use_sim_time_cmd = DeclareLaunchArgument(
    name='use_sim_time',
    default_value='True',
    description='whether to use simulation clock or not'
  )
 
  declare_world_name_cmd = DeclareLaunchArgument(
    name='world_name',
    default_value='room_with_walls',
    description='name of the world file (without extension)'
  )
  
  world_path = PathJoinSubstitution([
          sim_pkg_path,
          "worlds",
          PythonExpression(expression=["'", world_name, "'", " + '.sdf'"])
      ]
  )

  declare_headless_cmd = DeclareLaunchArgument(
    name='headless',
    default_value='False',
    description='run gazebo GUI (False) or not (True)'
  )

  #-----------------------------------------------------------------------------
  sim_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(sim_pkg_path,'launch','sim.launch.py')]
            ), 
            launch_arguments={
              'use_sim_time': 'True',
              'world_path': world_path,
              'headless': headless,
            }.items(),
  )

  rviz_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(rviz_pkg_path,'launch','mapping_and_navigation.launch.py')]
            )
  )

  nav_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(navigation_pkg_path,'launch','navigation.launch.py')]
            ), 
            launch_arguments={
              'use_sim_time': use_sim_time,
            }.items()
  )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_world_name_cmd)
  ld.add_action(declare_headless_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(sim_launch)
  ld.add_action(rviz_launch)
  ld.add_action(nav_launch)

  return ld