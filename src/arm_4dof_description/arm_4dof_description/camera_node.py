import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        
        self.publisher = self.create_publisher(Point, '/puzzle_pieces_pixels', 10)
        self.bridge = CvBridge()
        self.get_logger().info('Advanced Vision Camera Node with Green Bounding Box Active')

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'CV Bridge Error: {e}')
            return

        # تحويل الصورة إلى نطاق HSV للبحث عن اللون الأحمر للقطع
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2

        # تنظيف التشويش
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # البحث عن الحدود (Contours) للقطع الحمراء
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 150:  # تصفية المساحات الصغيرة لتفادي التشويش
                # حساب الإطار المحيط (Bounding Box) لإظهار الإطار الأخضر
                x, y, w, h = cv2.boundingRect(cnt)
                
                # حساب المركز (Center)
                cx = x + w // 2
                cy = y + h // 2

                # نشر الإحداثيات للكونترولر
                point_msg = Point()
                point_msg.x = float(cx)
                point_msg.y = float(cy)
                point_msg.z = 0.0
                self.publisher.publish(point_msg)

                # 1. رسم الإطار الأخضر حول قطعة البازل
                cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # 2. رسم نقطة المركز باللون الأزرق
                cv2.circle(cv_image, (cx, cy), 5, (255, 0, 0), -1)
                
                # 3. كتابة إحداثيات X و Y مباشرة على الصورة بجانب الإطار
                text = f"X:{cx}, Y:{cy}"
                cv2.putText(cv_image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # عرض نافذة الكاميرا بالمعاينة البصرية الحية
        cv2.imshow('Camera View - Puzzle Detection (Green Box)', cv_image)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
