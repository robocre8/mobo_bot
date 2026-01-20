import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
  DeclareLaunchArgument,
  IncludeLaunchDescription)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PythonExpression, LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml, ReplaceString


def generate_launch_description():
  # Set the path to this package.
  mobo_bot_navigation_pkg_path = get_package_share_directory('mobo_bot_navigation')
  nav2_bringup_pkg_path = get_package_share_directory('nav2_bringup')

  # Set the path to the slam params file
  slam_params_file_name = 'slam_toolbox_localization_params.yaml'
  slam_params_file = os.path.join(mobo_bot_navigation_pkg_path, 'config', slam_params_file_name)

  # Set the path to the nav params file
  nav_params_file_name = 'nav2_params_diff.yaml'
  nav_params_file = os.path.join(mobo_bot_navigation_pkg_path, 'config', nav_params_file_name)

  # Set the path to the map file used by AMCL
  map_file_name = 'room_with_walls.yaml'
  map_file = os.path.join(mobo_bot_navigation_pkg_path, 'maps', map_file_name)

  # bt_nav_to_pose_xml = os.path.join(mobo_bot_navigation_pkg_path, 'config', 'bt', 'navigate_to_pose_w_smoothing.xml')
  # bt_nav_through_poses_xml = os.path.join(mobo_bot_navigation_pkg_path, 'config', 'bt', 'navigate_through_pose_w_smoothing.xml')

  # rewritten_nav_params_file = RewrittenYaml(
  #   source_file=nav_params_file,
  #   root_key='',
  #   param_rewrites={
  #       'bt_navigator.ros__parameters.default_nav_to_pose_bt_xml': bt_nav_to_pose_xml,
  #       'bt_navigator.ros__parameters.default_nav_through_poses_bt_xml': bt_nav_through_poses_xml,
  #   },
  #   convert_types=True,
  # )
 
  #--------------------------------------------------------------------------

  # Launch configuration variables specific to simulation
  use_sim_time = LaunchConfiguration('use_sim_time')
  use_localization = LaunchConfiguration('use_localization')
  use_slam = LaunchConfiguration('use_slam')
  slam_params = LaunchConfiguration('slam_params')
  serialized_map_name = LaunchConfiguration('serialized_map_name')
  serialized_map_location = LaunchConfiguration('serialized_map_location')
  nav_params = LaunchConfiguration('nav_params')
  map = LaunchConfiguration('map')

  declare_use_sim_time_cmd = DeclareLaunchArgument(
      name='use_sim_time', 
      default_value='True',
      description='Flag to enable use_sim_time'
    )
  
  declare_use_localization_cmd = DeclareLaunchArgument(
      name='use_localization', 
      default_value='True',
      description='whether to use localization (AMCL or SLAM) or not'
    )
  
  declare_use_slam_cmd = DeclareLaunchArgument(
      name='use_slam', 
      default_value='False',
      description='Flag to enable using slam for localization'
    )
  
  declare_slam_params_cmd = DeclareLaunchArgument(
      name='slam_params',
      default_value=slam_params_file,
      description='file path to the parameter file'
    )
  
  declare_serialized_map_name_cmd = DeclareLaunchArgument(
      name='serialized_map_name',
      default_value='room_with_walls',
      description='name of the serialized_map'
    )
  
  declare_serialized_map_location_cmd = DeclareLaunchArgument(
      name='serialized_map_location',
      default_value=os.path.join(mobo_bot_navigation_pkg_path, 'maps'),
      description='location of the serialized_map'
    )
  
  declare_nav_params_cmd = DeclareLaunchArgument(
      name='nav_params',
      default_value=nav_params_file,
      # default_value=rewritten_nav_params_file,
      description='file path to the parameter file'
    )
  
  declare_map_cmd = DeclareLaunchArgument(
      name='map',
      default_value=map_file,
      description='file path to the map needed for navigation'
    )

  #-----------------------------------------------------------------------------

  localization_with_slam_launch_path = os.path.join(mobo_bot_navigation_pkg_path, 'launch', 'localization_with_slam.launch.py')

  localization_with_slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(localization_with_slam_launch_path),
        launch_arguments={
                'use_sim_time': use_sim_time,
                'slam_params': slam_params,
                'serialized_map_location': serialized_map_location,
                'serialized_map_name': serialized_map_name,
        }.items(),
        condition=IfCondition(
            PythonExpression([
              use_localization, " and ", use_slam
          ])
        )
    )
  


  localization_with_amcl_launch_path = os.path.join(mobo_bot_navigation_pkg_path, 'launch', 'localization_with_amcl.launch.py')

  localization_with_amcl_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(localization_with_amcl_launch_path),
        launch_arguments={
                'use_sim_time': use_sim_time,
                'nav_params': nav_params,
                'map': map,
        }.items(),
        condition=IfCondition(
            PythonExpression([
              use_localization, " and not ", use_slam
          ])
        )
    )

  #--------------------------------------------------------------------------------

  lifecycle_nodes = [
    # 'costmap',
    'planner_server',
    'controller_server',
    'bt_navigator',
    'behavior_server',
    'smoother_server',
    'waypoint_follower',
    'velocity_smoother',
  ]

  remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

  # nav2_costmap_2d_node = Node(
  #   package='nav2_costmap_2d',
  #   executable='nav2_costmap_2d',
  #   name='costmap',
  #   output='screen',
  #   parameters=[
  #     nav_params,
  #     {'use_sim_time': use_sim_time}
  #   ],
  # )

  nav2_planner_server_node = Node(
    package='nav2_planner',
    executable='planner_server',
    name='planner_server',
    output='screen',
    parameters=[
      nav_params,
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
      nav_params,
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
      nav_params,
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
      nav_params,
      {'use_sim_time': use_sim_time}
    ],
    remappings=remappings,
  )

  nav2_behavior_server_node = Node(
    package='nav2_behaviors',
    executable='behavior_server',
    name='behavior_server',
    output='screen',
    parameters=[
      nav_params,
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
      nav_params,
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
      nav_params,
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
  ld.add_action(declare_use_localization_cmd)
  ld.add_action(declare_use_slam_cmd)
  ld.add_action(declare_slam_params_cmd)
  ld.add_action(declare_serialized_map_name_cmd)
  ld.add_action(declare_serialized_map_location_cmd)
  ld.add_action(declare_nav_params_cmd)
  ld.add_action(declare_map_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(localization_with_slam_launch)
  ld.add_action(localization_with_amcl_launch)
  # ld.add_action(nav2_costmap_2d_node)
  ld.add_action(nav2_planner_server_node)
  ld.add_action(nav2_smoother_server_node)
  ld.add_action(nav2_controller_server_node)
  ld.add_action(nav2_bt_navigator_node)
  ld.add_action(nav2_behavior_server_node)
  ld.add_action(nav2_waypoint_follower_node)
  ld.add_action(nav2_velocity_smoother_node)
  ld.add_action(nav2_lifecycle_manager_node)

  return ld
