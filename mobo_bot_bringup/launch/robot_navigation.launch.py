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
  use_ekf = LaunchConfiguration('use_ekf')
  use_sim_time = LaunchConfiguration('use_sim_time')
  slam_params_name = LaunchConfiguration('slam_params_name')
  nav_params_name = LaunchConfiguration('nav_params_name')
  serialized_map_name = LaunchConfiguration('serialized_map_name')
  serialized_map_location = LaunchConfiguration('serialized_map_location')
  use_slam = LaunchConfiguration('use_slam')

  declare_use_ekf_cmd = DeclareLaunchArgument(
      name='use_ekf',
      default_value='False',
      description='fuse odometry and imu data if true'
  )

  declare_map_name_cmd = DeclareLaunchArgument(
    name='map_name',
    default_value='',
    description='name of the map file')
  
  map_path = PathJoinSubstitution([
          navigation_pkg_path,
          "maps",
          PythonExpression(expression=["'", map_name, "'", " + '.yaml'"])
      ]
  )  

  declare_use_sim_time_cmd = DeclareLaunchArgument(
    name='use_sim_time',
    default_value='False',
    description='whether to use simulation clock or not'
  )


  declare_nav_params_name_cmd = DeclareLaunchArgument(
    name='nav_params_name',
    default_value='nav2_params',
    description='name of the nav2 parameter file (without extension)'
  )
  
  nav_params_file = PathJoinSubstitution([
          navigation_pkg_path,
          "config",
          PythonExpression(expression=["'", nav_params_name, "'", " + '.yaml'"])
      ]
  )

  declare_slam_params_name_cmd = DeclareLaunchArgument(
    name='slam_params_name',
    default_value='slam_toolbox_localization_params',
    description='name of the slam toolbox parameter file (without extension)'
  )

  slam_params_file = PathJoinSubstitution([
          navigation_pkg_path,
          "config",
          PythonExpression(expression=["'", slam_params_name, "'", " + '.yaml'"])
      ]
  )

  declare_serialized_map_name_cmd = DeclareLaunchArgument(
      name='serialized_map_name',
      default_value='',
      description='name of the serialized_map (without extension)'
    )
  
  declare_serialized_map_location_cmd = DeclareLaunchArgument(
      name='serialized_map_location',
      default_value=os.path.join(navigation_pkg_path, 'maps'),
      description='location of the serialized_map'
    )

  declare_use_slam_cmd = DeclareLaunchArgument(
    name='use_slam',
    default_value='False',
    description='whether to use navigation while mapping'
  )
 
  #-----------------------------------------------------------------------------

  robot_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(base_pkg_path,'launch','robot.launch.py')]
            ),
            launch_arguments={
              'use_sim_time': use_sim_time,
              'use_ekf': use_ekf,
              'use_lidar': 'True',
              'use_camera': 'True',
            }.items(),
  )

  nav_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(navigation_pkg_path,'launch','navigation.launch.py')]
            ), 
            launch_arguments={
              'use_sim_time': use_sim_time,
              'use_slam': use_slam,
              'nav_params': nav_params_file,
              'map': map_path,
              'slam_params': slam_params_file,
              'serialized_map_name': serialized_map_name,
              'serialized_map_location': serialized_map_location,
            }.items()
  )

  #--------------------------------------------------------------------------------

  # Create the launch description
  ld = LaunchDescription()
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_map_name_cmd)
  ld.add_action(declare_use_ekf_cmd)
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_nav_params_name_cmd)
  ld.add_action(declare_slam_params_name_cmd)
  ld.add_action(declare_use_slam_cmd)
  ld.add_action(declare_serialized_map_name_cmd)
  ld.add_action(declare_serialized_map_location_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(robot_launch)
  ld.add_action(nav_launch)

  return ld