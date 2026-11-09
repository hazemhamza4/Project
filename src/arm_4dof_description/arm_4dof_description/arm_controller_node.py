import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class CleanArmController(Node):
    def __init__(self):
        super().__init__('arm_controller_node')
        
        self.subscription = self.create_subscription(
            Point,
            '/puzzle_pieces_pixels',
            self.piece_callback,
            10)
        
        self.publisher = self.create_publisher(JointTrajectory, '/set_joint_trajectory', 10)
        
        self.target_x = 320.0
        self.target_y = 240.0
        self.piece_detected = False
        self.state = "SEARCHING"
        self.base_correction = 0.0
        
        self.timer = self.create_timer(2.0, self.control_loop)
        self.get_logger().info('Clean Arm Controller Initialized!')

    def piece_callback(self, msg):
        self.target_x = msg.x
        self.target_y = msg.y
        self.piece_detected = True

    def send_joint_positions(self, positions):
        traj_msg = JointTrajectory()
        traj_msg.header.frame_id = 'base_link'
        traj_msg.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4']
        
        point = JointTrajectoryPoint()
        point.positions = [float(p) for p in positions]
        point.time_from_start.sec = 2
        point.time_from_start.nanosec = 0
        
        traj_msg.points.append(point)
        self.publisher.publish(traj_msg)

    def control_loop(self):
        if self.state == "SEARCHING":
            if self.piece_detected:
                self.get_logger().info(f'>> Piece Locked! Moving...')
                self.state = "TRACK_AND_MOVE"
            else:
                self.get_logger().info('Searching for puzzle piece...')
                self.send_joint_positions([0.0, 0.2, -0.2, 0.0])
                
        elif self.state == "TRACK_AND_MOVE":
            error_x = self.target_x - 320.0  
            self.base_correction = -error_x * 0.002 
            self.get_logger().info(f'>> Aligning base position...')
            self.send_joint_positions([self.base_correction, 0.4, 0.3, 0.0])
            self.state = "GRASP"
            
        elif self.state == "GRASP":
            self.get_logger().info('>> Lowering and simulating grasp on piece!')
            self.send_joint_positions([self.base_correction, 0.75, 0.65, 0.0])
            self.state = "TRANSPORT"
            
        elif self.state == "TRANSPORT":
            self.get_logger().info('>> Lifting and Transporting...')
            self.send_joint_positions([1.2, 0.1, 0.1, 0.0])
            self.state = "PLACE"
            
        elif self.state == "PLACE":
            self.get_logger().info('>> Placing piece down and resetting cycle!')
            self.send_joint_positions([0.0, 0.0, 0.0, 0.0])
            self.state = "SEARCHING"
            self.piece_detected = False

def main(args=None):
    rclpy.init(args=args)
    node = CleanArmController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
