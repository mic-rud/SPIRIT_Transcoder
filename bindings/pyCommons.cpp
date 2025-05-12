#include <pybind11/pybind11.h>
#include "PCCBitstreamCommon.h"
#include "PCCHighLevelSyntax.h"
#include "PCCSampleStreamV3CUnit.h"
#include "PCCSampleStreamNalUnit.h"
#include "PCCSei.h"

namespace py = pybind11;
using namespace pcc;

void bind_commons(py::module& m) {
    py::class_<PCCHighLevelSyntax>(m, "PCCHighLevelSyntax") .def(py::init<>());
    py::class_<SampleStreamV3CUnit>(m, "PCCSampleStreamV3CUnit") .def(py::init<>());
    py::class_<SampleStreamNalUnit>(m, "PCCSampleStreamNalUnit") .def(py::init<>());
}
