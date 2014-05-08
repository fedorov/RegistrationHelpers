cmake_minimum_required(VERSION 2.8.9)

project(RegistrationHelpers)

#-----------------------------------------------------------------------------
set(EXTENSION_HOMEPAGE "")
set(EXTENSION_CATEGORY "Utilities")
set(EXTENSION_CONTRIBUTORS "Andrey Fedorov (BWH)")
set(EXTENSION_DESCRIPTION "")
set(EXTENSION_ICONURL "")
set(EXTENSION_SCREENSHOTURLS "")

#-----------------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
add_subdirectory(TransformFiducialList)
add_subdirectory(SurfaceToBinaryImage)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
