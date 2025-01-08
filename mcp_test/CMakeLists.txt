cmake_minimum_required(VERSION 3.23)
project(mcp_test)

set(CMAKE_CXX_STANDARD 23)

add_executable(mcp_test main.cpp)

# Create a library for HIDAPI (compile hid.c from the MCP2210-Library)
add_library(hidapi STATIC
        ${CMAKE_SOURCE_DIR}/MCP2210-Library/hid.c
        )

# Add the MCP2210 library (build it from source)
add_library(MCP2210 STATIC
        ${CMAKE_SOURCE_DIR}/MCP2210-Library/mcp2210.cpp
        )

# Link MCP2210 and hidapi libraries to the executable
target_link_libraries(mcp_test PRIVATE MCP2210 hidapi udev)

# Specify the path to the include directory for headers (like hidapi.h)
target_include_directories(mcp_test PRIVATE
        ${CMAKE_SOURCE_DIR}/MCP2210-Library
        )