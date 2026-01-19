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

    eimu_config_file = os.path.join(base_pkg_path,'config','eimu_params.yaml')
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

    valid_base_types = ['2WD', '4WD', 'MEC', '22WD']
    base_type = os.environ.get("MOBOBOT_BASE_TYPE")

    if base_type is None:
        print("[ERROR]: MOBOBOT_BASE_TYPE environment variable not found")
        exit(1)
    elif base_type not in valid_base_types:
        print(f"[ERROR]: Invalid MOBOBOT_BASE_TYPE='{base_type}'. Expected one of {valid_base_types}")
        exit(1)

    print(f"Launching robot with {base_type} configuration")

    robot_controller = None

    if base_type == valid_base_types[0]:
        robot_controller = os.path.join(base_pkg_path,'config','robot_base_controller_2WD.yaml')
    elif base_type == valid_base_types[1]:
        robot_controller = os.path.join(base_pkg_path,'config','robot_base_controller_4WD.yaml')
    elif base_type == valid_base_types[2]:
        robot_controller = os.path.join(base_pkg_path,'config','robot_base_controller_MEC.yaml')
    elif base_type == valid_base_types[3]:
        robot_controller = os.path.join(base_pkg_path,'config','robot_base_controller_22WD.yaml')

    #----------------------------------------------------------------------------

    # create needed nodes or launch files
    rsp_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(description_pkg_path,'launch','rsp.launch.py')]), 
        launch_arguments={'use_sim_time': 'False',
                          'base_type': base_type,
                          'run_gz_sim': 'False'}.items(),
        )
    
    # see -> https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_2/bringup/launch/diffbot.launch.py
    # see -> https://control.ros.org/master/doc/ros2_control/controller_manager/doc/userdoc.html
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controller],
        output="both",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    if base_type == 'MEC':
        robot_base_controller_spawner_no_ekf = Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "mecanum_drive_controller",
                "--param-file",
                robot_controller,
                "--controller-ros-args",
                """
                -r /mecanum_drive_controller/cmd_vel:=/cmd_vel
                -r /mecanum_drive_controller/odom:=/odom
                """
            ],
            condition=UnlessCondition(use_ekf),
        )

        robot_base_controller_spawner = Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "mecanum_drive_controller",
                "--param-file",
                robot_controller,
                "--controller-ros-args",
                """
                -r /mecanum_drive_controller/cmd_vel:=/cmd_vel
                -r /mecanum_drive_controller/odom:=/wheel/odometry
                """
            ],
            condition=IfCondition(use_ekf),
        )

    else:
        robot_base_controller_spawner_no_ekf = Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "diff_drive_controller",
                "--param-file",
                robot_controller,
                "--controller-ros-args",
                """
                -r /diff_drive_controller/cmd_vel:=/cmd_vel
                -r /diff_drive_controller/odom:=/odom
                """
            ],
            condition=UnlessCondition(use_ekf),
        )

        robot_base_controller_spawner = Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "diff_drive_controller",
                "--param-file",
                robot_controller,
                "--controller-ros-args",
                """
                -r /diff_drive_controller/cmd_vel:=/cmd_vel
                -r /diff_drive_controller/odom:=/wheel/odometry
                """
            ],
            condition=IfCondition(use_ekf),
        )

    eimu_node = Node(
        package='eimu_ros',
        executable='eimu_ros',
        name='eimu_ros',
        output='screen',
        parameters=[
            eimu_config_file
        ],
        condition=IfCondition(use_ekf)
    )

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
    start_robot_base_controller_spawner_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[robot_base_controller_spawner],
        )
    )

    start_robot_base_controller_spawner_no_ekf_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[robot_base_controller_spawner_no_ekf],
        )
    )

    #--------------------------------------------------------------------------
    
    rp_lidar_c1_node = Node(
        package='sllidar_ros2',
        executable='sllidar_node',
        name='sllidar_node',
        parameters=[{'channel_type': 'serial',
                    # 'serial_port': '/dev/ttyUSB0', 
                    'serial_port': '/dev/rplidar_c1', 
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

    start_rp_lidar_c1_node_after_robot_base_controller_spawner_no_ekf = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=robot_base_controller_spawner_no_ekf,
            on_exit=[rp_lidar_c1_node],
        )
    )

    start_rp_lidar_c1_node_after_robot_base_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=robot_base_controller_spawner,
            on_exit=[rp_lidar_c1_node],
        )
    )

    #--------------------------------------------------------------------------

    camera_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(get_package_share_directory('opencv_ros_camera'),'launch','camera_image_transport.launch.py')]), 
        launch_arguments={'cam_frame_id': 'camera_optical',
                          'port_no': '0',
                          'image_width': '640',
                          'image_height': '360',
                          'publish_frequency': '30.0',
                          'jpeg_quality': '50'}.items(),
        condition=IfCondition(use_camera)
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
    ld.add_action(start_robot_base_controller_spawner_after_joint_state_broadcaster_spawner)
    ld.add_action(start_robot_base_controller_spawner_no_ekf_after_joint_state_broadcaster_spawner)
    ld.add_action(eimu_node)
    ld.add_action(ekf_node)
    ld.add_action(start_rp_lidar_c1_node_after_robot_base_controller_spawner)
    ld.add_action(start_rp_lidar_c1_node_after_robot_base_controller_spawner_no_ekf)
    ld.add_action(lidar_angle_filter_node)
    ld.add_action(camera_launch)
    ld.add_action(twist_mux_node)

    return ld      # return (i.e send) the launch description for excecution
