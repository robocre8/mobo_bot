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
  nav2_bt_navigator_pkg_path = get_package_share_directory('nav2_bt_navigator')
 
  # Set the path to the map file
  map_file_name = 'room_with_walls.yaml'
  map_yaml_path = os.path.join(navigation_pkg_path, 'maps', map_file_name)

  # Set the path to the nav params file
  nav_params_file_name = 'sim_nav2_params_diff.yaml'
  nav_params_file = os.path.join(navigation_pkg_path, 'config', nav_params_file_name)

  default_nav_to_pose_bt_xml = os.path.join(navigation_pkg_path, 'config', 'navigate_to_pose_w_smoothing.xml')
  default_nav_through_pose_bt_xml = os.path.join(navigation_pkg_path, 'config', 'navigate_through_pose_w_smoothing.xml')

  # default_nav_to_pose_bt_xml = os.path.join(nav2_bt_navigator_pkg_path, 'behavior_trees', 'navigate_to_pose_w_replanning_and_recovery.xml')
  # default_nav_through_pose_bt_xml = os.path.join(nav2_bt_navigator_pkg_path, 'behavior_trees', 'navigate_through_poses_w_replanning_and_recovery.xml')
 
  #--------------------------------------------------------------------------

  # Launch configuration variables specific to simulation
  use_sim_time = LaunchConfiguration('use_sim_time')
  map = LaunchConfiguration('map')
  params_file = LaunchConfiguration('params_file')
  slam = LaunchConfiguration('slam')
     
  declare_use_sim_time_cmd = DeclareLaunchArgument(
    name='use_sim_time',
    default_value='True',
    description='Use simulation (Gazebo) clock if true')
  
  declare_map_cmd = DeclareLaunchArgument(
      name='map',
      default_value=map_yaml_path,
      description='file path to the map needed for navigation')
  
  declare_params_file_cmd = DeclareLaunchArgument(
      name='params_file',
      default_value=nav_params_file,
      description='file path to the navigation paramater file needed for navigation')
  
  declare_slam_cmd = DeclareLaunchArgument(
      name='slam',
      default_value='False',
      description='file path to the map needed for navigation')

  #-----------------------------------------------------------------------------
  amcl_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(navigation_pkg_path,'launch','amcl.launch.py')]
            ), 
            launch_arguments={
              'params_file': params_file
            }.items(),
            condition=UnlessCondition(slam)
  )

  slam_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(navigation_pkg_path,'launch','slam.launch.py')]
            ), 
            launch_arguments={
              'params_file': params_file
            }.items(),
            condition=IfCondition(slam)
  )

  lifecycle_nodes = [
    # 'costmap',
    'planner_server',
    'controller_server',
    'bt_navigator',
    'behavior_server',
    'smoother_server',
    'waypoint_follower',
    # 'velocity_smoother',
  ]

  remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

  # nav2_costmap_2d_node = Node(
  #   package='nav2_costmap_2d',
  #   executable='nav2_costmap_2d',
  #   name='costmap',
  #   output='screen',
  #   parameters=[
  #     params_file,
  #     {'use_sim_time': use_sim_time}
  #   ],
  # )

  nav2_planner_server_node = Node(
    package='nav2_planner',
    executable='planner_server',
    name='planner_server',
    output='screen',
    parameters=[
      params_file,
      {'use_sim_time': use_sim_time}
    ],
    remappings=remappings,
  )

  nav2_smoother_server_node = Node(
    package='nav2_smoother',
    executable='smoother_server',
    name='smoother_server',
    output='screen',
    parameters=[
      params_file,
      {'use_sim_time': use_sim_time}
    ],
    remappings=remappings,
  )

  nav2_controller_server_node = Node(
    package='nav2_controller',
    executable='controller_server',
    name='controller_server',
    output='screen',
    parameters=[
      params_file,
      {'use_sim_time': use_sim_time}
    ],
    remappings=remappings + [('cmd_vel', 'cmd_vel_nav')],
  )

  nav2_bt_navigator_node = Node(
    package='nav2_bt_navigator',
    executable='bt_navigator',
    name='bt_navigator',
    output='screen',
    parameters=[
      params_file,
      {'use_sim_time': use_sim_time},
      {'default_nav_to_pose_bt_xml': default_nav_to_pose_bt_xml},
      {'default_nav_through_pose_bt_xml': default_nav_through_pose_bt_xml}
    ],
    remappings=remappings,
  )

  nav2_behavior_server_node = Node(
    package='nav2_behaviors',
    executable='behavior_server',
    name='behavior_server',
    output='screen',
    parameters=[
      params_file,
      {'use_sim_time': use_sim_time}
    ],
    remappings=remappings + [('cmd_vel', 'cmd_vel_nav')],
  )

  nav2_waypoint_follower_node = Node(
    package='nav2_waypoint_follower',
    executable='waypoint_follower',
    name='waypoint_follower',
    output='screen',
    parameters=[
      params_file,
      {'use_sim_time': use_sim_time}
    ],
    remappings=remappings,
  )

  nav2_velocity_smoother_node = Node(
    package='nav2_velocity_smoother',
    executable='velocity_smoother',
    name='velocity_smoother',
    output='screen',
    parameters=[
      params_file,
      {'use_sim_time': use_sim_time}
    ],
    remappings=remappings
    + [('cmd_vel', 'cmd_vel_nav')],
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
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_map_cmd)
  ld.add_action(declare_params_file_cmd)
  ld.add_action(declare_slam_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(amcl_launch)
  ld.add_action(slam_launch)
  # ld.add_action(nav2_costmap_2d_node)
  ld.add_action(nav2_planner_server_node)
  ld.add_action(nav2_smoother_server_node)
  ld.add_action(nav2_controller_server_node)
  ld.add_action(nav2_bt_navigator_node)
  ld.add_action(nav2_behavior_server_node)
  ld.add_action(nav2_waypoint_follower_node)
  # ld.add_action(nav2_velocity_smoother_node)
  ld.add_action(nav2_lifecycle_manager_node)

  return ld
