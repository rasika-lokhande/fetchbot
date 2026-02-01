cmake_minimum_required(VERSION 3.5)
project(fetchbot_interfaces)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Generate interfaces
##### COMMENT OUT THE FOLLOWING AFTER ADDING CUSTOM INTERFACE =============================

rosidl_generate_interfaces(${PROJECT_NAME}
"msg/Detection.msg"
  # Add your custom interfaces here
  # Example:
  # "msg/MyMessage.msg"
  # "srv/MyService.srv"
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()
