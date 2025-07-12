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

void bind_commons(py::module &m)
{
    py::class_<PCCHighLevelSyntax>(m, "PCCHighLevelSyntax")
        .def(py::init<>())
        ;

    py::class_<PCCContext, PCCHighLevelSyntax>(m, "PCCContext")
        .def(py::init<>())
        //.def("addV3CParameterSet", static_cast<V3CParameterSet&(PCCContext::*)(uint8_t)>(&PCCContext::addV3CParameterSet), py::arg("index"), py::return_value_policy::reference_internal)
        .def("setBitstreamStat", &PCCContext::setBitstreamStat, py::arg("PCCBitstreamStat&"))
        //.def("setActiveVpsId", &PCCContext::setActiveVpsId, py::arg("val"), py::return_value_policy::reference_internal)
        .def("checkProfile", &PCCContext::checkProfile, py::return_value_policy::reference_internal)
        .def("resizeAtlas", &PCCContext::resizeAtlas, py::arg("size"))
        .def("getVps", static_cast<V3CParameterSet &(PCCContext::*)()>(&PCCContext::getVps), py::return_value_policy::reference_internal)
        .def("getAtlasTileLayerList", &PCCContext::getAtlasTileLayerList, py::return_value_policy::reference_internal)
        .def("setAtlasIndex", &PCCContext::setAtlasIndex, py::arg("atlIdx"))
        .def("setOccupancyPrecision", &PCCContext::setOccupancyPrecision, py::arg("value"))
        .def("getVideoBitstream", static_cast<PCCVideoBitstream &(PCCContext::*)(PCCVideoType)>(&PCCContext::getVideoBitstream), py::return_value_policy::reference_internal);

    py::class_<SampleStreamV3CUnit>(m, "PCCSampleStreamV3CUnit")
        .def(py::init<>())
        .def("size", [](SampleStreamV3CUnit &self)
             { return self.getV3CUnitCount(); })
        .def("getV3CUnit", &SampleStreamV3CUnit::getV3CUnit, py::return_value_policy::reference_internal)
        .def("getV3CUnitCount", &SampleStreamV3CUnit::getV3CUnitCount, py::return_value_policy::reference_internal);

    py::class_<SampleStreamNalUnit>(m, "PCCSampleStreamNalUnit").def(py::init<>());

    py::class_<V3CParameterSet>(m, "V3CParameterSet")
        .def(py::init<>())
        .def("getAtlasCountMinus1", &V3CParameterSet::getAtlasCountMinus1, py::return_value_policy::reference_internal);

    py::class_<AtlasTileLayerRbsp>(m, "AtlasTileLayerRbsp")
        .def(py::init<>())
        .def("getHeader", &AtlasTileLayerRbsp::getHeader, py::return_value_policy::reference_internal)
        .def("getDataUnit", &AtlasTileLayerRbsp::getDataUnit, py::return_value_policy::reference_internal);

    py::class_<AtlasTileHeader>(m, "AtlasTileHeader")
        .def(py::init<>())
        .def("getType", &AtlasTileHeader::getType, py::return_value_policy::reference_internal);

    py::class_<AtlasTileDataUnit>(m, "AtlasTileDataUnit")
        .def(py::init<>())
        .def("addPatchInformationData", static_cast<PatchInformationData &(AtlasTileDataUnit::*)(uint8_t)>(&AtlasTileDataUnit::addPatchInformationData), py::arg("patchMode"))
        .def("getPatchCount", &AtlasTileDataUnit::getPatchCount, py::return_value_policy::reference_internal);

    py::class_<PatchInformationData>(m, "PatchInformationData")
        .def(py::init<>());

    py::enum_<PCCTileType>(m, "PCCTileType")
        .value("P_TILE", P_TILE)
        .value("I_TILE", I_TILE)
        .value("SKIP_TILE", SKIP_TILE)
        .value("RESERVED_3", RESERVED_3);

    py::enum_<PCCPatchModePTile>(m, "PCCPatchModePTile")
        .value("P_END", P_END);

    py::enum_<PCCPatchModeITile>(m, "PCCPatchModeITile")
        .value("I_END", I_END);

    py::class_<PCCVideoBitstream>(m, "PCCVideoBitstream")
        .def(py::init<PCCVideoType>())
        .def("sampleStreamToByteStream", &PCCVideoBitstream::sampleStreamToByteStream,
             py::arg("isAvc") = false,
             py::arg("isVvc") = false,
             py::arg("precision") = 4,
             py::arg("emulationPreventionBytes") = false,
             py::arg("changeStartCodeSize") = true)
        .def("vector", &PCCVideoBitstream::vector, py::return_value_policy::reference_internal)
        .def("resize", &PCCVideoBitstream::resize, py::arg("size"))
        .def("byteStreamToSampleStream", &PCCVideoBitstream::byteStreamToSampleStream,
             py::arg("precision") = 4,
             py::arg("emulationPreventionBytes") = false);
    ;
}