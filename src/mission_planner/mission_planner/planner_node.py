#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from .prompt_builder import PromptBuilder
from .llm_client import LLMClient


class MissionPlanner(Node):
    """
    ROS2 node responsible for converting a natural language
    command into structured mission JSON using an LLM.
    """

    def __init__(self):
        super().__init__("mission_planner")

        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()

        self.get_logger().info("Mission Planner Ready")

    def run(self):

        while rclpy.ok():

            try:

                user_prompt = input("\nMission > ").strip()

                if not user_prompt:
                    continue

                prompt = self.prompt_builder.build_prompt(user_prompt)

                self.get_logger().info("Sending prompt to LLM...")

                response = self.llm.generate(prompt)

                print("\n========== Mission JSON ==========\n")
                print(response)
                print("\n==================================\n")

            except KeyboardInterrupt:
                break

            except Exception as e:
                self.get_logger().error(str(e))


def main():

    rclpy.init()

    node = MissionPlanner()

    node.run()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()