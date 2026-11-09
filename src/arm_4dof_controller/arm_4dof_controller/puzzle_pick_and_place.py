#!/usr/init/env python3

import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
# استيراد خدمة ربط الأجسام في Gazebo
from gazebo_ros_link_attacher.srv import Attach, Detach


class PuzzlePickAndPlace(Node):
    def __init__(self):
        super().__init__('puzzle_pick_and_place')
        self.get_logger().info("=== بدء عقدة التقاط البازل بالشفط الهوائي ===")

        # 1. تهيئة عميل خدمة الشفط (Link Attacher)
        self.attach_client = self.create_client(Attach, '/link_attacher_node/attach')
        self.detach_client = self.create_client(Detach, '/link_attacher_node/detach')
        
        while not self.attach_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('خدمة الشفط غير متوفرة، جاري الانتظار...')

    def call_attach_service(self, model1, link1, model2, link2):
        """إرسال طلب تفعيل الشفط (ربط قطعة البازل برأس الذراع)"""
        request = Attach.Request()
        request.model_1 = model1
        request.link_1 = link1
        request.model_2 = model2
        request.link_2 = link2

        future = self.attach_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info("✅ تم تفعيل الشفط وإمساك القطعة بنجاح!")
        else:
            self.get_logger().error("❌ فشل استدعاء خدمة الشفط!")

    def call_detach_service(self, model1, link1, model2, link2):
        """إرسال طلب إيقاف الشفط (تحرير قطعة البازل)"""
        request = Detach.Request()
        request.model_1 = model1
        request.link_1 = link1
        request.model_2 = model2
        request.link_2 = link2

        future = self.detach_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info("✅ تم إيقاف الشفط وتحرير القطعة!")
        else:
            self.get_logger().error("❌ فشل استدعاء خدمة تحرير القطعة!")


def main(args=None):
    rclpy.init(args=args)
    node = PuzzlePickAndPlace()

    node.get_logger().info("الخطوة 1: تحريك الذراع فوق قطعة البازل...")
    
    node.get_logger().info("الخطوة 2: تشغيل الشفط والتقاط القطعة...")
    node.call_attach_service(
        model1="arm_4dof_puzzle", link1="end_effector_link",
        model2="puzzle_piece", link2="link"
    )

    node.get_logger().info("الخطوة 3: التحرك نحو مكان وضع البازل...")

    node.get_logger().info("الخطوة 4: إيقاف الشفط ووضع القطعة...")
    node.call_detach_service(
        model1="arm_4dof_puzzle", link1="end_effector_link",
        model2="puzzle_piece", link2="link"
    )

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
