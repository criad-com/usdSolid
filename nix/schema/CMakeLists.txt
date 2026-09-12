# SPDX-License-Identifier: MIT
cmake_minimum_required(VERSION 3.24)
project(usdSolid VERSION 0.1.6 LANGUAGES CXX)
find_package(pxr CONFIG REQUIRED)
include("${AECO_NATIVE_CMAKE}/AecoNative.cmake")
aeco_codeful_schema(NAME ${PROJECT_NAME} PYTHON_MODULE UsdSolid)
include(CTest)
add_test(NAME registry COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_CURRENT_SOURCE_DIR}/testenv/testRegistry.py")
add_test(NAME upstream-schema COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_CURRENT_SOURCE_DIR}/usdSolid/testenv/testUsdSolidBrepArray.py")
set_tests_properties(registry upstream-schema PROPERTIES ENVIRONMENT
    "PXR_PLUGINPATH_NAME=${CMAKE_BINARY_DIR}/lib;PYTHONPATH=${CMAKE_BINARY_DIR}/python:${AECO_USD_PYTHON}")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/usdSolid/userDoc"
    "${CMAKE_CURRENT_SOURCE_DIR}/usdSolid/testenv"
    DESTINATION share/usdSolid)
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/usdSolid/schema.usda"
    DESTINATION share/usdSolid)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/usdSolid/examples")
    install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/usdSolid/examples"
        DESTINATION share/usdSolid)
endif()
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/UPSTREAM-LICENSE.txt"
    DESTINATION share/licenses/usdSolid)
