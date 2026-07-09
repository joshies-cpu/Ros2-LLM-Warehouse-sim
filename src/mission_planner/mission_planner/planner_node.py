#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .prompt_builder import PromptBuilder
from .llm_client import LLMClient


class MissionPlanner(Node):
    """
    ROS2 node for mission planning.

    Converts a natural language command from /user_prompt into structured mission JSON using an LLM.
    """

    def __init__(self):
        super().__init__("mission_planner")

        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()
        self.mission_pub = self.create_publisher(
            String,
            "/mission_request",
            10,
        )
        self.prompt_sub = self.create_subscription(
            String,
            "/user_prompt",
            self.user_prompt_callback,
            10,
        )

        self.get_logger().info("Mission Planner Ready and subscribing to /user_prompt")

    def user_prompt_callback(self, msg: String):
        user_prompt = msg.data.strip()
        if not user_prompt:
            return

        self.get_logger().info(f"Received user prompt: {user_prompt}")
        try:
            prompt = self.prompt_builder.build_prompt(user_prompt)
            self.get_logger().info("Sending prompt to LLM...")
            response = self.llm.generate(prompt)

            msg_out = String()
            msg_out.data = response
            self.mission_pub.publish(msg_out)
            self.get_logger().info("Mission published to /mission_request")
        except Exception as e:
            self.get_logger().error(f"Failed to process user prompt: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = MissionPlanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
