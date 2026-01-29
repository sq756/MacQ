cmake_minimum_required(VERSION 3.15)
project(MacQ VERSION 1.2.0 LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Source files
set(SOURCES c_engine/src/macq.c)
set(HEADERS c_engine/include/macq.h)

# Shared library
add_library(macq_core SHARED ${SOURCES})

# Include directories
target_include_directories(macq_core PUBLIC c_engine/include)

# Platform-specific configurations
if(APPLE)
    # macOS: Use Accelerate framework
    find_library(ACCELERATE_FRAMEWORK Accelerate)
    if(ACCELERATE_FRAMEWORK)
        target_link_libraries(macq_core PRIVATE ${ACCELERATE_FRAMEWORK})
    endif()
    
    # Universal binary support on macOS (can be overridden by CIBW_ARCHS_MACOS)
    # set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64")
endif()

# Math library
target_link_libraries(macq_core PRIVATE m)

# Installation logic for scikit-build-core
# This ensures the library is placed inside the macq/core directory in the package
install(TARGETS macq_core DESTINATION macq/core)
install(FILES ${HEADERS} DESTINATION macq/include)
