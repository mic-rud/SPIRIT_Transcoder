#include <pybind11/pybind11.h>
#include "PCCBitstream.h"

namespace py = pybind11;
using namespace pcc;

void bind_PCCBitstream(py::module& m) {
    py::class_<PCCBitstream>(m, "PCCBitstream")
        .def(py::init<>())
        .def("size", &PCCBitstream::size);  // Example method
}
