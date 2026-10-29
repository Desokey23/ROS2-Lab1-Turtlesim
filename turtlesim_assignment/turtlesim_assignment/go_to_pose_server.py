import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from turtlesim.msg import Pose

from turtlesim_interfaces.action import GoToPose


class GoToPoseServer(Node):
    def __init__(self):
        super().__init__('go_to_pose_server')

        self.cb_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            GoToPose,
            'go_to_pose',
            self.execute_callback,
            callback_group=self.cb_group)

        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)

        self.subscriber = self.create_subscription(
            Pose, 'turtle1/pose', self.pose_callback, 10, callback_group=self.cb_group)

        self.current_pose = Pose()

        self.declare_parameter('max_linear_speed', 2.0)
        self.declare_parameter('max_angular_speed', 2.0)

        self.get_logger().info('GoToPose Action Server Started.')

    def pose_callback(self, msg):
        self.current_pose = msg

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing precision goal...')
        target = goal_handle.request.target
        if target.x <= 0.0 or target.x >= 11.0 or target.y <= 0.0 or target.y >= 11.0:
            self.get_logger().error(
                f'Target ({target.x}, {target.y}) is out of bounds! Must be between 0 and 11.')
            goal_handle.abort()
            result = GoToPose.Result()
            result.success = False
            return result
        feedback_msg = GoToPose.Feedback()

        msg = Twist()

        # go to  first point
        while True:
            max_linear = self.get_parameter(
                'max_linear_speed').get_parameter_value().double_value
            max_angular = self.get_parameter(
                'max_angular_speed').get_parameter_value().double_value

            distance = math.sqrt(
                (target.x - self.current_pose.x)**2 + (target.y - self.current_pose.y)**2)
            angle_to_target = math.atan2(
                target.y - self.current_pose.y, target.x - self.current_pose.x)
            angle_error = self.normalize_angle(
                angle_to_target - self.current_pose.theta)

            # dercrease error value
            if distance < 0.01:
                break

            k_linear = 2.0
            k_angular = 6.0

            # look at the right angle first
            if abs(angle_error) > 0.05:
                linear_vel = 0.0
            else:
                linear_vel = k_linear * distance

            angular_vel = k_angular * angle_error

            msg.linear.x = min(linear_vel, max_linear)
            msg.angular.z = max(min(angular_vel, max_angular), -max_angular)

            self.publisher_.publish(msg)

            feedback_msg.distance_remaining = distance
            goal_handle.publish_feedback(feedback_msg)

            time.sleep(0.02)

        # final angle move
        while True:
            max_angular = self.get_parameter(
                'max_angular_speed').get_parameter_value().double_value
            angle_error = self.normalize_angle(
                target.yaw - self.current_pose.theta)

            if abs(angle_error) < 0.01:
                break

            msg.linear.x = 0.0
            msg.angular.z = max(
                min(3.0 * angle_error, max_angular), -max_angular)
            self.publisher_.publish(msg)

            time.sleep(0.02)

        # stop
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)

        goal_handle.succeed()
        result = GoToPose.Result()
        result.success = True
        return result


def main(args=None):
    rclpy.init(args=args)
    go_to_pose_server = GoToPoseServer()
    executor = MultiThreadedExecutor()
    rclpy.spin(go_to_pose_server, executor=executor)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
