from setuptools import setup

package_name = 'arm_4dof_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hazem',
    maintainer_email='hazem@todo.todo',
    description='Controller for 4-DOF arm puzzle pick and place',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'puzzle_pick_and_place = arm_4dof_controller.puzzle_pick_and_place:main',
        ],
    },
)
