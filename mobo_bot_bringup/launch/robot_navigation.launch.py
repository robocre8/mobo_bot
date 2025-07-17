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
  base_pkg_path = get_package_share_directory('mobo_bot_base')
  navigation_pkg_path = get_package_share_directory('mobo_bot_navigation')

  #--------------------------------------------------------------------------

  # Launch configuration variables specific to simulation
  map_name = LaunchConfiguration('map_name')
  params_name = LaunchConfiguration('params_name')

  declare_map_name_cmd = DeclareLaunchArgument(
    name='map_name',
    default_value='simple_world_map',
    description='name of the map file')
  
  map_path = PathJoinSubstitution([
          navigation_pkg_path,
          "maps",
          PythonExpression(expression=["'", map_name, "'", " + '.yaml'"])
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

  robot_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(base_pkg_path,'launch','robot.launch.py')]
            ),
            launch_arguments={
              'use_sim_time': 'False',
              'use_ekf': 'True',
              'use_lidar': 'True',
              'use_camera': 'True',
            }.items(),
  )

  nav_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(navigation_pkg_path,'launch','nav_bringup.launch.py')]
            ), 
            launch_arguments={
              'slam': 'False',
              'map': map_path,
              'use_sim_time': 'False',
              'params_file': params_file
            }.items()
  )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_map_name_cmd)
  ld.add_action(declare_params_name_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(robot_launch)
  ld.add_action(nav_launch)

  return ld
