#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    warehouse_sim_dir = get_package_share_directory('warehouse_sim')
    
    # Resolve the workspace root directory dynamically for portability
    workspace_root = os.path.abspath(os.path.join(warehouse_sim_dir, '..', '..', '..', '..'))
    
    # ── Simulation Launch ─────────────────────────────────────────────────────
    simulation_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(warehouse_sim_dir, 'launch', 'simulation.launch.py')
        )
    )
    
    # ── Mission Executor Node ─────────────────────────────────────────────────
    executor_node = Node(
        package='mission_executor',
        executable='executor',
        name='mission_executor',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )
    
    # ── Mission Planner Node ──────────────────────────────────────────────────
    planner_node = Node(
        package='mission_planner',
        executable='planner_node',
        name='mission_planner',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )
    
    # ── Flask Web Interface ───────────────────────────────────────────────────
    flask_node = ExecuteProcess(
        cmd=['python3', '-u', 'web_interface/app.py'],
        cwd=workspace_root,
        output='screen'
    )
    
    return LaunchDescription([
        simulation_cmd,
        executor_node,
        planner_node,
        flask_node
    ])
