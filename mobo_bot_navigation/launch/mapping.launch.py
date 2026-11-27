import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, EmitEvent, LogInfo,
                            RegisterEventHandler)
from launch.conditions import IfCondition, UnlessCondition
from launch.events import matches_action
from launch.substitutions import (AndSubstitution, LaunchConfiguration,
                                  NotSubstitution)
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition
from launch_ros.descriptions import ParameterFile
from nav2_common.launch import RewrittenYaml, ReplaceString

from launch_ros.actions import Node


def generate_launch_description():

    robot_nav_pkg_path = get_package_share_directory('mobo_bot_navigation')


    autostart = LaunchConfiguration('autostart')
    use_lifecycle_manager = LaunchConfiguration("use_lifecycle_manager")
    use_sim_time = LaunchConfiguration('use_sim_time')
    slamtoolbox_params_file = LaunchConfiguration('slamtoolbox_params_file')
    easynav_costmap_params_file = LaunchConfiguration('easynav_costmap_params_file')
    easynav_simple_params_file = LaunchConfiguration('easynav_simple_params_file')
    use_costmap = LaunchConfiguration('use_costmap')


    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart', default_value='true',
        description='Automatically startup the slamtoolbox. '
                    'Ignored when use_lifecycle_manager is true.')
    
    declare_use_lifecycle_manager = DeclareLaunchArgument(
        'use_lifecycle_manager', default_value='false',
        description='Enable bond connection during node activation')
    
    declare_use_sim_time_argument = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation/Gazebo clock')
    
    declare_slamtoolbox_params_file_cmd = DeclareLaunchArgument(
        'slamtoolbox_params_file',
        default_value=os.path.join(robot_nav_pkg_path,
                                   'config', 'slam_toolbox_mapping_params.yaml'),
        description='Full path to the ROS2 parameters file to use for the slam_toolbox node')

    declare_easynav_simple_params_file_cmd = DeclareLaunchArgument(
        'easynav_simple_params_file',
        default_value=os.path.join(
            robot_nav_pkg_path, 'config', 'easynav_simple_mapping_params.yaml'),
        description='Full path to the ROS2 parameters file for easynav simple')

    declare_easynav_costmap_params_file_cmd = DeclareLaunchArgument(
        'easynav_costmap_params_file',
        default_value=os.path.join(
            robot_nav_pkg_path, 'config', 'easynav_costmap_mapping_params.yaml'),
        description='Full path to the ROS2 parameters file for easynav costmap')

    declare_use_costmap_cmd = DeclareLaunchArgument(
        'use_costmap',
        default_value="True",
        description='whether to use easynav simple or costmap')
    

     # Perform substitution `$find-pkg-share`
    slam_params_file_w_subst = ParameterFile(
        slamtoolbox_params_file,
        allow_substs=True,
    )
    
    start_async_slam_toolbox_node = LifecycleNode(
        parameters=[
          slam_params_file_w_subst,
          {
            'use_lifecycle_manager': use_lifecycle_manager,
            'use_sim_time': use_sim_time
          }
        ],
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        namespace=''
    )

    configure_event = EmitEvent(
        event=ChangeState(
          lifecycle_node_matcher=matches_action(start_async_slam_toolbox_node),
          transition_id=Transition.TRANSITION_CONFIGURE
        ),
        condition=IfCondition(AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager)))
    )

    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=start_async_slam_toolbox_node,
            start_state="configuring",
            goal_state="inactive",
            entities=[
                LogInfo(msg="[LifecycleLaunch] Slamtoolbox node is activating."),
                EmitEvent(event=ChangeState(
                    lifecycle_node_matcher=matches_action(start_async_slam_toolbox_node),
                    transition_id=Transition.TRANSITION_ACTIVATE
                ))
            ]
        ),
        condition=IfCondition(AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager)))
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
            ('/maps_manager_node/simple/incoming_map', '/map'),
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
        # remappings=[
        #     ('/maps_manager_node/costmap/incoming_map', '/map'),
        # ],
        condition=IfCondition(use_costmap)
    )
    

    ld = LaunchDescription()

    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_use_lifecycle_manager)
    ld.add_action(declare_use_sim_time_argument)
    ld.add_action(declare_slamtoolbox_params_file_cmd)
    ld.add_action(declare_easynav_costmap_params_file_cmd)
    ld.add_action(declare_easynav_simple_params_file_cmd)
    ld.add_action(declare_use_costmap_cmd)

    ld.add_action(start_async_slam_toolbox_node)
    ld.add_action(configure_event)
    ld.add_action(activate_event)
    ld.add_action(easynav_system_simple)
    ld.add_action(easynav_system_costmap)

    return ld