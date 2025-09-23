import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node





def generate_launch_description():
    # delare any path variable
    rviz_pkg_path = get_package_share_directory('mobo_bot_rviz')
    rviz_config_file = os.path.join(rviz_pkg_path,'config','mapping.rviz')

    # create needed nodes or launch files
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen'
    )

     # Create the launch description and populate
    ld = LaunchDescription()
    
    # Add the nodes to the launch description
    ld.add_action(rviz_node)

    
    return ld      # return (i.e send) the launch description for excecution

