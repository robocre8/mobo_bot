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
  map_name = LaunchConfiguration('map_name')
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

  declare_map_name_cmd = DeclareLaunchArgument(
    name='map_name',
    default_value='',
    description='name of the map file (without extension)'
  )
  
  simple_map_path = PathJoinSubstitution([
          "maps", "hardware",
          PythonExpression(expression=["'", map_name, "'", " + '.map'"])
      ]
  )

  costmap_map_path = PathJoinSubstitution([
          "maps", "hardware",
          PythonExpression(expression=["'", map_name, "'", " + '.yaml'"])
      ]
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

  nav_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(navigation_pkg_path,'launch','navigation.launch.py')]
            ), 
            launch_arguments={
              'use_sim_time': use_sim_time,
              'use_costmap': use_costmap,
              'simple_map_path': simple_map_path,
              'costmap_map_path': costmap_map_path
            }.items()
  )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_use_costmap_cmd)
  ld.add_action(declare_map_name_cmd)
  ld.add_action(declare_use_lidar_cmd)
  ld.add_action(declare_use_camera_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(robot_launch)
  ld.add_action(nav_launch)

  return ld