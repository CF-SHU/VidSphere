cmake_minimum_required(VERSION 3.5)

project(VidSphere VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets Network Multimedia MultimediaWidgets)
qt_standard_project_setup()

qt_add_executable(VidSphere
    playvideoui.h playvideoui.cpp
    playvideoui.ui
    main.cpp
    playvideo.h playvideo.cpp
    video.h video.cpp
    downloadvideowidget.h downloadvideowidget.cpp
)

target_compile_features(VidSphere PRIVATE cxx_std_23)

target_link_libraries(VidSphere
    PRIVATE
    Qt6::Core
    Qt6::Gui
    Qt6::Widgets
    Qt6::Network
    Qt6::Multimedia
    Qt6::MultimediaWidgets
)

set_target_properties(VidSphere PROPERTIES
    AUTORCC TRUE
    ${BUNDLE_ID_OPTION}
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

include(GNUInstallDirs)
install(TARGETS VidSphere
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

































# set(CMAKE_CXX_STANDARD_REQUIRED ON)
#
# @if false
# find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets LinguistTools)
# find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets LinguistTools)
#
# set(TS_FILES )
# @else
# find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets)
# find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets)
# @endif
#
# qt_standard_project_setup()
#
# set(PROJECT_SOURCES
#         main.cpp
#         playvideoui.cpp
#         playvideoui.h
#     @if true
#         playvideoui.ui
#     @endif
#     @if false
#         ${TS_FILES}
#     @endif
# )
#
# if(${QT_VERSION_MAJOR} GREATER_EQUAL 6)
#     qt_add_executable(VidSphere
#         MANUAL_FINALIZATION
#         ${PROJECT_SOURCES}
#     )
# # Define target properties for Android with Qt 6 as:
# #    set_property(TARGET VidSphere APPEND PROPERTY QT_ANDROID_PACKAGE_SOURCE_DIR
# #                 ${CMAKE_CURRENT_SOURCE_DIR}/android)
# # For more information, see https://doc.qt.io/qt-6/qt-add-executable.html#target-creation
# @if false
#     qt_create_translation(QM_FILES ${CMAKE_SOURCE_DIR} ${TS_FILES})
# @endif
# else()
#     if(ANDROID)
#         add_library(VidSphere SHARED
#             ${PROJECT_SOURCES}
#         )
# # Define properties for Android with Qt 5 after find_package() calls as:
# #    set(ANDROID_PACKAGE_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/android")
#     else()
#         add_executable(VidSphere
#             ${PROJECT_SOURCES}
#         )
#     endif()
# @if false
#
#     qt5_create_translation(QM_FILES ${CMAKE_SOURCE_DIR} ${TS_FILES})
# @endif
# endif()
#
# target_link_libraries(VidSphere
#     PRIVATE
#         Qt${QT_VERSION_MAJOR}::Widgets
# )
#
# # Qt for iOS sets MACOSX_BUNDLE_GUI_IDENTIFIER automatically since Qt 6.1.
# # If you are developing for iOS or macOS you should consider setting an
# # explicit, fixed bundle identifier manually though.
# if(${QT_VERSION} VERSION_LESS 6.1.0)
#   set(BUNDLE_ID_OPTION MACOSX_BUNDLE_GUI_IDENTIFIER com.example.VidSphere)
# endif()
#
# set_target_properties(VidSphere PROPERTIES
#     AUTORCC TRUE
#     ${BUNDLE_ID_OPTION}
#     MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
#     MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
#     MACOSX_BUNDLE TRUE
#     WIN32_EXECUTABLE TRUE
# )
#
# include(GNUInstallDirs)
# install(TARGETS VidSphere
#     BUNDLE DESTINATION .
#     LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
#     RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
# )
#
# if(QT_VERSION_MAJOR EQUAL 6)
#     qt_finalize_executable(VidSphere) #该命令在CMake3.19以后已经不需要使用了
# endif()



#qt_add_executable(VidSphere)  //Creates and finalizes an application target of a platform-specific type.
#This command performs the following tasks:

#    1. Create a CMake target of the appropriate type for the target platform.
#    2. Link the target to the Qt::Core library.
#    3. Handle finalization of the CMake target.
