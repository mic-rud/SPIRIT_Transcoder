#include <pybind11/pybind11.h>

void bind_PCCBitstreamReader(pybind11::module&);
void bind_PCCBitstreamWriter(pybind11::module&);
void bind_PCCBitstream(pybind11::module&);
void bind_commons(pybind11::module&);

PYBIND11_MODULE(bitstream_bindings, m) {
    bind_PCCBitstreamReader(m);
    bind_PCCBitstreamWriter(m);
    bind_PCCBitstream(m);
    bind_commons(m);
}
