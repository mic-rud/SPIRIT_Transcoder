#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "PCCBitstream.h"
#include "PCCBitstreamReader.h"
#include "PCCBitstreamCommon.h"  
#include "PCCHighLevelSyntax.h"

namespace py = pybind11;
using namespace pcc;

void bind_PCCBitstreamReader(py::module& m) {
    py::class_<PCCBitstreamReader>(m, "PCCBitstreamReader")
        .def(py::init<>())
        .def("decode", &PCCBitstreamReader::decode, py::arg("ssvu"), py::arg("syntax"), py::return_value_policy::reference_internal)
        .def_static("read", [](PCCBitstream& bitstream, SampleStreamV3CUnit& ssvu) {
            return PCCBitstreamReader::read(bitstream, ssvu);
        });
}
