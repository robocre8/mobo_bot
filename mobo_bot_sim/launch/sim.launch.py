import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
  DeclareLaunchArgument,
  ExecuteProcess,
  IncludeLaunchDescription,
  RegisterEventHandler,
  SetEnvironmentVariable)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit

from nav2_common.launch import ReplaceString

 
def generate_launch_description():
  # Set the path to this package.
  description_pkg_path = get_package_share_directory('mobo_bot_description')
  sim_pkg_path = get_package_share_directory('mobo_bot_sim') 

  # initial robot pose
  x_pos = 0.0; y_pos = 0.0; z_pos = 1.0; yaw = 0.0

  # Set the path to the world file
  # world_file_name = 'simple_world.sdf'
  world_file_name = 'room_with_walls.sdf'
  world_file_path = os.path.join(sim_pkg_path, 'worlds', world_file_name)
 
  #--------------------------------------------------------------------------

  # set some ignition environment variable
  gz_models_path = os.path.join(sim_pkg_path, "models")
  gz_sim_system_plugin_path = '/opt/ros/jazzy/lib/'

  set_env_gz_sim_resource_cmd = SetEnvironmentVariable(
          name="GZ_SIM_RESOURCE_PATH",
          value=gz_models_path,
      )
  
  set_env_gz_sim_path_cmd = SetEnvironmentVariable(
          name="GZ_SIM_SYSTEM_PLUGIN_PATH",
          value=gz_sim_system_plugin_path,
      )

  #--------------------------------------------------------------------------
 
  # Launch configuration variables specific to simulation
  headless = LaunchConfiguration('headless')
  use_sim_time = LaunchConfiguration('use_sim_time')
  world_path = LaunchConfiguration('world_path')
  gz_verbosity = LaunchConfiguration('gz_verbosity')
  robot_name = LaunchConfiguration('robot_name')
 
  declare_headless_cmd = DeclareLaunchArgument(
    name='headless',
    default_value='False',
    description='Whether to run only gzserver')
     
  declare_use_sim_time_cmd = DeclareLaunchArgument(
    name='use_sim_time',
    default_value='True',
    description='Use simulation (Gazebo) clock if true')
 
  declare_world_path_cmd = DeclareLaunchArgument(
    name='world_path',
    default_value=world_file_path,
    description='Full path to the world model file to load')
  
  declare_gz_verbosity_cmd = DeclareLaunchArgument(
    'gz_verbosity',
    default_value= '3',
    description='Verbosity level for Ignition Gazebo (0~4).')
  
  declare_robot_name_cmd = DeclareLaunchArgument(
      name='robot_name',
      default_value='mobo_bot',
      description='name of the robot')

  #--------------------------------------------------------------------------

  # Specify the actions
  rsp_launch = IncludeLaunchDescription(
      PythonLaunchDescriptionSource(
          [os.path.join(description_pkg_path,'launch','rsp.launch.py')]
      ), 
      launch_arguments={'use_sim_time': use_sim_time,
                        'run_gz_sim': 'True'}.items()
  )

  start_gz_sim = ExecuteProcess(
      condition=UnlessCondition(headless),
      cmd=['gz', 'sim',  '-r', '-v', gz_verbosity, world_path],
      output='screen',
      # shell=False,
  )
        
  start_gz_sim_headless = ExecuteProcess(
      condition=IfCondition(headless),
      cmd=['gz', 'sim',  '-r', '-v', gz_verbosity, '-s', '--headless-rendering', world_path],
      output='screen',
      # shell=False,
  )
        
  gz_bridge_config_file_path = os.path.join(sim_pkg_path, 'config', 'gz_bridge_config.yaml')

  gz_bridge_node = Node(
      package='ros_gz_bridge',
      executable='parameter_bridge',
      output='screen',
      parameters=[
        # { 'config_file': bridge_config }
        {'config_file': gz_bridge_config_file_path }
      ],
  )

  image_compress_node = Node(
      package='image_transport',
      executable='republish',
      name='raw_to_compressed_republisher',
      output='screen',
      parameters=[
          {'jpeg_quality': 50} 
      ],
      remappings=[
          ('in', '/camera_optical/image'),
          ('out', '/camera_optical/image_raw'),
          ('out/compressed', '/camera_optical/image_raw/compressed'),
          ('out/compressedDepth', '/camera_optical/image_raw/compressedDepth'),
          ('out/theora', '/camera_optical/image_raw/theora'),
          ('out/zstd', '/camera_optical/image_raw/zstd')
      ]
  )
  
  spawn_entity_in_ign = Node(
      package='ros_gz_sim',
      executable='create',
      output='screen',
      arguments=[
          '-topic', 'robot_description', 
          '-name', robot_name,
          '-x', str(x_pos),
          '-y', str(y_pos),
          '-z', str(z_pos),
          '-Y', str(yaw),
          ],
      parameters=[{"use_sim_time": use_sim_time}]
  )

  twist_mux_file_name = 'twist_mux.yaml'
  twist_mux_config_path = os.path.join(sim_pkg_path, 'config', twist_mux_file_name)
  twist_mux_node = Node(
    package='twist_mux',
    executable='twist_mux',
    name='twist_mux',
    output='screen',
    parameters=[twist_mux_config_path],
    remappings=[
        ('cmd_vel_out', '/cmd_vel')  # final merged velocity topic
    ]
  )

  #--------------------------------------------------------------------------
  
  # Create the launch description
  ld = LaunchDescription()

  ld.add_action(set_env_gz_sim_resource_cmd)
  ld.add_action(set_env_gz_sim_path_cmd)
 
  # add the necessary declared launch arguments to the launch description
  ld.add_action(declare_headless_cmd)
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_world_path_cmd)
  ld.add_action(declare_gz_verbosity_cmd)
  ld.add_action(declare_robot_name_cmd)
 
  # Add the nodes to the launch description
  ld.add_action(rsp_launch)
  ld.add_action(start_gz_sim)
  ld.add_action(start_gz_sim_headless)
  ld.add_action(gz_bridge_node)
  ld.add_action(image_compress_node)
  ld.add_action(spawn_entity_in_ign)
  ld.add_action(twist_mux_node)

 
  return ld