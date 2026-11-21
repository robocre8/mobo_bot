cmake_minimum_required(VERSION 3.8)
project(mobo_bot_hardware)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

add_executable(lidar_angle_filter src/lidar_angle_filter.cpp)
ament_target_dependencies(lidar_angle_filter rclcpp sensor_msgs)

install(TARGETS
  lidar_angle_filter
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()


# Install launch files.
install(DIRECTORY
    config
    launch
    DESTINATION share/${PROJECT_NAME}/
)

ament_package()
