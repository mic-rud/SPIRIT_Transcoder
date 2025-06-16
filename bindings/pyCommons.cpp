#include <pybind11/pybind11.h>
#include "PCCBitstreamCommon.h"
#include "PCCHighLevelSyntax.h"
#include "PCCSampleStreamV3CUnit.h"
#include "PCCSampleStreamNalUnit.h"
#include "PCCSei.h"
#include "PCCV3CParameterSet.h"
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace pcc;

void bind_commons(py::module& m) {
    py::class_<PCCHighLevelSyntax>(m, "PCCHighLevelSyntax")
        .def(py::init<>())
        .def("setBitstreamStat", &PCCHighLevelSyntax::setBitstreamStat, py::arg("PCCBitstreamStat&"))
        .def("getVps", static_cast<V3CParameterSet&(PCCHighLevelSyntax::*)()>(&PCCHighLevelSyntax::getVps), py::return_value_policy::reference_internal)
        .def("getV3CUnitHeaderAVD", &PCCHighLevelSyntax::getV3CUnitHeaderAVD,  py::return_value_policy::reference_internal)
        .def("getV3CUnitHeaderGVD", &PCCHighLevelSyntax::getV3CUnitHeaderGVD,  py::return_value_policy::reference_internal)
        .def("getV3CUnitHeaderOVD", &PCCHighLevelSyntax::getV3CUnitHeaderOVD,  py::return_value_policy::reference_internal)
        .def("getV3CUnitHeaderAD", &PCCHighLevelSyntax::getV3CUnitHeaderAD,  py::return_value_policy::reference_internal)
        .def("getV3CUnitHeader", &PCCHighLevelSyntax::getV3CUnitHeader, py::arg("index"), py::return_value_policy::reference_internal)
        .def("setActiveVpsId", &PCCHighLevelSyntax::setActiveVpsId, py::arg("val"), py::return_value_policy::reference_internal)
        .def("addV3CParameterSet", static_cast<V3CParameterSet&(PCCHighLevelSyntax::*)(uint8_t)>(&PCCHighLevelSyntax::addV3CParameterSet), py::arg("index"), py::return_value_policy::reference_internal)
        .def("setAtlasIndex", &PCCHighLevelSyntax::setAtlasIndex, py::arg("atlId"))
        ;
        
    py::class_<SampleStreamV3CUnit>(m, "PCCSampleStreamV3CUnit")
        .def(py::init<>())
        .def("size", [](SampleStreamV3CUnit& self) { return self.getV3CUnitCount(); })
        .def("getV3CUnit", &SampleStreamV3CUnit::getV3CUnit, py::return_value_policy::reference_internal)
        .def("getV3CUnitCount", &SampleStreamV3CUnit::getV3CUnitCount, py:: return_value_policy::reference_internal);

    py::class_<SampleStreamNalUnit>(m, "PCCSampleStreamNalUnit") .def(py::init<>());

    py::class_<V3CParameterSet>(m, "V3CParameterSet")
        .def(py::init<>());

}
