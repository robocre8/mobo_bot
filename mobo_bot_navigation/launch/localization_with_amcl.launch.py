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
  navigation_pkg_path = get_package_share_directory('mobo_bot_navigation')
  # nav2_bringup_pkg_path = get_package_share_directory('nav2_bringup')

  # Set the path to the nav params file
  nav_params_file_name = 'nav2_params_diff.yaml'
  nav_params_file = os.path.join(navigation_pkg_path, 'config', nav_params_file_name)

  # Set the path to the map file
  map_file_name = 'room_with_walls.yaml'
  map_file = os.path.join(navigation_pkg_path, 'maps', map_file_name)
 
  #--------------------------------------------------------------------------

  # Launch configuration variables specific to simulation
  use_sim_time = LaunchConfiguration('use_sim_time')
  nav_params = LaunchConfiguration('nav_params')
  map = LaunchConfiguration('map')

  declare_use_sim_time_cmd = DeclareLaunchArgument(
      name='use_sim_time', 
      default_value='True',
      description='Flag to enable use_sim_time'
    )
  
  declare_nav_params_cmd = DeclareLaunchArgument(
      name='nav_params',
      default_value=nav_params_file,
      description='file path to the parameter file'
    )
  
  declare_map_cmd = DeclareLaunchArgument(
      name='map',
      default_value=map_file,
      description='file path to the map needed for navigation'
    )

  #-----------------------------------------------------------------------------

  lifecycle_nodes = [
    'map_server',
    'amcl',
  ]

  remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

  nav2_map_server_node = Node(
    package='nav2_map_server',
    executable='map_server',
    name='map_server',
    output='screen',
    parameters=[
      nav_params,
      {'use_sim_time': use_sim_time},
      {'yaml_filename': map}
    ],
    remappings=remappings
  )

  nav2_amcl_node = Node(
    package='nav2_amcl',
    executable='amcl',
    name='amcl',
    output='screen',
    parameters=[
      nav_params,
      {'use_sim_time': use_sim_time},
    ],
    remappings=remappings
  )

  nav2_lifecycle_manager_node = Node(
  package='nav2_lifecycle_manager',
  executable='lifecycle_manager',
  name='lifecycle_manager_localization',
  output='screen',
  parameters=[
    {'use_sim_time': use_sim_time},
    {'autostart': True},
    {'bond_timeout': 0.0},
    {'node_names': lifecycle_nodes},
  ],
)

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_nav_params_cmd)
  ld.add_action(declare_map_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(nav2_map_server_node)
  ld.add_action(nav2_amcl_node)
  ld.add_action(nav2_lifecycle_manager_node)

  return ld
