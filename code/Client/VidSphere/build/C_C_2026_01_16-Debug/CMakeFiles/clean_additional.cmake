# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "Debug")
  file(REMOVE_RECURSE
  "CMakeFiles/VidSphere_autogen.dir/AutogenUsed.txt"
  "CMakeFiles/VidSphere_autogen.dir/ParseCache.txt"
  "VidSphere_autogen"
  )
endif()
