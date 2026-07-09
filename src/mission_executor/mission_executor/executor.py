import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger

from mission_validator.validator import MissionValidator
from .route_loader import RouteLoader
from .navigation_client import NavigationClient


class MissionExecutor(Node):
    """ROS2 node that executes validated robot missions."""

    def __init__(self):
        super().__init__("mission_executor")

        self.validator = MissionValidator()
        self.route_loader = RouteLoader()
        self.nav_client = NavigationClient(self)

        # Publishers & Subscribers
        self.status_pub = self.create_publisher(String, "mission_status", 10)
        self.mission_sub = self.create_subscription(
            String, "mission_request", self.mission_callback, 10
        )

        # Services
        self.cancel_srv = self.create_service(
            Trigger, "cancel_mission", self.cancel_callback
        )

        # Threading and State management
        self.is_executing = False
        self.cancel_requested = False
        self.current_mission_thread = None
        self.lock = threading.Lock()

        self.get_logger().info("Mission Executor Node Initialized and Ready")

    def publish_status(self, status_str: str) -> None:
        """Publish the current executor status to the mission_status topic."""
        msg = String()
        msg.data = status_str
        self.status_pub.publish(msg)
        self.get_logger().info(f"Status update: {status_str}")

    def mission_callback(self, msg: String) -> None:
        """Handle incoming mission requests."""
        with self.lock:
            if self.is_executing:
                self.get_logger().warn(
                    "A mission is already running. Rejecting new request."
                )
                self.publish_status(
                    "REJECTED: Another mission is already running"
                )
                return

            mission_json = msg.data
            self.get_logger().info(f"Received mission request: {mission_json}")

            try:
                # Validate the mission using the validator
                validated_mission = self.validator.validate(mission_json)
                self.get_logger().info(
                    f"Mission validation passed: {validated_mission}"
                )
            except Exception as e:
                self.get_logger().error(f"Mission validation failed: {e}")
                self.publish_status(f"FAILED: Validation error: {e}")
                return

            # Start the execution thread
            self.is_executing = True
            self.cancel_requested = False
            self.current_mission_thread = threading.Thread(
                target=self.execute_mission_thread, args=(validated_mission,)
            )
            self.current_mission_thread.start()

    def cancel_callback(
        self, request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        """Service callback to cancel the currently running mission."""
        with self.lock:
            if self.is_executing:
                self.get_logger().info("Cancellation requested by service.")
                self.cancel_requested = True
                self.nav_client.cancel_goal()
                response.success = True
                response.message = "Mission cancellation requested."
            else:
                self.get_logger().info(
                    "Cancellation requested but no mission is running."
                )
                response.success = False
                response.message = "No mission currently executing."
            return response

    def execute_mission_thread(self, mission: dict) -> None:
        """Thread worker function that coordinates the execution of a mission."""
        mission_type = mission.get("mission_type")
        parameters = mission.get("parameters", {})

        self.publish_status(f"RUNNING: Executing {mission_type} mission")

        success = False
        try:
            if mission_type == "patrol":
                success = self.execute_patrol(parameters)
            elif mission_type == "navigate":
                success = self.execute_navigate(parameters)
            elif mission_type == "return_home":
                success = self.execute_return_home()
            elif mission_type == "stop":
                success = self.execute_stop()
            else:
                self.get_logger().error(
                    f"Unsupported mission type: {mission_type}"
                )
                success = False
        except Exception as e:
            self.get_logger().error(f"Exception during mission execution: {e}")
            success = False

        # Clean up and update state
        with self.lock:
            self.is_executing = False

        if self.cancel_requested:
            self.get_logger().info("Mission execution cancelled.")
            self.publish_status("CANCELLED")
        elif success:
            self.get_logger().info("Mission completed successfully.")
            self.publish_status("SUCCESS")
        else:
            self.get_logger().error("Mission execution failed.")
            self.publish_status("FAILED")

    def execute_patrol(self, parameters: dict) -> bool:
        """Execute a patrol loop for a specified number of laps."""
        route_name = parameters.get("route")
        laps = parameters.get("laps", 1)
        speed = parameters.get("speed", 0.3)

        try:
            waypoints = self.route_loader.get_waypoints(route_name)
        except Exception as e:
            self.get_logger().error(f"Failed to load waypoints: {e}")
            return False

        self.get_logger().info(
            f"Starting patrol on route '{route_name}' for {laps} laps at target speed {speed} m/s"
        )

        for lap in range(1, laps + 1):
            if self.cancel_requested or not rclpy.ok():
                return False

            self.get_logger().info(f"Starting Lap {lap}/{laps}")
            self.publish_status(f"RUNNING: Patrol lap {lap}/{laps}")

            for idx, wp in enumerate(waypoints):
                if self.cancel_requested or not rclpy.ok():
                    return False

                x = wp.get("x")
                y = wp.get("y")
                yaw = wp.get("yaw", 0.0)
                frame_id = wp.get("frame_id", "map")

                self.get_logger().info(
                    f"Lap {lap}: Navigating to waypoint {idx+1}/{len(waypoints)}"
                )
                nav_success = self.nav_client.navigate_to(x, y, yaw, frame_id)
                if not nav_success:
                    if self.cancel_requested:
                        return False
                    self.get_logger().error(
                        f"Navigation failed at waypoint {idx+1}"
                    )
                    return False

        return True

    def execute_navigate(self, parameters: dict) -> bool:
        """Navigate to a specified destination waypoint."""
        destination = parameters.get("destination")
        speed = parameters.get("speed", 0.3)

        try:
            waypoints = self.route_loader.get_waypoints(destination)
        except Exception as e:
            self.get_logger().error(f"Failed to load destination: {e}")
            return False

        self.get_logger().info(
            f"Starting navigation to destination '{destination}' at target speed {speed} m/s"
        )

        for idx, wp in enumerate(waypoints):
            if self.cancel_requested or not rclpy.ok():
                return False

            x = wp.get("x")
            y = wp.get("y")
            yaw = wp.get("yaw", 0.0)
            frame_id = wp.get("frame_id", "map")

            self.get_logger().info(
                f"Navigating to waypoint {idx+1}/{len(waypoints)}"
            )
            nav_success = self.nav_client.navigate_to(x, y, yaw, frame_id)
            if not nav_success:
                if self.cancel_requested:
                    return False
                self.get_logger().error(
                    f"Navigation failed at waypoint {idx+1}"
                )
                return False

        return True

    def execute_return_home(self) -> bool:
        """Navigate back to the origin/home position."""
        self.get_logger().info("Returning to home (0.0, 0.0)")
        return self.nav_client.navigate_to(0.0, 0.0, 0.0, "map")

    def execute_stop(self) -> bool:
        """Immediately stop any current navigation."""
        self.get_logger().info("Executing stop action")
        self.cancel_requested = True
        self.nav_client.cancel_goal()
        return True


def main(args=None):
    rclpy.init(args=args)
    node = MissionExecutor()

    # Use a MultiThreadedExecutor to allow action client callbacks
    # to run while the subscriber callbacks are executing.
    from rclpy.executors import MultiThreadedExecutor

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
