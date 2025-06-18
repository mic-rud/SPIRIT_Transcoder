set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(PYBIND11_FINDPYTHON ON)

find_package(pybind11 REQUIRED)
file(GLOB BINDING_SOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp"
)

configure_file(
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamCommon/include/PCCConfig.h.in
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibCommon/include/PCCConfig.h.in
    ${CMAKE_BINARY_DIR}/generated/PCCConfig.h
)

pybind11_add_module(bitstream_bindings ${BINDING_SOURCES})

target_include_directories(bitstream_bindings PRIVATE
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamReader/include
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamWriter/include
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamCommon/include
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/source/lib/PccLibCommon/include
    ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/dependencies/HM-16.20+SCM-8.8/source/Lib/libmd5
    ${CMAKE_BINARY_DIR}/generated
)

set(MPEG_PCC_LIB_DIR ${CMAKE_SOURCE_DIR}/dependencies/mpeg-pcc-tmc2/lib)

target_link_libraries(bitstream_bindings PRIVATE
    pybind11::module
    ${MPEG_PCC_LIB_DIR}/libPccLibBitstreamReader.a
    ${MPEG_PCC_LIB_DIR}/libPccLibBitstreamWriter.a
    ${MPEG_PCC_LIB_DIR}/libPccLibBitstreamCommon.a
    ${MPEG_PCC_LIB_DIR}/libPccLibCommon.a
    ${MPEG_PCC_LIB_DIR}/liblibmd5.a
)