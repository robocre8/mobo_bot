import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue
from launch.conditions import IfCondition, UnlessCondition

import xacro


def generate_launch_description():
    
    # Process the URDF file
    description_pkg_path = get_package_share_directory('mobo_bot_description')
    xacro_file = os.path.join(description_pkg_path,'urdf','robot_urdf.xacro')

    # Check if we're told to use sim time
    run_gz_sim = LaunchConfiguration('run_gz_sim')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_joint_state_pub = LaunchConfiguration('use_joint_state_pub')
    
    # declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='False',
        description='Use sim time if true'
    )

    declare_run_gz_sim_cmd = DeclareLaunchArgument(
        'run_gz_sim',
        default_value='False',
        description='Use simulation if true'
    )

    declare_use_joint_state_pub_cmd = DeclareLaunchArgument(
        'use_joint_state_pub',
        default_value='False',
        description='Use sim time if true'
    )

    #--------------------------------------------------------------------------

    valid_base_types = ['2WD', '4WD', 'MEC', '22WD']
    base_type = os.environ.get("MOBOBOT_BASE_TYPE")

    if base_type is None:
        print("[ERROR]: MOBOBOT_BASE_TYPE environment variable not found")
        exit(1)
    elif base_type not in valid_base_types:
        print(f"[ERROR]: Invalid MOBOBOT_BASE_TYPE='{base_type}'. Expected one of {valid_base_types}")
        exit(1)
        
    #----------------------------------------------------------------------------

    # Create a robot_state_publisher node
    # doc = xacro.parse(open(xacro_file))
    # xacro.process_doc(doc)
    # robot_description_xml = doc.toxml()

    robot_description_config= Command(['xacro ', xacro_file,
                                       ' run_gz_sim:=', run_gz_sim,
                                       ' base_type:=', base_type ])
    robot_description_xml = ParameterValue(robot_description_config, value_type=str)

    params = {'robot_description': robot_description_xml, 'use_sim_time': use_sim_time}
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params],
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen',
        condition=IfCondition(use_joint_state_pub)
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # add the necessary declared launch arguments to the launch description
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_run_gz_sim_cmd)
    ld.add_action(declare_use_joint_state_pub_cmd)

    # Add the nodes to the launch description
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_node)
    
    return ld      # return (i.e send) the launch description for excecution
    