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
 
  #--------------------------------------------------------------------------

  # Launch configuration variables specific to simulation
  world_name = LaunchConfiguration('world_name')
  headless = LaunchConfiguration('headless')
  use_rviz = LaunchConfiguration('use_rviz')
 
  declare_world_name_cmd = DeclareLaunchArgument(
    name='world_name',
    default_value='room_with_walls',
    description='name of the world file (without extension)')
  
  world_path = PathJoinSubstitution([
          sim_pkg_path,
          "worlds",
          PythonExpression(expression=["'", world_name, "'", " + '.sdf'"])
      ]
  )

  declare_headless_cmd = DeclareLaunchArgument(
    name='headless',
    default_value='False',
    description='run gazebo GUI (False) or not (True)')

  declare_use_rviz_cmd = DeclareLaunchArgument(
    name='use_rviz',
    default_value='True',
    description='whether to run rviz (True) or not (False)')

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
              [os.path.join(rviz_pkg_path,'launch','robot.launch.py')]
            ),
            condition=IfCondition(use_rviz)
  )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_world_name_cmd)
  ld.add_action(declare_headless_cmd)
  ld.add_action(declare_use_rviz_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(sim_launch)
  ld.add_action(rviz_launch)

  return ld