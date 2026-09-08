#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

static inline float fp16_to_f32(uint16_t h) {
    uint32_t s = (uint32_t)(h >> 15) & 1u;
    uint32_t e = (uint32_t)(h >> 10) & 31u;
    uint32_t f = (uint32_t)h & 1023u;
    uint32_t out;
    if (e == 0) {
        if (f == 0) out = s << 31;
        else {
            int shift = 0;
            while ((f & 0x400u) == 0) { f <<= 1; shift++; }
            f &= 0x3ffu;
            out = (s << 31) | ((uint32_t)(127 - 14 - shift) << 23) | (f << 13);
        }
    } else if (e == 31) {
        out = (s << 31) | 0x7f800000u | (f << 13);
    } else {
        out = (s << 31) | ((e + (127 - 15)) << 23) | (f << 13);
    }
    float v;
    memcpy(&v, &out, sizeof(v));
    return v;
}

static inline float bf16_to_f32(uint16_t b) {
    uint32_t u = ((uint32_t)b) << 16;
    float v;
    memcpy(&v, &u, sizeof(v));
    return v;
}

static inline uint16_t rd16(const uint8_t *p) {
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

static void q4k_scales(const uint8_t *sc, int scale[8], int minv[8]) {
    for (int j = 0; j < 4; ++j) {
        scale[j] = sc[j] & 63;
        minv[j] = sc[j + 4] & 63;
    }
    for (int j = 4; j < 8; ++j) {
        scale[j] = (sc[j + 4] & 15) | ((sc[j - 4] >> 6) << 4);
        minv[j] = (sc[j + 4] >> 4) | ((sc[j] >> 6) << 4);
    }
}

/* R39 is quantized and the reference path ultimately consumes float32 logits.
   Keeping the hot kernel accumulation in float lets the compiler use twice as
   many SIMD lanes as the former double accumulator on x86_64. The live
   native/reference probes remain the correctness oracle for this tradeoff. */
static float dot_row_f32(const uint8_t *row, int cols, const float *x) {
    const float *w = (const float *)row;
    float sum = 0.0f;
    for (int i = 0; i < cols; ++i) sum += w[i] * x[i];
    return sum;
}

static float dot_row_f16(const uint8_t *row, int cols, const float *x) {
    float sum = 0.0f;
    for (int i = 0; i < cols; ++i) sum += fp16_to_f32(rd16(row + 2*i)) * x[i];
    return sum;
}

static float dot_row_bf16(const uint8_t *row, int cols, const float *x) {
    float sum = 0.0f;
    for (int i = 0; i < cols; ++i) sum += bf16_to_f32(rd16(row + 2*i)) * x[i];
    return sum;
}

static float dot_row_q40(const uint8_t *row, int cols, const float *x) {
    float sum = 0.0f;
    const int blocks = cols / 32;
    for (int b = 0; b < blocks; ++b) {
        const uint8_t *p = row + b * 18;
        const float d = fp16_to_f32(rd16(p));
        const uint8_t *q = p + 2;
        const int base = b * 32;
        float local = 0.0f;
        for (int i = 0; i < 16; ++i) {
            local += (float)((int)(q[i] & 15) - 8) * x[base + i];
            local += (float)((int)(q[i] >> 4) - 8) * x[base + 16 + i];
        }
        sum += d * local;
    }
    return sum;
}

static float dot_row_q80(const uint8_t *row, int cols, const float *x) {
    float sum = 0.0f;
    const int blocks = cols / 32;
    for (int b = 0; b < blocks; ++b) {
        const uint8_t *p = row + b * 34;
        const float d = fp16_to_f32(rd16(p));
        const int8_t *q = (const int8_t *)(p + 2);
        const int base = b * 32;
        float local = 0.0f;
        for (int i = 0; i < 32; ++i) local += (float)q[i] * x[base + i];
        sum += d * local;
    }
    return sum;
}

static float dot_row_q4k(const uint8_t *row, int cols, const float *x) {
    float sum = 0.0f;
    const int blocks = cols / 256;
    for (int b = 0; b < blocks; ++b) {
        const uint8_t *p = row + b * 144;
        const float d = fp16_to_f32(rd16(p));
        const float dm = fp16_to_f32(rd16(p + 2));
        const uint8_t *sc = p + 4;
        const uint8_t *qs = p + 16;
        int scale[8], minv[8];
        q4k_scales(sc, scale, minv);
        const int base = b * 256;
        for (int g = 0; g < 4; ++g) {
            const uint8_t *q = qs + g * 32;
            const int o = base + g * 64;
            float sx0 = 0.0f, sx1 = 0.0f, qx0 = 0.0f, qx1 = 0.0f;
            for (int i = 0; i < 32; ++i) {
                const float x0 = x[o + i];
                const float x1 = x[o + 32 + i];
                sx0 += x0;
                sx1 += x1;
                qx0 += (float)(q[i] & 15) * x0;
                qx1 += (float)(q[i] >> 4) * x1;
            }
            sum += d * (float)scale[2*g] * qx0 - dm * (float)minv[2*g] * sx0;
            sum += d * (float)scale[2*g + 1] * qx1 - dm * (float)minv[2*g + 1] * sx1;
        }
    }
    return sum;
}

static float dot_row_q6k(const uint8_t *row, int cols, const float *x) {
    float sum = 0.0f;
    const int blocks = cols / 256;
    for (int b = 0; b < blocks; ++b) {
        const uint8_t *p = row + b * 210;
        const uint8_t *ql = p;
        const uint8_t *qh = p + 128;
        const int8_t *sc = (const int8_t *)(p + 192);
        const float d = fp16_to_f32(rd16(p + 208));
        const int base = b * 256;
        for (int half = 0; half < 2; ++half) {
            const uint8_t *lo0 = ql + half * 64;
            const uint8_t *lo1 = ql + half * 64 + 32;
            const uint8_t *hi = qh + half * 32;
            const int s = half * 8;
            const int o = base + half * 128;
            for (int i = 0; i < 32; ++i) {
                const int ix = i / 16;
                const int q1 = (int)((lo0[i] & 15) | (((hi[i] >> 0) & 3) << 4)) - 32;
                const int q2 = (int)((lo1[i] & 15) | (((hi[i] >> 2) & 3) << 4)) - 32;
                const int q3 = (int)(((lo0[i] >> 4) & 15) | (((hi[i] >> 4) & 3) << 4)) - 32;
                const int q4 = (int)(((lo1[i] >> 4) & 15) | (((hi[i] >> 6) & 3) << 4)) - 32;
                sum += d * (float)sc[s + ix] * (float)q1 * x[o + i];
                sum += d * (float)sc[s + 2 + ix] * (float)q2 * x[o + 32 + i];
                sum += d * (float)sc[s + 4 + ix] * (float)q3 * x[o + 64 + i];
                sum += d * (float)sc[s + 6 + ix] * (float)q4 * x[o + 96 + i];
            }
        }
    }
    return sum;
}

typedef float (*dot_row_fn)(const uint8_t *, int, const float *);

static PyObject *py_matvec(PyObject *self, PyObject *args) {
    const char *kind = NULL;
    PyObject *raw_obj = NULL, *x_obj = NULL;
    int cols = 0, rows = 0;
    if (!PyArg_ParseTuple(args, "sOiiO", &kind, &raw_obj, &cols, &rows, &x_obj)) return NULL;
    if (cols <= 0 || rows <= 0) {
        PyErr_SetString(PyExc_ValueError, "cols and rows must be positive");
        return NULL;
    }

    Py_buffer raw;
    if (PyObject_GetBuffer(raw_obj, &raw, PyBUF_CONTIG_RO) != 0) return NULL;
    PyArrayObject *x_arr = (PyArrayObject *)PyArray_FROM_OTF(x_obj, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY);
    if (!x_arr) { PyBuffer_Release(&raw); return NULL; }
    if (PyArray_SIZE(x_arr) != cols) {
        Py_DECREF(x_arr);
        PyBuffer_Release(&raw);
        PyErr_SetString(PyExc_ValueError, "x size mismatch");
        return NULL;
    }

    int rb = 0;
    dot_row_fn dot = NULL;
    if (strcmp(kind, "f32") == 0) { rb = cols * 4; dot = dot_row_f32; }
    else if (strcmp(kind, "f16") == 0) { rb = cols * 2; dot = dot_row_f16; }
    else if (strcmp(kind, "bf16") == 0) { rb = cols * 2; dot = dot_row_bf16; }
    else if (strcmp(kind, "q4_0") == 0 && cols % 32 == 0) { rb = (cols / 32) * 18; dot = dot_row_q40; }
    else if (strcmp(kind, "q8_0") == 0 && cols % 32 == 0) { rb = (cols / 32) * 34; dot = dot_row_q80; }
    else if (strcmp(kind, "q4_k") == 0 && cols % 256 == 0) { rb = (cols / 256) * 144; dot = dot_row_q4k; }
    else if (strcmp(kind, "q6_k") == 0 && cols % 256 == 0) { rb = (cols / 256) * 210; dot = dot_row_q6k; }
    else {
        Py_DECREF(x_arr);
        PyBuffer_Release(&raw);
        PyErr_SetString(PyExc_ValueError, "unsupported quantizer or block mismatch");
        return NULL;
    }
    if (raw.len < (Py_ssize_t)rb * rows) {
        Py_DECREF(x_arr);
        PyBuffer_Release(&raw);
        PyErr_SetString(PyExc_ValueError, "raw tensor is shorter than expected");
        return NULL;
    }

    npy_intp dims[1] = {rows};
    PyArrayObject *out = (PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_FLOAT32);
    if (!out) { Py_DECREF(x_arr); PyBuffer_Release(&raw); return NULL; }
    const uint8_t *rp = (const uint8_t *)raw.buf;
    const float *x = (const float *)PyArray_DATA(x_arr);
    float *y = (float *)PyArray_DATA(out);

    Py_BEGIN_ALLOW_THREADS
    for (int r = 0; r < rows; ++r) {
        y[r] = dot(rp + (size_t)r * rb, cols, x);
    }
    Py_END_ALLOW_THREADS

    Py_DECREF(x_arr);
    PyBuffer_Release(&raw);
    return (PyObject *)out;
}

static PyMethodDef Methods[] = {
    {"matvec", py_matvec, METH_VARARGS, "Direct quantized matrix-vector multiply."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef Module = {
    PyModuleDef_HEAD_INIT,
    "_r39_native",
    "Native direct-quantized R39 kernels",
    -1,
    Methods
};

PyMODINIT_FUNC PyInit__r39_native(void) {
    import_array();
    return PyModule_Create(&Module);
}
