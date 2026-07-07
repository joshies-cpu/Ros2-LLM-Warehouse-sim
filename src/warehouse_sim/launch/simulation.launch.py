#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    # ── Directories ───────────────────────────────────────────────────────────
    warehouse_sim = get_package_share_directory("warehouse_sim")
    nav2_bringup = get_package_share_directory("nav2_bringup")
    turtlebot3_gazebo = get_package_share_directory("turtlebot3_gazebo")
    pkg_gazebo_ros = get_package_share_directory("gazebo_ros")

    # ── Launch Arguments ──────────────────────────────────────────────────────
    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="true",
        description="Use simulation clock"
    )
    declare_x_pose = DeclareLaunchArgument(
        "x_pose", default_value="0.0",
        description="X spawn position of the robot"
    )
    declare_y_pose = DeclareLaunchArgument(
        "y_pose", default_value="0.0",
        description="Y spawn position of the robot"
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    x_pose = LaunchConfiguration("x_pose")
    y_pose = LaunchConfiguration("y_pose")

    # ── Environment Configuration ─────────────────────────────────────────────
    # Ensure gzclient can find gzserver on the default master URI
    set_gazebo_master = SetEnvironmentVariable(
        name="GAZEBO_MASTER_URI",
        value="http://localhost:11345"
    )
    # Automatically define model as burger if not already set
    set_turtlebot_model = SetEnvironmentVariable(
        name="TURTLEBOT3_MODEL",
        value="burger"
    )

    # ── World File ────────────────────────────────────────────────────────────
    world = os.path.join(warehouse_sim, "worlds", "my_world.world")

    # ── Gazebo Server ─────────────────────────────────────────────────────────
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gzserver.launch.py")
        ),
        launch_arguments={"world": world}.items()
    )

    # ── Gazebo Client (delayed 5s to ensure gzserver is ready) ───────────────
    gzclient_cmd = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_gazebo_ros, "launch", "gzclient.launch.py")
                )
            )
        ]
    )

    # ── Robot State Publisher ─────────────────────────────────────────────────
    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(turtlebot3_gazebo, "launch", "robot_state_publisher.launch.py")
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items()
    )

    # ── Spawn TurtleBot3 (delayed 3s to ensure gzserver accepted the world) ──
    spawn_turtlebot_cmd = TimerAction(
        period=3.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(turtlebot3_gazebo, "launch", "spawn_turtlebot3.launch.py")
                ),
                launch_arguments={
                    "x_pose": x_pose,
                    "y_pose": y_pose,
                }.items()
            )
        ]
    )

    # ── Nav2 Bringup (delayed 7s to ensure simulator is running and active) ──
    map_yaml_file = os.path.join(warehouse_sim, "maps", "my_map.yaml")
    nav2_params_file = os.path.join(warehouse_sim, "config", "nav2_params.yaml")

    nav2_bringup_cmd = TimerAction(
        period=7.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav2_bringup, "launch", "bringup_launch.py")
                ),
                launch_arguments={
                    "map": map_yaml_file,
                    "params_file": nav2_params_file,
                    "use_sim_time": use_sim_time,
                }.items()
            )
        ]
    )

    # ── RViz (delayed 10s to ensure map_server and costmaps are initialized) ──
    rviz_config_file = os.path.join(nav2_bringup, "rviz", "nav2_default_view.rviz")

    rviz_cmd = TimerAction(
        period=10.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav2_bringup, "launch", "rviz_launch.py")
                ),
                launch_arguments={
                    "rviz_config": rviz_config_file,
                    "use_sim_time": use_sim_time,
                }.items()
            )
        ]
    )

    # ── Assemble Launch Description ───────────────────────────────────────────
    ld = LaunchDescription()

    # Environment
    ld.add_action(set_gazebo_master)
    ld.add_action(set_turtlebot_model)

    # Arguments
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_x_pose)
    ld.add_action(declare_y_pose)

    # Launch Pipeline
    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(robot_state_publisher_cmd)
    ld.add_action(spawn_turtlebot_cmd)
    ld.add_action(nav2_bringup_cmd)
    ld.add_action(rviz_cmd)

    return ld

