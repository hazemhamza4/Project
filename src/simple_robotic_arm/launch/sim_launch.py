import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    pkg = get_package_share_directory("simple_robotic_arm")  

    urdf_path = os.path.join(pkg, "urdf", "simple_robotic_arm.urdf")  

    with open(urdf_path, 'r') as f:  
        robot_description = f.read()  

    controllers = os.path.join(pkg, "config", "controllers.yaml")  

    # STATE PUBLISHER  
    rsp = Node(  
        package="robot_state_publisher",  
        executable="robot_state_publisher",  
        parameters=[{"robot_description": robot_description}],  
        output="screen"  
    )  

    node_joint_state_publisher_gui = Node(  
        package="joint_state_publisher_gui",  
        executable="joint_state_publisher_gui",  
        name="joint_state_publisher_gui",  
    )  

    # GAZEBO: تشغيل المحاكي مع تحميل مكتبة ROS Factory
    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )

    # SPAWN ROBOT: إضافة الروبوت من ملف الـ URDF مباشرة
    spawn = Node(  
        package="gazebo_ros",  
        executable="spawn_entity.py",  
        arguments=["-file", urdf_path, "-entity", "robot_arm", "-z", "0.2"],  
        output="screen",  
        emulate_tty=True  
    )  

    # تأخير عملية الـ Spawn لمنح Gazebo وقتاً للتهيئة
    delayed_spawn = TimerAction(
        period=8.0,
        actions=[spawn]
    )

    # RVIZ  
    rviz = Node(  
        package="rviz2",  
        executable="rviz2",  
        arguments=["-d", os.path.join(pkg, "rviz", "robot.rviz")],  
        output="screen"  
    )  

    # CONTROLLERS  
    jsb = Node(  
        package="controller_manager",  
        executable="spawner",  
        arguments=["joint_state_broadcaster"]  
    )  

    jtc = Node(  
        package="controller_manager",  
        executable="spawner",  
        arguments=["joint_trajectory_controller", "--param-file", controllers]  
    )  

    return LaunchDescription([  
        gazebo,  
        rsp,  
        delayed_spawn, 
        rviz,  
        node_joint_state_publisher_gui,  
    ])
