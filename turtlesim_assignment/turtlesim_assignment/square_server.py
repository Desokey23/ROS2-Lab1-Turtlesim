import math

import rclpy
from rclpy.action import ActionClient, ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_srvs.srv import Empty

from turtlesim_interfaces.action import GoToPose, Square
from turtlesim_interfaces.msg import TargetPoint


class SquareServer(Node):
    def __init__(self):
        super().__init__('square_server')

        # group functions
        self.cb_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            Square,
            'draw_square',
            self.execute_callback,
            callback_group=self.cb_group)

        self.goto_client = ActionClient(
            self, GoToPose, 'go_to_pose', callback_group=self.cb_group)
        self.reset_client = self.create_client(
            Empty, 'reset_turtle_custom', callback_group=self.cb_group)

        self.get_logger().info('Square Action Server Started.')

    async def execute_callback(self, goal_handle):
        self.get_logger().info('Executing square goal...')
        side = goal_handle.request.side_length
        feedback_msg = Square.Feedback()

        # Reset
        while not self.reset_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Reset service not available, waiting...')

        reset_req = Empty.Request()
        await self.reset_client.call_async(reset_req)
        self.get_logger().info('Reset complete.')

        # determine angles
        x_start = 5.544445
        y_start = 5.544445

        if x_start + side > 11 or y_start + side > 11 or x_start - side < 0 or y_start - side < 0:
            self.get_logger().error('Square too large for window.')
            goal_handle.abort()
            result = Square.Result()
            result.success = False
            return result

        corners = [
            (x_start + side, y_start, math.pi/2),
            (x_start + side, y_start + side, math.pi),
            (x_start, y_start + side, -math.pi/2),
            (x_start, y_start, 0.0)
        ]

        # send the 4 steps periodclly
        for i, (cx, cy, cyaw) in enumerate(corners):
            if not self.goto_client.wait_for_server(timeout_sec=1.0):
                self.get_logger().info('GoToPose action server not available, waiting...')

            goal_msg = GoToPose.Goal()
            target = TargetPoint()
            target.x = cx
            target.y = cy
            target.yaw = cyaw
            goal_msg.target = target

            self.get_logger().info(f'Sending goal {i+1}: ({cx}, {cy}, {cyaw})')

            client_goal_handle = await self.goto_client.send_goal_async(goal_msg)

            if not client_goal_handle.accepted:
                self.get_logger().error('Goal rejected by GoToPose server')
                continue

            await client_goal_handle.get_result_async()

            feedback_msg.current_side = i + 1
            goal_handle.publish_feedback(feedback_msg)

        goal_handle.succeed()
        result = Square.Result()
        result.success = True
        return result


def main(args=None):
    rclpy.init(args=args)
    square_server = SquareServer()

    # avoid freeze
    executor = MultiThreadedExecutor()
    rclpy.spin(square_server, executor=executor)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
