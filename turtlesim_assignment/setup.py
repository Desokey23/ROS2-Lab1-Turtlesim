import os
from glob import glob

from setuptools import setup

package_name = 'turtlesim_assignment'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include all launch files
        (os.path.join('share', package_name, 'launch'), glob(
            os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='Turtlesim Lab 1 Assignment Servers',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'go_to_pose_server = turtlesim_assignment.go_to_pose_server:main',
            'speed_parameter_service = turtlesim_assignment.speed_parameter_service:main',
            'reset_service = turtlesim_assignment.reset_service:main',
            'square_server = turtlesim_assignment.square_server:main',
        ],
    },
)
