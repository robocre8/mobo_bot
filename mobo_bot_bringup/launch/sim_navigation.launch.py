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
  use_4_wheels = LaunchConfiguration('use_4_wheels')
 
  declare_world_name_cmd = DeclareLaunchArgument(
    name='world_name',
    default_value='room_with_walls',
    description='name of the world file')
  
  declare_use_4_wheels_cmd = DeclareLaunchArgument(
      'use_4_wheels',
      default_value='False',
      description='Use 4 wheels base if true else it uses 2 wheels'
  )
  
  world_path = PathJoinSubstitution([
          sim_pkg_path,
          "worlds",
          PythonExpression(expression=["'", world_name, "'", " + '.sdf'"])
      ]
  )
  
  map_path = PathJoinSubstitution([
          navigation_pkg_path,
          "maps",
          PythonExpression(expression=["'", world_name, "'", " + '.yaml'"])
      ]
  )

  declare_params_name_cmd = DeclareLaunchArgument(
    name='params_name',
    default_value='nav2_bringup_params',
    description='name of the navigation parameter file')
  
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
              'use_4_wheels': use_4_wheels,
              'world_path': world_path,
            }.items(),
  )

  rviz_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(rviz_pkg_path,'launch','robot_navigation.launch.py')]
            )
  )

  nav_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(navigation_pkg_path,'launch','navigation.launch.py')]
            ), 
            launch_arguments={
              'slam': 'False',
              'map': map_path,
              'use_sim_time': 'True',
              'params_file': params_file
            }.items()
  )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_world_name_cmd)
  ld.add_action(declare_params_name_cmd)
  ld.add_action(declare_use_4_wheels_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(sim_launch)
  ld.add_action(rviz_launch)
  ld.add_action(nav_launch)

  return ld
