
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "PCCBitstreamWriter.h"
#include "PCCBitstream.h"
#include "PCCBitstreamCommon.h"  
#include "PCCHighLevelSyntax.h"
#include "PCCSampleStreamV3CUnit.h"
#include "PCCSampleStreamNalUnit.h"
#include "PCCSei.h"

namespace py = pybind11;
using namespace pcc;

void bind_PCCBitstreamWriter(py::module& m) {
    py::class_<PCCBitstreamWriter>(m, "PCCBitstreamWriter")
        .def(py::init<>())
        .def("encode", &PCCBitstreamWriter::encode, py::arg("syntax"), py::arg("ssvu"))
        .def("write_v3c", [](PCCBitstreamWriter& self, SampleStreamV3CUnit& ssvu, PCCBitstream& bitstream, uint32_t precision){
            return self.write(ssvu, bitstream, precision);
        }, py::arg("ssvu"), py::arg("bitstream"), py::arg("precision") = 0)
        .def("write_nal", [](PCCBitstreamWriter& self, SampleStreamNalUnit& ssnu, PCCBitstream& bitstream, uint32_t precision){
            return self.write(ssnu, bitstream, precision);
        }, py::arg("ssnu"), py::arg("bitstream"), py::arg("precision") = 0);
}
