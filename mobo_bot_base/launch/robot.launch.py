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
    # delare any path variable
    description_pkg_path = get_package_share_directory('mobo_bot_description')
    base_pkg_path = get_package_share_directory('mobo_bot_base')

    robot_controllers = os.path.join(base_pkg_path,'config','robot_base_controller.yaml')
    ekf_config_path = os.path.join(base_pkg_path,'config','ekf.yaml')

    #--------------------------------------------------------------------------

    # Launch configuration variables specific to robot (i.e mobo_bot)
    use_ekf = LaunchConfiguration('use_ekf')
    use_lidar = LaunchConfiguration('use_lidar')
    use_camera = LaunchConfiguration('use_camera')
    
    declare_use_ekf_cmd = DeclareLaunchArgument(
      name='use_ekf',
      default_value='False',
      description='fuse odometry and imu data if true')
    
    declare_lidar_cmd = DeclareLaunchArgument(
      name='use_lidar',
      default_value='False',
      description='use lidar if true')
    
    declare_camera_cmd = DeclareLaunchArgument(
      name='use_camera',
      default_value='False',
      description='use camera if true')

    #--------------------------------------------------------------------------

    # create needed nodes or launch files
    rsp_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(description_pkg_path,'launch','rsp.launch.py')]), 
        launch_arguments={'use_sim_time': 'False',
                          'run_gz_sim': 'False'}.items(),
        )
    
    # see -> https://github.com/ros-controls/ros2_control_demos/blob/humble/example_2/bringup/launch/diffbot.launch.py
    # see -> https://control.ros.org/master/doc/ros2_control/controller_manager/doc/userdoc.html
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controllers],
        output="both",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    diff_drive_controller_spawner_no_ekf = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "--param-file",
            robot_controllers,
            "--controller-ros-args",
            """
            -r /diff_drive_controller/cmd_vel:=/cmd_vel
            -r /diff_drive_controller/odom:=/odom
            """
        ],
        condition=UnlessCondition(use_ekf),
    )

    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "--param-file",
            robot_controllers,
            "--controller-ros-args",
            """
            -r /diff_drive_controller/cmd_vel:=/cmd_vel
            -r /diff_drive_controller/odom:=/wheel/odometry
            """
        ],
        condition=IfCondition(use_ekf),
    )

    imu_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "imu_broadcaster",
            "--param-file",
            robot_controllers,
            "--controller-ros-args",
            "-r /imu_broadcaster/imu:=/imu/data",
        ],
        condition=IfCondition(use_ekf),
    )

    ekf_config_path = os.path.join(base_pkg_path,'config','ekf.yaml')
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            ekf_config_path
        ],
        condition=IfCondition(use_ekf),
        remappings=[("odometry/filtered", "/odom")]
    ) 

    # Delay start of robot_controller after `joint_state_broadcaster`
    start_diff_drive_controller_spawner_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_controller_spawner],
        )
    )

    start_diff_drive_controller_spawner_after_joint_state_broadcaster_spawner_no_ekf = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_controller_spawner_no_ekf],
        )
    )

    start_imu_broadcaster_spawner_after_diff_drive_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=diff_drive_controller_spawner,
            on_exit=[imu_broadcaster_spawner],
        )
    )

    start_ekf_node_after_imu_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=imu_broadcaster_spawner,
            on_exit=[ekf_node],
        )
    )

    #--------------------------------------------------------------------------
    
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
        condition=IfCondition(use_lidar),
        output='screen'
    )

    lidar_angle_filter_node = Node(
        package='mobo_bot_base',
        executable='lidar_angle_filter',
        name='lidar_angle_filter',
        output='screen',
        condition=IfCondition(use_lidar),
        parameters=[{'scan_topic': 'scan',
                    'min_angle_deg': -150.0,
                    'max_angle_deg': 150.0}
                    ],
        remappings=[("filtered_scan", "lidar/scan")]
    )

    start_rp_lidar_c1_node_after_diff_drive_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=diff_drive_controller_spawner,
            on_exit=[rp_lidar_c1_node],
        )
    )

    #--------------------------------------------------------------------------

    camera_node = Node(
        package='opencv_ros_camera',
        executable='camera_publisher',
        name='camera_publisher',
        output='screen',
        parameters=[{'frame_id': "camera_optical",
                      'port_no': 2,
                      'frame_width': 640,
                      'frame_height': 480,
                      'compression_format': "jpeg", # you can also use "jpeg"
                      'publish_frequency': 30.0}
                    ],
        condition=IfCondition(use_camera),
    )

    #--------------------------------------------------------------------------


    twist_mux_file_name = 'twist_mux.yaml'
    twist_mux_config_path = os.path.join(base_pkg_path, 'config', twist_mux_file_name)
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


    # Create the launch description and populate
    ld = LaunchDescription()

    # add the necessary declared launch arguments to the launch description
    ld.add_action(declare_use_ekf_cmd)
    ld.add_action(declare_lidar_cmd)
    ld.add_action(declare_camera_cmd)
    

    # Add the nodes to the launch description
    ld.add_action(rsp_launch)
    ld.add_action(controller_manager)
    ld.add_action(joint_state_broadcaster_spawner)
    ld.add_action(start_diff_drive_controller_spawner_after_joint_state_broadcaster_spawner)
    ld.add_action(start_diff_drive_controller_spawner_after_joint_state_broadcaster_spawner_no_ekf)
    ld.add_action(start_imu_broadcaster_spawner_after_diff_drive_controller_spawner)
    ld.add_action(start_ekf_node_after_imu_broadcaster_spawner)
    # ld.add_action(rp_lidar_c1_node)
    ld.add_action(start_rp_lidar_c1_node_after_diff_drive_controller_spawner)
    ld.add_action(lidar_angle_filter_node)
    ld.add_action(camera_node)

    return ld      # return (i.e send) the launch description for excecution
