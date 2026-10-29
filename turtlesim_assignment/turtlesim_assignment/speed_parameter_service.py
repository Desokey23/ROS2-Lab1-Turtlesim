import time

import rclpy
from rcl_interfaces.msg import Parameter as ParamMsg
from rcl_interfaces.msg import ParameterType, ParameterValue
from rcl_interfaces.srv import SetParameters
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from turtlesim_interfaces.srv import SetSpeeds


class SpeedParameterService(Node):
    def __init__(self):
        super().__init__('speed_parameter_service')
        self.cb_group = ReentrantCallbackGroup()
        self.srv = self.create_service(
            SetSpeeds, 'set_speeds', self.set_speeds_callback, callback_group=self.cb_group)

        self.param_client = self.create_client(
            SetParameters, '/go_to_pose_server/set_parameters', callback_group=self.cb_group)
        self.get_logger().info('Speed Parameter Service Started.')

    def set_speeds_callback(self, request, response):
        if request.max_linear_speed <= 0 or request.max_angular_speed <= 0:
            self.get_logger().warn('Invalid speeds.')
            response.success = False
            return response

        while not self.param_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting for param service...')

        req = SetParameters.Request()
        val_linear = ParameterValue(
            type=ParameterType.PARAMETER_DOUBLE, double_value=request.max_linear_speed)
        val_angular = ParameterValue(
            type=ParameterType.PARAMETER_DOUBLE, double_value=request.max_angular_speed)

        req.parameters = [
            ParamMsg(name='max_linear_speed', value=val_linear),
            ParamMsg(name='max_angular_speed', value=val_angular)
        ]

        future = self.param_client.call_async(req)
        while not future.done():
            time.sleep(0.05)

        self.get_logger().info(
            f'Speeds updated: Linear={request.max_linear_speed}')
        response.success = True
        return response


def main(args=None):
    rclpy.init(args=args)
    speed_parameter_service = SpeedParameterService()
    executor = MultiThreadedExecutor()
    rclpy.spin(speed_parameter_service, executor=executor)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
