import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
  DeclareLaunchArgument,
  IncludeLaunchDescription)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
  # Set the path to this package.
  description_pkg_path = get_package_share_directory('mobo_bot_description')
  rviz_pkg_path = get_package_share_directory('mobo_bot_rviz')
 
  #--------------------------------------------------------------------------

  use_hardware = LaunchConfiguration('use_hardware')
  use_sim_time = LaunchConfiguration('use_sim_time')
  use_4_wheels = LaunchConfiguration('use_4_wheels')
  run_gz_sim = LaunchConfiguration('run_gz_sim')
  
  # declare launch arguments
  declare_use_hardware_cmd = DeclareLaunchArgument(
      'use_hardware',
      default_value='False',
      description='are you running the actual robot hardware'
  )

  declare_use_sim_time_cmd = DeclareLaunchArgument(
      'use_sim_time',
      default_value='False',
      description='Use sim time if true'
  )

  declare_use_4_wheels_cmd = DeclareLaunchArgument(
      'use_4_wheels',
      default_value='False',
      description='Use 4 wheels base if true else it uses 2 wheels'
  )

  declare_run_gz_sim_cmd = DeclareLaunchArgument(
      'run_gz_sim',
      default_value='False',
      description='are you running the actual robot hardware'
  )

  #-----------------------------------------------------------------------------
  rsp_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(description_pkg_path,'launch','rsp.launch.py')]), 
        launch_arguments={'use_sim_time': use_sim_time,
                          'use_4_wheels': use_4_wheels,
                          'run_gz_sim': run_gz_sim,
                          'use_joint_state_pub': 'True'}.items(),
        condition=UnlessCondition(use_hardware)
        )

  rviz_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(rviz_pkg_path,'launch','rsp.launch.py')]
            )
  )

  rqt_tf_tree_node = Node(
      package='rqt_tf_tree',
      executable='rqt_tf_tree',
      output='screen',
  )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_use_hardware_cmd)
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_use_4_wheels_cmd)
  ld.add_action(declare_run_gz_sim_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(rsp_launch)
  ld.add_action(rviz_launch)
  ld.add_action(rqt_tf_tree_node)

  return ld
