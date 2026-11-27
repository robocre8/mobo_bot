import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition
from nav2_common.launch import RewrittenYaml, ReplaceString


def generate_launch_description():

    robot_nav_pkg_path = get_package_share_directory('mobo_bot_navigation')


    use_sim_time = LaunchConfiguration('use_sim_time')
    easynav_costmap_params_file = LaunchConfiguration('easynav_costmap_params_file')
    easynav_simple_params_file = LaunchConfiguration('easynav_simple_params_file')
    use_costmap = LaunchConfiguration('use_costmap')
    simple_map_path = LaunchConfiguration('simple_map_path')
    costmap_map_path = LaunchConfiguration('costmap_map_path')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value="True",
        description='whether to use simulation time or not')

    declare_easynav_simple_params_file_cmd = DeclareLaunchArgument(
        'easynav_simple_params_file',
        default_value=os.path.join(robot_nav_pkg_path, 'config', 'easynav_simple_params.yaml'),
        description='Full path to the ROS2 parameters file for easynav simple')

    declare_easynav_costmap_params_file_cmd = DeclareLaunchArgument(
        'easynav_costmap_params_file',
        default_value=os.path.join(robot_nav_pkg_path, 'config', 'easynav_costmap_params.yaml'),
        description='Full path to the ROS2 parameters file for easynav costmap')

    declare_use_costmap_cmd = DeclareLaunchArgument(
        'use_costmap',
        default_value="True",
        description='whether to use easynav simple or costmap')

    declare_world_name_cmd = DeclareLaunchArgument(
        name='world_name',
        default_value='room_with_walls',
        description='name of the world file (without extension)'
    )


    rewritten_easynav_simple_params_file = RewrittenYaml(
        source_file=easynav_simple_params_file,
        root_key='',
        param_rewrites={
            'controller_node.ros__parameters.use_sim_time': use_sim_time,
            'localizer_node.ros__parameters.use_sim_time': use_sim_time,
            'maps_manager_node.ros__parameters.use_sim_time': use_sim_time,
            'planner_node.ros__parameters.use_sim_time': use_sim_time,
            'sensor_node.ros__parameters.use_sim_time': use_sim_time,
            'system_node.ros__parameters.use_sim_time': use_sim_time,
            
            'maps_manager_node.ros__parameters.simple.map_path_file': simple_map_path,
        },
        convert_types=True,
    )


    rewritten_easynav_costmap_params_file = RewrittenYaml(
        source_file=easynav_costmap_params_file,
        root_key='',
        param_rewrites={
            'controller_node.ros__parameters.use_sim_time': use_sim_time,
            'localizer_node.ros__parameters.use_sim_time': use_sim_time,
            'maps_manager_node.ros__parameters.use_sim_time': use_sim_time,
            'planner_node.ros__parameters.use_sim_time': use_sim_time,
            'sensor_node.ros__parameters.use_sim_time': use_sim_time,
            'system_node.ros__parameters.use_sim_time': use_sim_time,

            'maps_manager_node.ros__parameters.costmap.map_path_file': costmap_map_path,
        },
        convert_types=True,
    )


    easynav_system_simple = Node(
        package='easynav_system',
        executable='system_main',
        parameters=[
            rewritten_easynav_simple_params_file
        ],
        output='screen',
        remappings=[
            ('/cmd_vel', '/cmd_vel_easynav'),
        ],
        condition=UnlessCondition(use_costmap)
    )
  
    easynav_system_costmap = Node(
        package='easynav_system',
        executable='system_main',
        parameters=[
            rewritten_easynav_costmap_params_file
        ],
        output='screen',
        remappings=[
            ('/cmd_vel', '/cmd_vel_easynav'),
        ],
        condition=IfCondition(use_costmap)
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



    ld = LaunchDescription()

    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_easynav_simple_params_file_cmd)
    ld.add_action(declare_easynav_costmap_params_file_cmd)
    ld.add_action(declare_easynav_simple_params_file_cmd)
    ld.add_action(declare_use_costmap_cmd)
    ld.add_action(declare_world_name_cmd)

    ld.add_action(easynav_system_costmap)
    ld.add_action(easynav_system_simple)
    ld.add_action(twist_stamper)

    return ld