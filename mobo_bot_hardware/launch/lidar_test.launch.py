import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition


def generate_launch_description():
    description_pkg_path = get_package_share_directory('mobo_bot_description')

    #--------------------------------------------------------------------------
    rsp_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(description_pkg_path,'launch','rsp.launch.py')]), 
        launch_arguments={'use_sim_time': 'False',
                          'run_gz_sim': 'False'}.items(),
        )
    
    rp_lidar_c1_node = Node(
        package='sllidar_ros2',
        executable='sllidar_node',
        name='sllidar_node',
        parameters=[{'channel_type': 'serial',
                    'serial_port': '/dev/serial/by-path/pci-0000:00:14.0-usb-0:3.2:1.0-port0', 
                    'serial_baudrate': 460800, 
                    'frame_id': 'lidar',
                    'inverted': False, 
                    'angle_compensate': True, 
                    'scan_mode': 'Standard'}
                    ],
        output='screen'
    )

    lidar_angle_filter_node = Node(
        package='mobo_bot_base',
        executable='lidar_angle_filter',
        name='lidar_angle_filter',
        output='screen',
        parameters=[{'scan_topic': "scan"},
                    {'min_angle_deg': -150.0},
                    {'max_angle_deg': 150.0}
                    ],
        remappings=[("filtered_scan", "lidar/scan")]
    )
    
    start_lidar_angle_filter_node_after_rp_lidar_c1_node = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=rp_lidar_c1_node,
            on_exit=[lidar_angle_filter_node],
        )
    )

    #--------------------------------------------------------------------------

    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(rsp_launch)
    ld.add_action(rp_lidar_c1_node)
    ld.add_action(lidar_angle_filter_node)

    return ld      # return (i.e send) the launch description for excecution
