import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
  DeclareLaunchArgument,
  IncludeLaunchDescription)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
  # Set the path to this package.
  base_pkg_path = get_package_share_directory('mobo_bot_base')
 
  use_ekf = LaunchConfiguration('use_ekf')

  declare_use_ekf_cmd = DeclareLaunchArgument(
      name='use_ekf',
      default_value='False',
      description='fuse odometry and imu data if true'
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

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()

  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_use_ekf_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(robot_launch)

  return ld