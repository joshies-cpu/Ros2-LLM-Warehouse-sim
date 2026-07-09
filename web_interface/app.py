#!/usr/bin/env python3

import os
import sys
import time
import json
import threading
import requests
from flask import Flask, render_template, jsonify, request, Response

# Check if rclpy is available
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
except ImportError:
    print("Error: rclpy not found. Please source your ROS2 workspace before running.")
    sys.exit(1)

app = Flask(__name__)

# Thread-safe container for system states
class ROS2State:
    def __init__(self):
        self.latest_status = "IDLE"
        self.latest_json = ""
        self.planner_connected = False
        self.executor_connected = False
        self.ollama_connected = False
        self.mission_active = False
        self.lock = threading.Lock()

state = ROS2State()

class WebInterfaceNode(Node):
    def __init__(self):
        super().__init__("web_interface_node")
        
        # Subscribers
        self.status_sub = self.create_subscription(
            String,
            "mission_status",
            self.status_callback,
            10
        )
        self.request_sub = self.create_subscription(
            String,
            "mission_request",
            self.request_callback,
            10
        )
        
        # Publisher
        self.prompt_pub = self.create_publisher(
            String,
            "user_prompt",
            10
        )
        
        self.get_logger().info("Web Interface ROS2 Node Started")

    def status_callback(self, msg):
        with state.lock:
            state.latest_status = msg.data
            # Set active state based on status prefix
            if msg.data.startswith("RUNNING"):
                state.mission_active = True
            elif msg.data in ["SUCCESS", "FAILED", "CANCELLED"] or msg.data.startswith("FAILED") or msg.data.startswith("REJECTED"):
                state.mission_active = False

    def request_callback(self, msg):
        with state.lock:
            state.latest_json = msg.data

    def publish_prompt(self, prompt_text):
        msg = String()
        msg.data = prompt_text
        self.prompt_pub.publish(msg)
        self.get_logger().info(f"Published prompt to /user_prompt: {prompt_text}")


def ros2_thread_function():
    """Background thread to spin the ROS2 node and manage status monitoring."""
    rclpy.init(args=None)
    node = WebInterfaceNode()
    
    # Store reference on app so we can use it to publish
    app.ros_node = node
    
    # Check node status periodically
    def check_system():
        while rclpy.ok():
            try:
                # 1. Check active ROS2 nodes
                node_names = node.get_node_names()
                
                # 2. Check Ollama server status
                ollama_ok = False
                try:
                    r = requests.get("http://localhost:11434/api/tags", timeout=0.5)
                    if r.status_code == 200:
                        ollama_ok = True
                except Exception:
                    pass
                
                with state.lock:
                    state.planner_connected = "mission_planner" in node_names
                    state.executor_connected = "mission_executor" in node_names
                    state.ollama_connected = ollama_ok
            except Exception as e:
                node.get_logger().error(f"Error in status check loop: {e}")
            time.sleep(1.0)
            
    status_thread = threading.Thread(target=check_system, daemon=True)
    status_thread.start()
    
    try:
        rclpy.spin(node)
    except Exception as e:
        node.get_logger().error(f"ROS2 Spin failed: {e}")
    finally:
        node.destroy_node()
        rclpy.shutdown()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/send_prompt", methods=["POST"])
def send_prompt():
    data = request.json
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"success": False, "error": "Prompt cannot be empty"}), 400
        
    if not hasattr(app, "ros_node"):
        return jsonify({"success": False, "error": "ROS2 node not initialized"}), 500
        
    # Clear previous JSON when a new prompt is sent
    with state.lock:
        state.latest_json = ""
        
    app.ros_node.publish_prompt(prompt)
    return jsonify({"success": True})


@app.route("/status_stream")
def status_stream():
    def event_stream():
        while True:
            with state.lock:
                current_status = state.latest_status
                current_json = state.latest_json
                current_planner = state.planner_connected
                current_executor = state.executor_connected
                current_ollama = state.ollama_connected
                current_active = state.mission_active
                
            data = {
                "status": current_status,
                "json": current_json,
                "planner_connected": current_planner,
                "executor_connected": current_executor,
                "ollama_connected": current_ollama,
                "mission_active": current_active
            }
            
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.5)
            
    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    # Start ROS2 in a background daemon thread
    ros_thread = threading.Thread(target=ros2_thread_function, daemon=True)
    ros_thread.start()
    
    # Clear sys.argv to prevent Flask's CLI parser from processing ROS2 launch arguments
    sys.argv = [sys.argv[0]]
    
    # Run Flask application
    app.run(host="0.0.0.0", port=5000, debug=False)
