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
  params_name = LaunchConfiguration('params_name')
  use_ekf = LaunchConfiguration('use_ekf')

  declare_use_ekf_cmd = DeclareLaunchArgument(
      name='use_ekf',
      default_value='False',
      description='fuse odometry and imu data if true'
  )

  declare_params_name_cmd = DeclareLaunchArgument(
    name='params_name',
    default_value='robot_nav2_params_diff',
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
              'use_ekf': use_ekf,
              'use_lidar': 'True',
              'use_camera': 'True',
            }.items(),
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
  ld.add_action(declare_params_name_cmd)
  ld.add_action(declare_use_ekf_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(robot_launch)
  ld.add_action(slam_mapping_launch)

  return ld