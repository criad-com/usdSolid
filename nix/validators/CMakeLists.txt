# SPDX-License-Identifier: MIT
cmake_minimum_required(VERSION 3.24)
project(usdSolidValidators VERSION 0.1.4 LANGUAGES CXX)
find_package(pxr CONFIG REQUIRED)
find_package(usdSolid CONFIG REQUIRED)
include("${AECO_NATIVE_CMAKE}/AecoNative.cmake")
set(source "${CMAKE_CURRENT_SOURCE_DIR}/usdSolidValidators")
file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/include/pxr/usdValidation")
file(CREATE_LINK "${source}"
    "${CMAKE_BINARY_DIR}/include/pxr/usdValidation/usdSolidValidators" SYMBOLIC)
add_library(usdSolidValidators SHARED
    "${source}/validators.cpp" "${source}/validatorTokens.cpp")
target_compile_definitions(usdSolidValidators PRIVATE USDSOLIDVALIDATORS_EXPORTS)
target_include_directories(usdSolidValidators PUBLIC
    "$<BUILD_INTERFACE:${CMAKE_BINARY_DIR}/include>" "$<INSTALL_INTERFACE:include>")
target_link_libraries(usdSolidValidators PUBLIC
    usdSolid::usdSolid usdValidation usdGeom usd sdf gf plug tf)
aeco_native_plugin(NAME usdSolidValidators)
install(FILES "${source}/api.h" "${source}/validatorTokens.h"
    DESTINATION include/pxr/usdValidation/usdSolidValidators)
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/UPSTREAM-LICENSE.txt"
    DESTINATION share/licenses/usdSolidValidators)
include(CTest)
add_executable(testUsdSolidValidators "${source}/testenv/testUsdSolidValidators.cpp")
target_link_libraries(testUsdSolidValidators PRIVATE usdSolidValidators)
add_test(NAME upstream-validators COMMAND testUsdSolidValidators)
set_tests_properties(upstream-validators PROPERTIES ENVIRONMENT
    "PXR_PLUGINPATH_NAME=${CMAKE_BINARY_DIR}/lib:${USDSOLID_PLUGIN_PATH}")
install(TARGETS testUsdSolidValidators RUNTIME DESTINATION libexec/usdSolidValidators)
