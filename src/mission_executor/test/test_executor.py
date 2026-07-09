import pytest
from unittest.mock import patch
import rclpy
from std_msgs.msg import String
from std_srvs.srv import Trigger
from mission_executor.route_loader import RouteLoader
from mission_executor.executor import MissionExecutor


# Mock Node methods to prevent actual ROS 2 network initialization during unit testing
@patch("rclpy.node.Node.create_publisher")
@patch("rclpy.node.Node.create_subscription")
@patch("rclpy.node.Node.create_service")
@patch("mission_executor.executor.NavigationClient")
def test_executor_init(
    mock_nav_client,
    mock_create_service,
    mock_create_subscription,
    mock_create_publisher,
):
    if not rclpy.ok():
        rclpy.init()
    try:
        with patch("rclpy.node.Node.get_logger"):
            executor = MissionExecutor()
            assert executor is not None
            mock_create_publisher.assert_any_call(
                String, "mission_status", 10
            )
            mock_create_subscription.assert_any_call(
                String, "mission_request", executor.mission_callback, 10
            )
            mock_create_service.assert_any_call(
                Trigger, "cancel_mission", executor.cancel_callback
            )
            mock_nav_client.assert_called_once_with(executor)
    finally:
        if rclpy.ok():
            rclpy.shutdown()


def test_route_loader():
    loader = RouteLoader()
    assert "inspection_loop" in loader.routes
    waypoints = loader.get_waypoints("inspection_loop")
    assert len(waypoints) == 4
    assert waypoints[0]["x"] == 0.0

    with pytest.raises(KeyError):
        loader.get_waypoints("nonexistent_route")


def test_route_loader_invalid_file():
    with pytest.raises(FileNotFoundError):
        RouteLoader("/path/to/nowhere.json")
