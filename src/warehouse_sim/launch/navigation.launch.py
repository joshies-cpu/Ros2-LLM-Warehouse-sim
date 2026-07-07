import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    warehouse_sim = get_package_share_directory("warehouse_sim")

    nav2_bringup = get_package_share_directory("nav2_bringup")

    map_file = os.path.join(
        warehouse_sim,
        "maps",
        "my_map.yaml"
    )

    params_file = os.path.join(
        warehouse_sim,
        "config",
        "nav2_params.yaml"
    )

    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                nav2_bringup,
                "launch",
                "bringup_launch.py"
            )
        ),
        launch_arguments={
            "map": map_file,
            "params_file": params_file,
            "use_sim_time": "True"
        }.items()
    )

    return LaunchDescription([
        bringup
    ])