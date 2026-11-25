import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition


def generate_launch_description():

  robot_nav_pkg_path = get_package_share_directory('mobo_bot_navigation')
  easynav_costmap_params_file = LaunchConfiguration('easynav_costmap_params_file')
  # rviz_config = LaunchConfiguration('rviz_config')
  
  declare_easynav_costmap_params_file_cmd = DeclareLaunchArgument(
          'easynav_costmap_params_file',
          default_value=os.path.join(robot_nav_pkg_path, 'config', 'easynav_costmap_params.yaml'),
          description='Full path to the ROS2 parameters file for easynav')
  

  # declare_rviz_config_cmd = DeclareLaunchArgument(
  #     'rviz_config',
  #     default_value=os.path.join(
  #         bringup_dir, 'rviz_config', 'easynav_simple.rviz'),
  #     description='Full path to the RViz2 configuration file',
  # )

  easynav_system_costmap = Node(
      package='easynav_system',
      executable='system_main',
      parameters=[easynav_costmap_params_file],
      output='screen',
      remappings=[
          ('/cmd_vel', '/cmd_vel_easynav'),
      ]
  )

  twist_stamper = Node(
      package='twist_stamper',
      executable='twist_stamper',
      parameters=[
          {"frame_id": "odom"}
      ],
      output='screen',
      remappings=[
          ('/cmd_vel_in', '/cmd_vel_easynav'),
          ('/cmd_vel_out', '/cmd_vel_nav'),
      ],
    )

  # rviz_cmd = Node(
  #     package='rviz2',
  #     executable='rviz2',
  #     arguments=['-d', rviz_config],
  #     parameters=[{'use_sim_time': True}],
  #     output='screen',
  # )


  ld = LaunchDescription()

  ld.add_action(declare_easynav_costmap_params_file_cmd)
  # ld.add_action(declare_rviz_config_cmd)

  ld.add_action(easynav_system_costmap)
  ld.add_action(twist_stamper)
  # ld.add_action(rviz_cmd)

  return ld