import math
import time
import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus


class NavigationClient:
    """Action client wrapper for Nav2's NavigateToPose action."""

    def __init__(self, node):
        self.node = node
        self.callback_group = ReentrantCallbackGroup()
        self.client = ActionClient(
            self.node,
            NavigateToPose,
            "navigate_to_pose",
            callback_group=self.callback_group,
        )
        self.goal_handle = None

    def wait_for_server(self, timeout_sec: float = 10.0) -> bool:
        """Wait for the NavigateToPose action server to become available."""
        self.node.get_logger().info(
            "Waiting for 'navigate_to_pose' action server..."
        )
        return self.client.wait_for_server(timeout_sec=timeout_sec)

    def send_pose_goal(self, x: float, y: float, yaw: float, frame_id: str = "map"):
        """Send a navigation goal asynchronously."""
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = frame_id
        goal_msg.pose.header.stamp = self.node.get_clock().now().to_msg()

        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        # Convert yaw to quaternion: q = [0, 0, sin(yaw/2), cos(yaw/2)]
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.node.get_logger().info(
            f"Sending navigation goal: (x: {x:.2f}, y: {y:.2f}, "
            f"yaw: {yaw:.2f}) in frame '{frame_id}'"
        )
        return self.client.send_goal_async(goal_msg)

    def cancel_goal(self):
        """Cancel the current goal if it is active."""
        if self.goal_handle is not None:
            self.node.get_logger().info("Cancelling current navigation goal...")
            return self.goal_handle.cancel_goal_async()
        return None

    def navigate_to(
        self, x: float, y: float, yaw: float, frame_id: str = "map"
    ) -> bool:
        """
        Navigate to a pose and block until completion.

        Return True if successful, False if failed/cancelled.
        """
        if not self.wait_for_server(timeout_sec=2.0):
            self.node.get_logger().error(
                "Action server 'navigate_to_pose' not available!"
            )
            return False

        send_goal_future = self.send_pose_goal(x, y, yaw, frame_id)

        # Wait for the server to accept/reject the goal
        while rclpy.ok() and not send_goal_future.done():
            time.sleep(0.05)

        try:
            self.goal_handle = send_goal_future.result()
        except Exception as e:
            self.node.get_logger().error(f"Failed to send goal: {e}")
            return False

        if not self.goal_handle.accepted:
            self.node.get_logger().error("Goal rejected by action server!")
            return False

        self.node.get_logger().info("Goal accepted by action server.")

        # Wait for the result
        result_future = self.goal_handle.get_result_async()
        while rclpy.ok() and not result_future.done():
            time.sleep(0.05)

        try:
            result = result_future.result()
            if result.status == GoalStatus.STATUS_SUCCEEDED:
                self.node.get_logger().info("Goal reached successfully!")
                return True
            else:
                self.node.get_logger().warn(
                    f"Goal failed with status: {result.status}"
                )
                return False
        except Exception as e:
            self.node.get_logger().error(f"Error getting goal result: {e}")
            return False
        finally:
            self.goal_handle = None
