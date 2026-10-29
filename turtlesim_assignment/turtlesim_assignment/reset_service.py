import time

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_srvs.srv import Empty
from turtlesim.srv import SetPen, TeleportAbsolute


class ResetService(Node):
    def __init__(self):
        super().__init__('reset_service')
        self.cb_group = ReentrantCallbackGroup()

        self.srv = self.create_service(
            Empty, 'reset_turtle_custom', self.reset_callback, callback_group=self.cb_group)

        self.clear_client = self.create_client(
            Empty, 'clear', callback_group=self.cb_group)
        self.teleport_client = self.create_client(
            TeleportAbsolute, 'turtle1/teleport_absolute', callback_group=self.cb_group)
        self.pen_client = self.create_client(
            SetPen, 'turtle1/set_pen', callback_group=self.cb_group)

        self.get_logger().info('Reset Service Started.')

    def reset_callback(self, request, response):
        self.get_logger().info('Resetting turtle...')

        pen_req = SetPen.Request()
        pen_req.off = 1
        self.call_service_sync(self.pen_client, pen_req)

        teleport_req = TeleportAbsolute.Request()
        teleport_req.x = 5.544445
        teleport_req.y = 5.544445
        teleport_req.theta = 0.0
        self.call_service_sync(self.teleport_client, teleport_req)

        clear_req = Empty.Request()
        self.call_service_sync(self.clear_client, clear_req)

        pen_req.off = 0
        self.call_service_sync(self.pen_client, pen_req)

        return response

    def call_service_sync(self, client, request):
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(f'waiting for service...')  # noqa: F541

        future = client.call_async(request)
        # wait before skleep
        while not future.done():
            time.sleep(0.05)
        return future.result()


def main(args=None):
    rclpy.init(args=args)
    reset_service = ResetService()
    executor = MultiThreadedExecutor()
    rclpy.spin(reset_service, executor=executor)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
