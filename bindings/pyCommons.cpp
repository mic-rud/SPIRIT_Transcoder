#include <pybind11/pybind11.h>
#include "PCCBitstreamCommon.h"
#include "PCCHighLevelSyntax.h"
#include "PCCSampleStreamV3CUnit.h"
#include "PCCSampleStreamNalUnit.h"
#include "PCCSei.h"
#include "PCCV3CParameterSet.h"
#include <pybind11/stl.h>
#include "PCCContext.h"
#include <PCCFrameContext.h>


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
    
    py::class_<PCCContext, PCCHighLevelSyntax>(m, "PCCContext")
        .def(py::init<>())
        .def("addV3CParameterSet", static_cast<V3CParameterSet&(PCCContext::*)(uint8_t)>(&PCCContext::addV3CParameterSet), py::arg("index"), py::return_value_policy::reference_internal)
        .def("setBitstreamStat", &PCCContext::setBitstreamStat, py::arg("PCCBitstreamStat&"))
        .def("setActiveVpsId", &PCCContext::setActiveVpsId, py::arg("val"), py::return_value_policy::reference_internal)
        .def("checkProfile", &PCCContext::checkProfile, py::return_value_policy::reference_internal)
        .def("resizeAtlas", &PCCContext::resizeAtlas, py::arg("size"))
        .def("getVps", static_cast<V3CParameterSet&(PCCContext::*)()>(&PCCContext::getVps), py::return_value_policy::reference_internal)
        .def("getAtlasTileLayerList", &PCCContext::getAtlasTileLayerList, py::return_value_policy::reference_internal)

        ;
        
    py::class_<SampleStreamV3CUnit>(m, "PCCSampleStreamV3CUnit")
        .def(py::init<>())
        .def("size", [](SampleStreamV3CUnit& self) { return self.getV3CUnitCount(); })
        .def("getV3CUnit", &SampleStreamV3CUnit::getV3CUnit, py::return_value_policy::reference_internal)
        .def("getV3CUnitCount", &SampleStreamV3CUnit::getV3CUnitCount, py:: return_value_policy::reference_internal);

    py::class_<SampleStreamNalUnit>(m, "PCCSampleStreamNalUnit") .def(py::init<>());

    py::class_<V3CParameterSet>(m, "V3CParameterSet")
        .def(py::init<>())
        .def("getAtlasCountMinus1", &V3CParameterSet::getAtlasCountMinus1, py::return_value_policy::reference_internal)
        ;

    py::class_<PCCLogger>(m, "PCCLogger")
        .def(py::init<>())
        //to do
        ;
    
    py::class_<AtlasTileLayerRbsp>(m, "AtlasTileLayerRbsp")
        .def(py::init<>())
        .def("getHeader", &AtlasTileLayerRbsp::getHeader, py::return_value_policy::reference_internal)
        .def("getDataUnit", &AtlasTileLayerRbsp::getDataUnit, py::return_value_policy::automatic_reference)
       ;

    py::class_<AtlasTileHeader>(m, "AtlasTileHeader")
        .def(py::init<>())
        .def("getType", &AtlasTileHeader::getType, py::return_value_policy::reference_internal)
        ;
    
    py::class_<AtlasTileDataUnit>(m, "AtlasTileDataUnit")
        .def(py::init<>())
        .def("addPatchInformationData",static_cast<PatchInformationData& (AtlasTileDataUnit::*)(uint8_t)>(&AtlasTileDataUnit::addPatchInformationData), py::arg("patchMode"))
        ;

    py::class_<PatchInformationData>(m, "PatchInformationData")
        .def(py::init<>())
        ;

    py::enum_<PCCTileType>(m, "PCCTileType")
        .value("P_TILE", P_TILE)
        .value("I_TILE", I_TILE)
        .value("SKIP_TILE", SKIP_TILE)
        .value("RESERVED_3", RESERVED_3)
        ;

    py::enum_<PCCPatchModePTile>(m, "PCCPatchModePTile")
        .value("P_END", P_END)
        ;

    py::enum_<PCCPatchModeITile>(m, "PCCPatchModeITile")
        .value("I_END", I_END)
        ;
}