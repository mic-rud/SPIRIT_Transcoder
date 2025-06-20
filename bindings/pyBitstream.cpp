#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "PCCBitstream.h"

namespace py = pybind11;
using namespace pcc;

void bind_PCCBitstream(py::module& m) {
    py::class_<PCCBitstream>(m, "PCCBitstream")
        .def(py::init<>())
        .def("size", &PCCBitstream::size)  // Example method
        .def("initialize", py::overload_cast<const std::string&>(&PCCBitstream::initialize),py::arg("compressedStreamPath"),py::return_value_policy::reference_internal)
        .def("write", static_cast<bool (PCCBitstream::*)(const std::string&)>(&PCCBitstream::write), py::arg("compressedStreamPath"))
        //.def("initialize", py::overload_cast<uint64_t>(&PCCBitstream::initialize),py::arg("bitStreamSize"))
        //.def("vector", &PCCBitstream::vector, py::return_value_policy::reference_internal)
        //.def("computeMD5", &PCCBitstream::computeMD5) //not working :(
        ;

    py::class_<PCCBitstreamStat>(m, "PCCBitstreamStat")
        .def(py::init<>())
        .def("setHeader", &PCCBitstreamStat::setHeader, py::arg("size"))
        .def("incrHeader", &PCCBitstreamStat::incrHeader, py::arg("size"))
        //.def("setV3CUnitSize", &PCCBitstreamStat::setV3CUnitSize, py::arg("type"), py::arg("size"))
        //.def("getV3CUnitSize", &PCCBitstreamStat::getV3CUnitSize, py::arg("type"), py::return_value_policy::reference_internal)
        .def("trace", &PCCBitstreamStat::trace, py::arg("byGOF "))
        ;

    py::enum_<V3CUnitType>(m, "V3CUnitType")
        .value("V3C_VPS", V3C_VPS)
        .value("V3C_AD", V3C_AD)
        .value("V3C_OVD", V3C_OVD)
        .value("V3C_GVD", V3C_GVD)
        .value("V3C_AVD", V3C_AVD)
        .value("NUM_V3C_UNIT_TYPE", NUM_V3C_UNIT_TYPE);
} 
