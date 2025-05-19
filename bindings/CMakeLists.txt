find_package(pybind11 REQUIRED)
file(GLOB BINDING_SOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp"
)

configure_file(
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamCommon/include/PCCConfig.h.in
    ${CMAKE_BINARY_DIR}/generated/PCCConfig.h
)

add_library(bitstream_bindings MODULE ${BINDING_SOURCES})
add_library(PccLibBitstreamReader SHARED
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamReader/source/PCCBitstreamReader.cpp
)
add_library(PccLibBitstreamWriter SHARED
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamWriter/source/PCCBitstreamWriter.cpp
)

target_include_directories(PccLibBitstreamReader PUBLIC
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamReader/include
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamCommon/include
    ${CMAKE_BINARY_DIR}/generated
)
target_include_directories(PccLibBitstreamWriter PUBLIC
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamWriter/include
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamCommon/include
    ${CMAKE_BINARY_DIR}/generated
)

target_link_libraries(bitstream_bindings
    pybind11::module
    PccLibBitstreamReader
    PccLibBitstreamWriter
)