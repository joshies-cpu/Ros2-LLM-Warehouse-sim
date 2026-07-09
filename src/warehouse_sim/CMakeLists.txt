cmake_minimum_required(VERSION 3.8)
project(warehouse_sim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Install launch files
install(
  DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

# Install world files
install(
  DIRECTORY worlds/
  DESTINATION share/${PROJECT_NAME}/worlds
)

# Install model files
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/models")
  install(
    DIRECTORY models/
    DESTINATION share/${PROJECT_NAME}/models
  )
endif()

# Install map files
install(
  DIRECTORY maps/
  DESTINATION share/${PROJECT_NAME}/maps
)

# Install config files (RViz, params, etc.)
install(
  DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
