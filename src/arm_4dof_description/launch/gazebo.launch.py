import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('arm_4dof_description')
    moveit_pkg_share = get_package_share_directory('arm_4dof_moveit_config')
    
    urdf_path = os.path.join(pkg_share, 'urdf', 'arm_4dof.urdf')
    table_urdf_path = os.path.join(pkg_share, 'urdf', 'table.urdf')
    piece_urdf_path = os.path.join(pkg_share, 'urdf', 'puzzle_piece.urdf')
    
    robot_description = ParameterValue(Command(['cat ', urdf_path]), value_type=str)

    # 1. تشغيل بيئة Gazebo
    start_gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )

    # 2. عقدة نشر الحالة للروبوت (مع تفعيل وقت المحاكاة)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    # 3. إدخال الذراع إلى Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'arm_4dof'],
        output='screen'
    )

    # 4. إدخال الطاولة
    spawn_table = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-file', table_urdf_path, '-entity', 'puzzle_board', '-x', '0.25', '-y', '0.0', '-z', '0.0'],
        output='screen'
    )

    # 5. إدخال قطع البازل فوق الطاولة
    spawn_piece_1 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-file', piece_urdf_path, '-entity', 'red_piece_1', '-x', '0.25', '-y', '0.0', '-z', '0.05'],
        output='screen'
    )
    
    spawn_piece_2 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-file', piece_urdf_path, '-entity', 'red_piece_2', '-x', '0.22', '-y', '0.08', '-z', '0.05'],
        output='screen'
    )

    # 6. تشغيل MoveIt (move_group) للتخطيط والحركة
    move_group_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moveit_pkg_share, 'launch', 'move_group.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 7. تشغيل واجهة RViz الرسمية الخاصة بـ MoveIt
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moveit_pkg_share, 'launch', 'moveit_rviz.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    return LaunchDescription([
        start_gazebo,
        robot_state_publisher_node,
        spawn_entity,
        spawn_table,
        spawn_piece_1,
        spawn_piece_2,
        move_group_launch,
        rviz_launch
    ])
