from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim'
        ),
        Node(
            package='turtlesim_assignment',
            executable='go_to_pose_server',
            name='go_to_pose_server',
            parameters=[
                {'max_linear_speed': 2.0},
                {'max_angular_speed': 2.0}
            ]
        ),
        Node(
            package='turtlesim_assignment',
            executable='speed_parameter_service',
            name='speed_parameter_service'
        ),
        Node(
            package='turtlesim_assignment',
            executable='reset_service',
            name='reset_service'
        ),
        Node(
            package='turtlesim_assignment',
            executable='square_server',
            name='square_server'
        )
    ])
