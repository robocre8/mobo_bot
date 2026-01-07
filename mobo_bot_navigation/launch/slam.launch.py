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

  # Set the path to the nav params file
  nav_params_file_name = 'slam_localization_params.yaml'
  nav_params_file = os.path.join(navigation_pkg_path, 'config', nav_params_file_name)
 
  #--------------------------------------------------------------------------

  # Launch configuration variables specific to simulation
  use_sim_time = LaunchConfiguration('use_sim_time')
  use_lifecycle_manager = LaunchConfiguration('use_lifecycle_manager')
  params_file = LaunchConfiguration('params_file')
  
  declare_params_file_cmd = DeclareLaunchArgument(
      name='params_file',
      default_value=nav_params_file,
      description='file path to the navigation paramater file needed for navigation')
  
  declare_use_sim_time_cmd = DeclareLaunchArgument(
    name='use_sim_time',
    default_value='True',
    description='Use simulation (Gazebo) clock if true')
  
  declare_use_lifecycle_manager_cmd = DeclareLaunchArgument(
    name='use_lifecycle_manager',
    default_value='True',
    description='use_lifecycle_manager')

  #-----------------------------------------------------------------------------

  lifecycle_nodes = [
    'slam_toolbox',
  ]

  slam_localization_node = Node(
      package='slam_toolbox',
      executable='localization_slam_toolbox_node',
      name='slam_toolbox',
      output='screen',
      parameters=[
        {
          'use_lifecycle_manager': use_lifecycle_manager,
          'use_sim_time': use_sim_time
        },
        params_file
      ],
    )
  
  nav2_lifecycle_manager_node = Node(
    package='nav2_lifecycle_manager',
    executable='lifecycle_manager',
    output='screen',
    parameters=[{"autostart": True, "bond_timeout": 0.0}, {'node_names': lifecycle_nodes}],
  )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_params_file_cmd)
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_use_lifecycle_manager_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(slam_localization_node)
  ld.add_action(nav2_lifecycle_manager_node)

  return ld
