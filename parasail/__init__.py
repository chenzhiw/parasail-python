
import ctypes
import platform
import os
import sys

import numpy

__version__ = "1.0.0"
__title__ = "parasail"
__description__ = "pairwise sequence alignment library"
__uri__ = "https://github.com/jeffdaily/parasail-python"
__author__ = "Jeff Daily"
__email__ = "jeff.daily@pnnl.gov"
__license__ = "BSD"
__copyright__ = "Copyright (c) 2016 Jeff Daily"

_libname = "libparasail.so"
if platform.system() == 'Darwin':
    _libname = "libparasail.dylib"
elif platform.system() == 'Windows':
    _libname = "parasail.dll"
_libpath = os.path.join(os.path.dirname(__file__), _libname)

_lib = None
if os.path.exists(_libpath):
    _lib = ctypes.CDLL(_libpath)
else:
    _lib = ctypes.CDLL(_libname)

def _make_nd_array(c_pointer, shape, dtype=numpy.intc, order='C', own_data=True):
    arr_size = numpy.prod(shape[:]) * numpy.dtype(dtype).itemsize 
    if sys.version_info.major >= 3:
        buf_from_mem = ctypes.pythonapi.PyMemoryView_FromMemory
        buf_from_mem.restype = ctypes.py_object
        buf_from_mem.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
        buffer = buf_from_mem(c_pointer, arr_size, 0x100)
    else:
        buf_from_mem = ctypes.pythonapi.PyBuffer_FromMemory
        buf_from_mem.restype = ctypes.py_object
        buffer = buf_from_mem(c_pointer, arr_size)
    return numpy.ndarray(tuple(shape[:]), dtype, buffer, order=order)

c_int_p = ctypes.POINTER(ctypes.c_int)

class result_t(ctypes.Structure):
    _fields_ = [
       ("saturated",     ctypes.c_int),
       ("score",         ctypes.c_int),
       ("matches",       ctypes.c_int),
       ("similar",       ctypes.c_int),
       ("length",        ctypes.c_int),
       ("end_query",     ctypes.c_int),
       ("end_ref",       ctypes.c_int),
       ("score_table",   c_int_p),
       ("matches_table", c_int_p),
       ("similar_table", c_int_p),
       ("length_table",  c_int_p),
       ("score_row",     c_int_p),
       ("matches_row",   c_int_p),
       ("similar_row",   c_int_p),
       ("length_row",    c_int_p),
       ("score_col",     c_int_p),
       ("matches_col",   c_int_p),
       ("similar_col",   c_int_p),
       ("length_col",    c_int_p)
       ]

c_result_p = ctypes.POINTER(result_t)

class Result:
    def __init__(self, pointer, len_query, len_ref):
        self.pointer = pointer
        self.len_query = len_query
        self.len_ref = len_ref
        self._as_parameter_ = pointer
    def __del__(self):
        _lib.parasail_result_free(self.pointer)
    @property
    def saturated(self):
        return self.pointer[0].saturated != 0
    @property
    def score(self):
        return self.pointer[0].score
    @property
    def matches(self):
        return self.pointer[0].matches
    @property
    def similar(self):
        return self.pointer[0].similar
    @property
    def length(self):
        return self.pointer[0].length
    @property
    def end_query(self):
        return self.pointer[0].end_query
    @property
    def end_ref(self):
        return self.pointer[0].end_ref
    @property
    def score_table(self):
        return _make_nd_array(
            self.pointer[0].score_table,
            (self.len_query, self.len_ref))
    @property
    def matches_table(self):
        return _make_nd_array(
            self.pointer[0].matches_table,
            (self.len_query, self.len_ref))
    @property
    def similar_table(self):
        return _make_nd_array(
            self.pointer[0].similar_table,
            (self.len_query, self.len_ref))
    @property
    def length_table(self):
        return _make_nd_array(
            self.pointer[0].length_table,
            (self.len_query, self.len_ref))
    @property
    def score_row(self):
        return _make_nd_array(
            self.pointer[0].score_row,
            (self.len_ref,))
    @property
    def matches_row(self):
        return _make_nd_array(
            self.pointer[0].matches_row,
            (self.len_ref,))
    @property
    def similar_row(self):
        return _make_nd_array(
            self.pointer[0].similar_row,
            (self.len_ref,))
    @property
    def length_row(self):
        return _make_nd_array(
            self.pointer[0].length_row,
            (self.len_ref,))
    @property
    def score_col(self):
        return _make_nd_array(
            self.pointer[0].score_col,
            (self.len_query,))
    @property
    def matches_col(self):
        return _make_nd_array(
            self.pointer[0].matches_col,
            (self.len_query,))
    @property
    def similar_col(self):
        return _make_nd_array(
            self.pointer[0].similar_col,
            (self.len_query,))
    @property
    def length_col(self):
        return _make_nd_array(
            self.pointer[0].length_col,
            (self.len_query,))

class matrix_t(ctypes.Structure):
    _fields_ = [
        ("name",      ctypes.c_char_p),
        ("matrix",    c_int_p),
        ("mapper",    c_int_p),
        ("size",      ctypes.c_int),
        ("max",       ctypes.c_int),
        ("min",       ctypes.c_int),
        ("need_free", ctypes.c_int)
        ]

c_matrix_p = ctypes.POINTER(matrix_t)

class Matrix:
    def __init__(self, pointer):
        self.pointer = pointer
        self._as_parameter_ = pointer
    def __del__(self):
        if self.pointer[0].need_free:
            _lib.parasail_matrix_free(self.pointer)
    @property
    def name(self):
        return self.pointer[0].name
    @property
    def matrix(self):
        return _make_nd_array(
            self.pointer[0].matrix,
            (self.pointer[0].size, self.pointer[0].size))
    @property
    def size(self):
        return self.pointer[0].size
    @property
    def max(self):
        return self.pointer[0].max
    @property
    def min(self):
        return self.pointer[0].min

class profile_data_t(ctypes.Structure):
    _fields_ = [
        ("score", ctypes.c_void_p),
        ("matches", ctypes.c_void_p),
        ("similar", ctypes.c_void_p)
    ]

class profile_t(ctypes.Structure):
    _fields_ = [
        ("s1", ctypes.c_char_p),
        ("s1Len", ctypes.c_int),
        ("matrix", c_matrix_p),
        ("profile8", profile_data_t),
        ("profile16", profile_data_t),
        ("profile32", profile_data_t),
        ("profile64", profile_data_t),
        ("free", ctypes.c_void_p),
        ("stop", ctypes.c_int)
        ]

c_profile_p = ctypes.POINTER(profile_t)

class Profile:
    def __init__(self, pointer, matrix):
        self.pointer = pointer
        self.matrix_ = matrix
        self._as_parameter_ = pointer
    def __del__(self):
        _lib.parasail_profile_free(self.pointer)
    @property
    def s1(self):
        return self.pointer[0].s1
    @property
    def s1Len(self):
        return self.pointer[0].s1Len
    @property
    def matrix(self):
        return self.matrix_

_profile_create_argtypes = [ctypes.c_char_p, ctypes.c_int, c_matrix_p]

_lib.parasail_profile_create_8.argtypes = _profile_create_argtypes
_lib.parasail_profile_create_8.restype = c_profile_p

_lib.parasail_profile_create_16.argtypes = _profile_create_argtypes
_lib.parasail_profile_create_16.restype = c_profile_p

_lib.parasail_profile_create_32.argtypes = _profile_create_argtypes
_lib.parasail_profile_create_32.restype = c_profile_p

_lib.parasail_profile_create_64.argtypes = _profile_create_argtypes
_lib.parasail_profile_create_64.restype = c_profile_p

_lib.parasail_profile_create_sat.argtypes = _profile_create_argtypes
_lib.parasail_profile_create_sat.restype = c_profile_p

_lib.parasail_profile_create_stats_8.argtypes = _profile_create_argtypes
_lib.parasail_profile_create_stats_8.restype = c_profile_p

_lib.parasail_profile_create_stats_16.argtypes = _profile_create_argtypes
_lib.parasail_profile_create_stats_16.restype = c_profile_p

_lib.parasail_profile_create_stats_32.argtypes = _profile_create_argtypes
_lib.parasail_profile_create_stats_32.restype = c_profile_p

_lib.parasail_profile_create_stats_64.argtypes = _profile_create_argtypes
_lib.parasail_profile_create_stats_64.restype = c_profile_p

_lib.parasail_profile_create_stats_sat.argtypes = _profile_create_argtypes
_lib.parasail_profile_create_stats_sat.restype = c_profile_p

def profile_create_8(s1, matrix):
    return Profile(_lib.parasail_profile_create_8(s1, len(s1), matrix), matrix)

def profile_create_16(s1, matrix):
    return Profile(_lib.parasail_profile_create_16(s1, len(s1), matrix), matrix)

def profile_create_32(s1, matrix):
    return Profile(_lib.parasail_profile_create_32(s1, len(s1), matrix), matrix)

def profile_create_64(s1, matrix):
    return Profile(_lib.parasail_profile_create_64(s1, len(s1), matrix), matrix)

def profile_create_sat(s1, matrix):
    return Profile(_lib.parasail_profile_create_sat(s1, len(s1), matrix), matrix)

def profile_create_stats_8(s1, matrix):
    return Profile(_lib.parasail_profile_create_stats_8(s1, len(s1), matrix), matrix)

def profile_create_stats_16(s1, matrix):
    return Profile(_lib.parasail_profile_create_stats_16(s1, len(s1), matrix), matrix)

def profile_create_stats_32(s1, matrix):
    return Profile(_lib.parasail_profile_create_stats_32(s1, len(s1), matrix), matrix)

def profile_create_stats_64(s1, matrix):
    return Profile(_lib.parasail_profile_create_stats_64(s1, len(s1), matrix), matrix)

def profile_create_stats_sat(s1, matrix):
    return Profile(_lib.parasail_profile_create_stats_sat(s1, len(s1), matrix), matrix)

def can_use_avx2():
    return bool(_lib.parasail_can_use_avx2())

def can_use_sse41():
    return bool(_lib.parasail_can_use_sse41())

def can_use_sse2():
    return bool(_lib.parasail_can_use_sse2())

# begin non-alignment functions defined here

# parasail_profile_free is not exposed.
# Memory is managed by the Profile class.
_lib.parasail_profile_free.argtypes = [c_profile_p]
_lib.parasail_profile_free.restype = None

# parasail_result_free is not exposed.
# Memory is managed by the Result class.
_lib.parasail_result_free.argtypes = [c_result_p]
_lib.parasail_result_free.restype = None

_lib.parasail_version.argtypes = [c_int_p, c_int_p, c_int_p]
_lib.parasail_version.restype = None

def version():
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    _lib.parasail_version(
            ctypes.byref(major),
            ctypes.byref(minor),
            ctypes.byref(patch))
    return major.value, minor.value, patch.value

_lib.parasail_time.argtypes = []
_lib.parasail_time.restype = ctypes.c_double

def time():
    return _lib.parasail_time()

_lib.parasail_matrix_lookup
_lib.parasail_matrix_lookup.argtypes = [ctypes.c_char_p]
_lib.parasail_matrix_lookup.restype = c_matrix_p

blosum100 = Matrix(_lib.parasail_matrix_lookup("blosum100"))
blosum30 = Matrix(_lib.parasail_matrix_lookup("blosum30"))
blosum35 = Matrix(_lib.parasail_matrix_lookup("blosum35"))
blosum40 = Matrix(_lib.parasail_matrix_lookup("blosum40"))
blosum45 = Matrix(_lib.parasail_matrix_lookup("blosum45"))
blosum50 = Matrix(_lib.parasail_matrix_lookup("blosum50"))
blosum55 = Matrix(_lib.parasail_matrix_lookup("blosum55"))
blosum60 = Matrix(_lib.parasail_matrix_lookup("blosum60"))
blosum62 = Matrix(_lib.parasail_matrix_lookup("blosum62"))
blosum65 = Matrix(_lib.parasail_matrix_lookup("blosum65"))
blosum70 = Matrix(_lib.parasail_matrix_lookup("blosum70"))
blosum75 = Matrix(_lib.parasail_matrix_lookup("blosum75"))
blosum80 = Matrix(_lib.parasail_matrix_lookup("blosum80"))
blosum85 = Matrix(_lib.parasail_matrix_lookup("blosum85"))
blosum90 = Matrix(_lib.parasail_matrix_lookup("blosum90"))
pam10 = Matrix(_lib.parasail_matrix_lookup("pam10"))
pam100 = Matrix(_lib.parasail_matrix_lookup("pam100"))
pam110 = Matrix(_lib.parasail_matrix_lookup("pam110"))
pam120 = Matrix(_lib.parasail_matrix_lookup("pam120"))
pam130 = Matrix(_lib.parasail_matrix_lookup("pam130"))
pam140 = Matrix(_lib.parasail_matrix_lookup("pam140"))
pam150 = Matrix(_lib.parasail_matrix_lookup("pam150"))
pam160 = Matrix(_lib.parasail_matrix_lookup("pam160"))
pam170 = Matrix(_lib.parasail_matrix_lookup("pam170"))
pam180 = Matrix(_lib.parasail_matrix_lookup("pam180"))
pam190 = Matrix(_lib.parasail_matrix_lookup("pam190"))
pam20 = Matrix(_lib.parasail_matrix_lookup("pam20"))
pam200 = Matrix(_lib.parasail_matrix_lookup("pam200"))
pam210 = Matrix(_lib.parasail_matrix_lookup("pam210"))
pam220 = Matrix(_lib.parasail_matrix_lookup("pam220"))
pam230 = Matrix(_lib.parasail_matrix_lookup("pam230"))
pam240 = Matrix(_lib.parasail_matrix_lookup("pam240"))
pam250 = Matrix(_lib.parasail_matrix_lookup("pam250"))
pam260 = Matrix(_lib.parasail_matrix_lookup("pam260"))
pam270 = Matrix(_lib.parasail_matrix_lookup("pam270"))
pam280 = Matrix(_lib.parasail_matrix_lookup("pam280"))
pam290 = Matrix(_lib.parasail_matrix_lookup("pam290"))
pam30 = Matrix(_lib.parasail_matrix_lookup("pam30"))
pam300 = Matrix(_lib.parasail_matrix_lookup("pam300"))
pam310 = Matrix(_lib.parasail_matrix_lookup("pam310"))
pam320 = Matrix(_lib.parasail_matrix_lookup("pam320"))
pam330 = Matrix(_lib.parasail_matrix_lookup("pam330"))
pam340 = Matrix(_lib.parasail_matrix_lookup("pam340"))
pam350 = Matrix(_lib.parasail_matrix_lookup("pam350"))
pam360 = Matrix(_lib.parasail_matrix_lookup("pam360"))
pam370 = Matrix(_lib.parasail_matrix_lookup("pam370"))
pam380 = Matrix(_lib.parasail_matrix_lookup("pam380"))
pam390 = Matrix(_lib.parasail_matrix_lookup("pam390"))
pam40 = Matrix(_lib.parasail_matrix_lookup("pam40"))
pam400 = Matrix(_lib.parasail_matrix_lookup("pam400"))
pam410 = Matrix(_lib.parasail_matrix_lookup("pam410"))
pam420 = Matrix(_lib.parasail_matrix_lookup("pam420"))
pam430 = Matrix(_lib.parasail_matrix_lookup("pam430"))
pam440 = Matrix(_lib.parasail_matrix_lookup("pam440"))
pam450 = Matrix(_lib.parasail_matrix_lookup("pam450"))
pam460 = Matrix(_lib.parasail_matrix_lookup("pam460"))
pam470 = Matrix(_lib.parasail_matrix_lookup("pam470"))
pam480 = Matrix(_lib.parasail_matrix_lookup("pam480"))
pam490 = Matrix(_lib.parasail_matrix_lookup("pam490"))
pam50 = Matrix(_lib.parasail_matrix_lookup("pam50"))
pam500 = Matrix(_lib.parasail_matrix_lookup("pam500"))
pam60 = Matrix(_lib.parasail_matrix_lookup("pam60"))
pam70 = Matrix(_lib.parasail_matrix_lookup("pam70"))
pam80 = Matrix(_lib.parasail_matrix_lookup("pam80"))
pam90 = Matrix(_lib.parasail_matrix_lookup("pam90"))

_lib.parasail_matrix_create.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
_lib.parasail_matrix_create.restype = c_matrix_p

def matrix_create(alphabet, match, mismatch):
    return Matrix(_lib.parasail_matrix_create(alphabet, match, mismatch))

# parasail_matrix_free is not exposed.
# Memory is managed by the Matrix class.
_lib.parasail_matrix_free.argtypes = [c_matrix_p]
_lib.parasail_matrix_free.restype = None

# begin generated names here

_argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, c_matrix_p]


_lib.parasail_nw.argtypes = _argtypes
_lib.parasail_nw.restype = c_result_p
def nw(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table.argtypes = _argtypes
_lib.parasail_nw_table.restype = c_result_p
def nw_table(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol.argtypes = _argtypes
_lib.parasail_nw_rowcol.restype = c_result_p
def nw_rowcol(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats.argtypes = _argtypes
_lib.parasail_nw_stats.restype = c_result_p
def nw_stats(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table.argtypes = _argtypes
_lib.parasail_nw_stats_table.restype = c_result_p
def nw_stats_table(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol.restype = c_result_p
def nw_stats_rowcol(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg.argtypes = _argtypes
_lib.parasail_sg.restype = c_result_p
def sg(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table.argtypes = _argtypes
_lib.parasail_sg_table.restype = c_result_p
def sg_table(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol.argtypes = _argtypes
_lib.parasail_sg_rowcol.restype = c_result_p
def sg_rowcol(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats.argtypes = _argtypes
_lib.parasail_sg_stats.restype = c_result_p
def sg_stats(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table.argtypes = _argtypes
_lib.parasail_sg_stats_table.restype = c_result_p
def sg_stats_table(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol.restype = c_result_p
def sg_stats_rowcol(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw.argtypes = _argtypes
_lib.parasail_sw.restype = c_result_p
def sw(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table.argtypes = _argtypes
_lib.parasail_sw_table.restype = c_result_p
def sw_table(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol.argtypes = _argtypes
_lib.parasail_sw_rowcol.restype = c_result_p
def sw_rowcol(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats.argtypes = _argtypes
_lib.parasail_sw_stats.restype = c_result_p
def sw_stats(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table.argtypes = _argtypes
_lib.parasail_sw_stats_table.restype = c_result_p
def sw_stats_table(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol.restype = c_result_p
def sw_stats_rowcol(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_scan.argtypes = _argtypes
_lib.parasail_nw_scan.restype = c_result_p
def nw_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_scan.argtypes = _argtypes
_lib.parasail_nw_table_scan.restype = c_result_p
def nw_table_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_scan.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan.restype = c_result_p
def nw_rowcol_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_scan.argtypes = _argtypes
_lib.parasail_nw_stats_scan.restype = c_result_p
def nw_stats_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_scan.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan.restype = c_result_p
def nw_stats_table_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_scan.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan.restype = c_result_p
def nw_stats_rowcol_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_scan.argtypes = _argtypes
_lib.parasail_sg_scan.restype = c_result_p
def sg_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_scan.argtypes = _argtypes
_lib.parasail_sg_table_scan.restype = c_result_p
def sg_table_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_scan.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan.restype = c_result_p
def sg_rowcol_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_scan.argtypes = _argtypes
_lib.parasail_sg_stats_scan.restype = c_result_p
def sg_stats_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_scan.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan.restype = c_result_p
def sg_stats_table_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_scan.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan.restype = c_result_p
def sg_stats_rowcol_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_scan.argtypes = _argtypes
_lib.parasail_sw_scan.restype = c_result_p
def sw_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_scan.argtypes = _argtypes
_lib.parasail_sw_table_scan.restype = c_result_p
def sw_table_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_scan.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan.restype = c_result_p
def sw_rowcol_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_scan.argtypes = _argtypes
_lib.parasail_sw_stats_scan.restype = c_result_p
def sw_stats_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_scan.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan.restype = c_result_p
def sw_stats_table_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_scan.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan.restype = c_result_p
def sw_stats_rowcol_scan(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_scan(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_scan_64.argtypes = _argtypes
_lib.parasail_nw_scan_64.restype = c_result_p
def nw_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_scan_32.argtypes = _argtypes
_lib.parasail_nw_scan_32.restype = c_result_p
def nw_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_scan_16.argtypes = _argtypes
_lib.parasail_nw_scan_16.restype = c_result_p
def nw_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_scan_8.argtypes = _argtypes
_lib.parasail_nw_scan_8.restype = c_result_p
def nw_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_scan_sat.argtypes = _argtypes
_lib.parasail_nw_scan_sat.restype = c_result_p
def nw_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_striped_64.argtypes = _argtypes
_lib.parasail_nw_striped_64.restype = c_result_p
def nw_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_striped_32.argtypes = _argtypes
_lib.parasail_nw_striped_32.restype = c_result_p
def nw_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_striped_16.argtypes = _argtypes
_lib.parasail_nw_striped_16.restype = c_result_p
def nw_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_striped_8.argtypes = _argtypes
_lib.parasail_nw_striped_8.restype = c_result_p
def nw_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_striped_sat.argtypes = _argtypes
_lib.parasail_nw_striped_sat.restype = c_result_p
def nw_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_diag_64.argtypes = _argtypes
_lib.parasail_nw_diag_64.restype = c_result_p
def nw_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_diag_32.argtypes = _argtypes
_lib.parasail_nw_diag_32.restype = c_result_p
def nw_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_diag_16.argtypes = _argtypes
_lib.parasail_nw_diag_16.restype = c_result_p
def nw_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_diag_8.argtypes = _argtypes
_lib.parasail_nw_diag_8.restype = c_result_p
def nw_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_diag_sat.argtypes = _argtypes
_lib.parasail_nw_diag_sat.restype = c_result_p
def nw_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_scan_64.argtypes = _argtypes
_lib.parasail_nw_table_scan_64.restype = c_result_p
def nw_table_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_scan_32.argtypes = _argtypes
_lib.parasail_nw_table_scan_32.restype = c_result_p
def nw_table_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_scan_16.argtypes = _argtypes
_lib.parasail_nw_table_scan_16.restype = c_result_p
def nw_table_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_scan_8.argtypes = _argtypes
_lib.parasail_nw_table_scan_8.restype = c_result_p
def nw_table_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_scan_sat.argtypes = _argtypes
_lib.parasail_nw_table_scan_sat.restype = c_result_p
def nw_table_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_striped_64.argtypes = _argtypes
_lib.parasail_nw_table_striped_64.restype = c_result_p
def nw_table_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_striped_32.argtypes = _argtypes
_lib.parasail_nw_table_striped_32.restype = c_result_p
def nw_table_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_striped_16.argtypes = _argtypes
_lib.parasail_nw_table_striped_16.restype = c_result_p
def nw_table_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_striped_8.argtypes = _argtypes
_lib.parasail_nw_table_striped_8.restype = c_result_p
def nw_table_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_striped_sat.argtypes = _argtypes
_lib.parasail_nw_table_striped_sat.restype = c_result_p
def nw_table_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_diag_64.argtypes = _argtypes
_lib.parasail_nw_table_diag_64.restype = c_result_p
def nw_table_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_diag_32.argtypes = _argtypes
_lib.parasail_nw_table_diag_32.restype = c_result_p
def nw_table_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_diag_16.argtypes = _argtypes
_lib.parasail_nw_table_diag_16.restype = c_result_p
def nw_table_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_diag_8.argtypes = _argtypes
_lib.parasail_nw_table_diag_8.restype = c_result_p
def nw_table_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_table_diag_sat.argtypes = _argtypes
_lib.parasail_nw_table_diag_sat.restype = c_result_p
def nw_table_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_table_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_scan_64.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan_64.restype = c_result_p
def nw_rowcol_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_scan_32.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan_32.restype = c_result_p
def nw_rowcol_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_scan_16.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan_16.restype = c_result_p
def nw_rowcol_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_scan_8.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan_8.restype = c_result_p
def nw_rowcol_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_scan_sat.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan_sat.restype = c_result_p
def nw_rowcol_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_striped_64.argtypes = _argtypes
_lib.parasail_nw_rowcol_striped_64.restype = c_result_p
def nw_rowcol_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_striped_32.argtypes = _argtypes
_lib.parasail_nw_rowcol_striped_32.restype = c_result_p
def nw_rowcol_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_striped_16.argtypes = _argtypes
_lib.parasail_nw_rowcol_striped_16.restype = c_result_p
def nw_rowcol_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_striped_8.argtypes = _argtypes
_lib.parasail_nw_rowcol_striped_8.restype = c_result_p
def nw_rowcol_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_striped_sat.argtypes = _argtypes
_lib.parasail_nw_rowcol_striped_sat.restype = c_result_p
def nw_rowcol_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_diag_64.argtypes = _argtypes
_lib.parasail_nw_rowcol_diag_64.restype = c_result_p
def nw_rowcol_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_diag_32.argtypes = _argtypes
_lib.parasail_nw_rowcol_diag_32.restype = c_result_p
def nw_rowcol_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_diag_16.argtypes = _argtypes
_lib.parasail_nw_rowcol_diag_16.restype = c_result_p
def nw_rowcol_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_diag_8.argtypes = _argtypes
_lib.parasail_nw_rowcol_diag_8.restype = c_result_p
def nw_rowcol_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_rowcol_diag_sat.argtypes = _argtypes
_lib.parasail_nw_rowcol_diag_sat.restype = c_result_p
def nw_rowcol_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_rowcol_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_scan_64.argtypes = _argtypes
_lib.parasail_nw_stats_scan_64.restype = c_result_p
def nw_stats_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_scan_32.argtypes = _argtypes
_lib.parasail_nw_stats_scan_32.restype = c_result_p
def nw_stats_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_scan_16.argtypes = _argtypes
_lib.parasail_nw_stats_scan_16.restype = c_result_p
def nw_stats_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_scan_8.argtypes = _argtypes
_lib.parasail_nw_stats_scan_8.restype = c_result_p
def nw_stats_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_scan_sat.argtypes = _argtypes
_lib.parasail_nw_stats_scan_sat.restype = c_result_p
def nw_stats_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_striped_64.argtypes = _argtypes
_lib.parasail_nw_stats_striped_64.restype = c_result_p
def nw_stats_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_striped_32.argtypes = _argtypes
_lib.parasail_nw_stats_striped_32.restype = c_result_p
def nw_stats_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_striped_16.argtypes = _argtypes
_lib.parasail_nw_stats_striped_16.restype = c_result_p
def nw_stats_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_striped_8.argtypes = _argtypes
_lib.parasail_nw_stats_striped_8.restype = c_result_p
def nw_stats_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_striped_sat.argtypes = _argtypes
_lib.parasail_nw_stats_striped_sat.restype = c_result_p
def nw_stats_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_diag_64.argtypes = _argtypes
_lib.parasail_nw_stats_diag_64.restype = c_result_p
def nw_stats_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_diag_32.argtypes = _argtypes
_lib.parasail_nw_stats_diag_32.restype = c_result_p
def nw_stats_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_diag_16.argtypes = _argtypes
_lib.parasail_nw_stats_diag_16.restype = c_result_p
def nw_stats_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_diag_8.argtypes = _argtypes
_lib.parasail_nw_stats_diag_8.restype = c_result_p
def nw_stats_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_diag_sat.argtypes = _argtypes
_lib.parasail_nw_stats_diag_sat.restype = c_result_p
def nw_stats_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_scan_64.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan_64.restype = c_result_p
def nw_stats_table_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_scan_32.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan_32.restype = c_result_p
def nw_stats_table_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_scan_16.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan_16.restype = c_result_p
def nw_stats_table_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_scan_8.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan_8.restype = c_result_p
def nw_stats_table_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_scan_sat.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan_sat.restype = c_result_p
def nw_stats_table_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_striped_64.argtypes = _argtypes
_lib.parasail_nw_stats_table_striped_64.restype = c_result_p
def nw_stats_table_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_striped_32.argtypes = _argtypes
_lib.parasail_nw_stats_table_striped_32.restype = c_result_p
def nw_stats_table_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_striped_16.argtypes = _argtypes
_lib.parasail_nw_stats_table_striped_16.restype = c_result_p
def nw_stats_table_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_striped_8.argtypes = _argtypes
_lib.parasail_nw_stats_table_striped_8.restype = c_result_p
def nw_stats_table_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_striped_sat.argtypes = _argtypes
_lib.parasail_nw_stats_table_striped_sat.restype = c_result_p
def nw_stats_table_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_diag_64.argtypes = _argtypes
_lib.parasail_nw_stats_table_diag_64.restype = c_result_p
def nw_stats_table_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_diag_32.argtypes = _argtypes
_lib.parasail_nw_stats_table_diag_32.restype = c_result_p
def nw_stats_table_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_diag_16.argtypes = _argtypes
_lib.parasail_nw_stats_table_diag_16.restype = c_result_p
def nw_stats_table_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_diag_8.argtypes = _argtypes
_lib.parasail_nw_stats_table_diag_8.restype = c_result_p
def nw_stats_table_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_table_diag_sat.argtypes = _argtypes
_lib.parasail_nw_stats_table_diag_sat.restype = c_result_p
def nw_stats_table_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_table_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_scan_64.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan_64.restype = c_result_p
def nw_stats_rowcol_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_scan_32.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan_32.restype = c_result_p
def nw_stats_rowcol_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_scan_16.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan_16.restype = c_result_p
def nw_stats_rowcol_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_scan_8.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan_8.restype = c_result_p
def nw_stats_rowcol_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_scan_sat.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan_sat.restype = c_result_p
def nw_stats_rowcol_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_striped_64.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_striped_64.restype = c_result_p
def nw_stats_rowcol_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_striped_32.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_striped_32.restype = c_result_p
def nw_stats_rowcol_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_striped_16.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_striped_16.restype = c_result_p
def nw_stats_rowcol_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_striped_8.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_striped_8.restype = c_result_p
def nw_stats_rowcol_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_striped_sat.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_striped_sat.restype = c_result_p
def nw_stats_rowcol_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_diag_64.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_diag_64.restype = c_result_p
def nw_stats_rowcol_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_diag_32.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_diag_32.restype = c_result_p
def nw_stats_rowcol_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_diag_16.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_diag_16.restype = c_result_p
def nw_stats_rowcol_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_diag_8.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_diag_8.restype = c_result_p
def nw_stats_rowcol_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_nw_stats_rowcol_diag_sat.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_diag_sat.restype = c_result_p
def nw_stats_rowcol_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_nw_stats_rowcol_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_scan_64.argtypes = _argtypes
_lib.parasail_sg_scan_64.restype = c_result_p
def sg_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_scan_32.argtypes = _argtypes
_lib.parasail_sg_scan_32.restype = c_result_p
def sg_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_scan_16.argtypes = _argtypes
_lib.parasail_sg_scan_16.restype = c_result_p
def sg_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_scan_8.argtypes = _argtypes
_lib.parasail_sg_scan_8.restype = c_result_p
def sg_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_scan_sat.argtypes = _argtypes
_lib.parasail_sg_scan_sat.restype = c_result_p
def sg_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_striped_64.argtypes = _argtypes
_lib.parasail_sg_striped_64.restype = c_result_p
def sg_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_striped_32.argtypes = _argtypes
_lib.parasail_sg_striped_32.restype = c_result_p
def sg_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_striped_16.argtypes = _argtypes
_lib.parasail_sg_striped_16.restype = c_result_p
def sg_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_striped_8.argtypes = _argtypes
_lib.parasail_sg_striped_8.restype = c_result_p
def sg_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_striped_sat.argtypes = _argtypes
_lib.parasail_sg_striped_sat.restype = c_result_p
def sg_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_diag_64.argtypes = _argtypes
_lib.parasail_sg_diag_64.restype = c_result_p
def sg_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_diag_32.argtypes = _argtypes
_lib.parasail_sg_diag_32.restype = c_result_p
def sg_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_diag_16.argtypes = _argtypes
_lib.parasail_sg_diag_16.restype = c_result_p
def sg_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_diag_8.argtypes = _argtypes
_lib.parasail_sg_diag_8.restype = c_result_p
def sg_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_diag_sat.argtypes = _argtypes
_lib.parasail_sg_diag_sat.restype = c_result_p
def sg_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_scan_64.argtypes = _argtypes
_lib.parasail_sg_table_scan_64.restype = c_result_p
def sg_table_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_scan_32.argtypes = _argtypes
_lib.parasail_sg_table_scan_32.restype = c_result_p
def sg_table_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_scan_16.argtypes = _argtypes
_lib.parasail_sg_table_scan_16.restype = c_result_p
def sg_table_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_scan_8.argtypes = _argtypes
_lib.parasail_sg_table_scan_8.restype = c_result_p
def sg_table_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_scan_sat.argtypes = _argtypes
_lib.parasail_sg_table_scan_sat.restype = c_result_p
def sg_table_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_striped_64.argtypes = _argtypes
_lib.parasail_sg_table_striped_64.restype = c_result_p
def sg_table_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_striped_32.argtypes = _argtypes
_lib.parasail_sg_table_striped_32.restype = c_result_p
def sg_table_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_striped_16.argtypes = _argtypes
_lib.parasail_sg_table_striped_16.restype = c_result_p
def sg_table_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_striped_8.argtypes = _argtypes
_lib.parasail_sg_table_striped_8.restype = c_result_p
def sg_table_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_striped_sat.argtypes = _argtypes
_lib.parasail_sg_table_striped_sat.restype = c_result_p
def sg_table_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_diag_64.argtypes = _argtypes
_lib.parasail_sg_table_diag_64.restype = c_result_p
def sg_table_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_diag_32.argtypes = _argtypes
_lib.parasail_sg_table_diag_32.restype = c_result_p
def sg_table_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_diag_16.argtypes = _argtypes
_lib.parasail_sg_table_diag_16.restype = c_result_p
def sg_table_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_diag_8.argtypes = _argtypes
_lib.parasail_sg_table_diag_8.restype = c_result_p
def sg_table_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_table_diag_sat.argtypes = _argtypes
_lib.parasail_sg_table_diag_sat.restype = c_result_p
def sg_table_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_table_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_scan_64.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan_64.restype = c_result_p
def sg_rowcol_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_scan_32.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan_32.restype = c_result_p
def sg_rowcol_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_scan_16.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan_16.restype = c_result_p
def sg_rowcol_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_scan_8.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan_8.restype = c_result_p
def sg_rowcol_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_scan_sat.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan_sat.restype = c_result_p
def sg_rowcol_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_striped_64.argtypes = _argtypes
_lib.parasail_sg_rowcol_striped_64.restype = c_result_p
def sg_rowcol_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_striped_32.argtypes = _argtypes
_lib.parasail_sg_rowcol_striped_32.restype = c_result_p
def sg_rowcol_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_striped_16.argtypes = _argtypes
_lib.parasail_sg_rowcol_striped_16.restype = c_result_p
def sg_rowcol_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_striped_8.argtypes = _argtypes
_lib.parasail_sg_rowcol_striped_8.restype = c_result_p
def sg_rowcol_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_striped_sat.argtypes = _argtypes
_lib.parasail_sg_rowcol_striped_sat.restype = c_result_p
def sg_rowcol_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_diag_64.argtypes = _argtypes
_lib.parasail_sg_rowcol_diag_64.restype = c_result_p
def sg_rowcol_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_diag_32.argtypes = _argtypes
_lib.parasail_sg_rowcol_diag_32.restype = c_result_p
def sg_rowcol_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_diag_16.argtypes = _argtypes
_lib.parasail_sg_rowcol_diag_16.restype = c_result_p
def sg_rowcol_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_diag_8.argtypes = _argtypes
_lib.parasail_sg_rowcol_diag_8.restype = c_result_p
def sg_rowcol_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_rowcol_diag_sat.argtypes = _argtypes
_lib.parasail_sg_rowcol_diag_sat.restype = c_result_p
def sg_rowcol_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_rowcol_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_scan_64.argtypes = _argtypes
_lib.parasail_sg_stats_scan_64.restype = c_result_p
def sg_stats_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_scan_32.argtypes = _argtypes
_lib.parasail_sg_stats_scan_32.restype = c_result_p
def sg_stats_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_scan_16.argtypes = _argtypes
_lib.parasail_sg_stats_scan_16.restype = c_result_p
def sg_stats_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_scan_8.argtypes = _argtypes
_lib.parasail_sg_stats_scan_8.restype = c_result_p
def sg_stats_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_scan_sat.argtypes = _argtypes
_lib.parasail_sg_stats_scan_sat.restype = c_result_p
def sg_stats_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_striped_64.argtypes = _argtypes
_lib.parasail_sg_stats_striped_64.restype = c_result_p
def sg_stats_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_striped_32.argtypes = _argtypes
_lib.parasail_sg_stats_striped_32.restype = c_result_p
def sg_stats_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_striped_16.argtypes = _argtypes
_lib.parasail_sg_stats_striped_16.restype = c_result_p
def sg_stats_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_striped_8.argtypes = _argtypes
_lib.parasail_sg_stats_striped_8.restype = c_result_p
def sg_stats_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_striped_sat.argtypes = _argtypes
_lib.parasail_sg_stats_striped_sat.restype = c_result_p
def sg_stats_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_diag_64.argtypes = _argtypes
_lib.parasail_sg_stats_diag_64.restype = c_result_p
def sg_stats_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_diag_32.argtypes = _argtypes
_lib.parasail_sg_stats_diag_32.restype = c_result_p
def sg_stats_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_diag_16.argtypes = _argtypes
_lib.parasail_sg_stats_diag_16.restype = c_result_p
def sg_stats_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_diag_8.argtypes = _argtypes
_lib.parasail_sg_stats_diag_8.restype = c_result_p
def sg_stats_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_diag_sat.argtypes = _argtypes
_lib.parasail_sg_stats_diag_sat.restype = c_result_p
def sg_stats_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_scan_64.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan_64.restype = c_result_p
def sg_stats_table_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_scan_32.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan_32.restype = c_result_p
def sg_stats_table_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_scan_16.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan_16.restype = c_result_p
def sg_stats_table_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_scan_8.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan_8.restype = c_result_p
def sg_stats_table_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_scan_sat.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan_sat.restype = c_result_p
def sg_stats_table_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_striped_64.argtypes = _argtypes
_lib.parasail_sg_stats_table_striped_64.restype = c_result_p
def sg_stats_table_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_striped_32.argtypes = _argtypes
_lib.parasail_sg_stats_table_striped_32.restype = c_result_p
def sg_stats_table_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_striped_16.argtypes = _argtypes
_lib.parasail_sg_stats_table_striped_16.restype = c_result_p
def sg_stats_table_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_striped_8.argtypes = _argtypes
_lib.parasail_sg_stats_table_striped_8.restype = c_result_p
def sg_stats_table_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_striped_sat.argtypes = _argtypes
_lib.parasail_sg_stats_table_striped_sat.restype = c_result_p
def sg_stats_table_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_diag_64.argtypes = _argtypes
_lib.parasail_sg_stats_table_diag_64.restype = c_result_p
def sg_stats_table_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_diag_32.argtypes = _argtypes
_lib.parasail_sg_stats_table_diag_32.restype = c_result_p
def sg_stats_table_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_diag_16.argtypes = _argtypes
_lib.parasail_sg_stats_table_diag_16.restype = c_result_p
def sg_stats_table_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_diag_8.argtypes = _argtypes
_lib.parasail_sg_stats_table_diag_8.restype = c_result_p
def sg_stats_table_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_table_diag_sat.argtypes = _argtypes
_lib.parasail_sg_stats_table_diag_sat.restype = c_result_p
def sg_stats_table_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_table_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_scan_64.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan_64.restype = c_result_p
def sg_stats_rowcol_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_scan_32.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan_32.restype = c_result_p
def sg_stats_rowcol_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_scan_16.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan_16.restype = c_result_p
def sg_stats_rowcol_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_scan_8.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan_8.restype = c_result_p
def sg_stats_rowcol_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_scan_sat.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan_sat.restype = c_result_p
def sg_stats_rowcol_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_striped_64.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_striped_64.restype = c_result_p
def sg_stats_rowcol_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_striped_32.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_striped_32.restype = c_result_p
def sg_stats_rowcol_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_striped_16.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_striped_16.restype = c_result_p
def sg_stats_rowcol_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_striped_8.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_striped_8.restype = c_result_p
def sg_stats_rowcol_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_striped_sat.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_striped_sat.restype = c_result_p
def sg_stats_rowcol_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_diag_64.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_diag_64.restype = c_result_p
def sg_stats_rowcol_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_diag_32.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_diag_32.restype = c_result_p
def sg_stats_rowcol_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_diag_16.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_diag_16.restype = c_result_p
def sg_stats_rowcol_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_diag_8.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_diag_8.restype = c_result_p
def sg_stats_rowcol_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sg_stats_rowcol_diag_sat.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_diag_sat.restype = c_result_p
def sg_stats_rowcol_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sg_stats_rowcol_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_scan_64.argtypes = _argtypes
_lib.parasail_sw_scan_64.restype = c_result_p
def sw_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_scan_32.argtypes = _argtypes
_lib.parasail_sw_scan_32.restype = c_result_p
def sw_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_scan_16.argtypes = _argtypes
_lib.parasail_sw_scan_16.restype = c_result_p
def sw_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_scan_8.argtypes = _argtypes
_lib.parasail_sw_scan_8.restype = c_result_p
def sw_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_scan_sat.argtypes = _argtypes
_lib.parasail_sw_scan_sat.restype = c_result_p
def sw_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_striped_64.argtypes = _argtypes
_lib.parasail_sw_striped_64.restype = c_result_p
def sw_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_striped_32.argtypes = _argtypes
_lib.parasail_sw_striped_32.restype = c_result_p
def sw_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_striped_16.argtypes = _argtypes
_lib.parasail_sw_striped_16.restype = c_result_p
def sw_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_striped_8.argtypes = _argtypes
_lib.parasail_sw_striped_8.restype = c_result_p
def sw_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_striped_sat.argtypes = _argtypes
_lib.parasail_sw_striped_sat.restype = c_result_p
def sw_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_diag_64.argtypes = _argtypes
_lib.parasail_sw_diag_64.restype = c_result_p
def sw_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_diag_32.argtypes = _argtypes
_lib.parasail_sw_diag_32.restype = c_result_p
def sw_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_diag_16.argtypes = _argtypes
_lib.parasail_sw_diag_16.restype = c_result_p
def sw_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_diag_8.argtypes = _argtypes
_lib.parasail_sw_diag_8.restype = c_result_p
def sw_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_diag_sat.argtypes = _argtypes
_lib.parasail_sw_diag_sat.restype = c_result_p
def sw_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_scan_64.argtypes = _argtypes
_lib.parasail_sw_table_scan_64.restype = c_result_p
def sw_table_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_scan_32.argtypes = _argtypes
_lib.parasail_sw_table_scan_32.restype = c_result_p
def sw_table_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_scan_16.argtypes = _argtypes
_lib.parasail_sw_table_scan_16.restype = c_result_p
def sw_table_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_scan_8.argtypes = _argtypes
_lib.parasail_sw_table_scan_8.restype = c_result_p
def sw_table_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_scan_sat.argtypes = _argtypes
_lib.parasail_sw_table_scan_sat.restype = c_result_p
def sw_table_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_striped_64.argtypes = _argtypes
_lib.parasail_sw_table_striped_64.restype = c_result_p
def sw_table_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_striped_32.argtypes = _argtypes
_lib.parasail_sw_table_striped_32.restype = c_result_p
def sw_table_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_striped_16.argtypes = _argtypes
_lib.parasail_sw_table_striped_16.restype = c_result_p
def sw_table_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_striped_8.argtypes = _argtypes
_lib.parasail_sw_table_striped_8.restype = c_result_p
def sw_table_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_striped_sat.argtypes = _argtypes
_lib.parasail_sw_table_striped_sat.restype = c_result_p
def sw_table_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_diag_64.argtypes = _argtypes
_lib.parasail_sw_table_diag_64.restype = c_result_p
def sw_table_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_diag_32.argtypes = _argtypes
_lib.parasail_sw_table_diag_32.restype = c_result_p
def sw_table_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_diag_16.argtypes = _argtypes
_lib.parasail_sw_table_diag_16.restype = c_result_p
def sw_table_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_diag_8.argtypes = _argtypes
_lib.parasail_sw_table_diag_8.restype = c_result_p
def sw_table_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_table_diag_sat.argtypes = _argtypes
_lib.parasail_sw_table_diag_sat.restype = c_result_p
def sw_table_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_table_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_scan_64.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan_64.restype = c_result_p
def sw_rowcol_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_scan_32.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan_32.restype = c_result_p
def sw_rowcol_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_scan_16.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan_16.restype = c_result_p
def sw_rowcol_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_scan_8.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan_8.restype = c_result_p
def sw_rowcol_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_scan_sat.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan_sat.restype = c_result_p
def sw_rowcol_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_striped_64.argtypes = _argtypes
_lib.parasail_sw_rowcol_striped_64.restype = c_result_p
def sw_rowcol_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_striped_32.argtypes = _argtypes
_lib.parasail_sw_rowcol_striped_32.restype = c_result_p
def sw_rowcol_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_striped_16.argtypes = _argtypes
_lib.parasail_sw_rowcol_striped_16.restype = c_result_p
def sw_rowcol_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_striped_8.argtypes = _argtypes
_lib.parasail_sw_rowcol_striped_8.restype = c_result_p
def sw_rowcol_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_striped_sat.argtypes = _argtypes
_lib.parasail_sw_rowcol_striped_sat.restype = c_result_p
def sw_rowcol_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_diag_64.argtypes = _argtypes
_lib.parasail_sw_rowcol_diag_64.restype = c_result_p
def sw_rowcol_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_diag_32.argtypes = _argtypes
_lib.parasail_sw_rowcol_diag_32.restype = c_result_p
def sw_rowcol_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_diag_16.argtypes = _argtypes
_lib.parasail_sw_rowcol_diag_16.restype = c_result_p
def sw_rowcol_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_diag_8.argtypes = _argtypes
_lib.parasail_sw_rowcol_diag_8.restype = c_result_p
def sw_rowcol_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_rowcol_diag_sat.argtypes = _argtypes
_lib.parasail_sw_rowcol_diag_sat.restype = c_result_p
def sw_rowcol_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_rowcol_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_scan_64.argtypes = _argtypes
_lib.parasail_sw_stats_scan_64.restype = c_result_p
def sw_stats_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_scan_32.argtypes = _argtypes
_lib.parasail_sw_stats_scan_32.restype = c_result_p
def sw_stats_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_scan_16.argtypes = _argtypes
_lib.parasail_sw_stats_scan_16.restype = c_result_p
def sw_stats_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_scan_8.argtypes = _argtypes
_lib.parasail_sw_stats_scan_8.restype = c_result_p
def sw_stats_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_scan_sat.argtypes = _argtypes
_lib.parasail_sw_stats_scan_sat.restype = c_result_p
def sw_stats_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_striped_64.argtypes = _argtypes
_lib.parasail_sw_stats_striped_64.restype = c_result_p
def sw_stats_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_striped_32.argtypes = _argtypes
_lib.parasail_sw_stats_striped_32.restype = c_result_p
def sw_stats_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_striped_16.argtypes = _argtypes
_lib.parasail_sw_stats_striped_16.restype = c_result_p
def sw_stats_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_striped_8.argtypes = _argtypes
_lib.parasail_sw_stats_striped_8.restype = c_result_p
def sw_stats_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_striped_sat.argtypes = _argtypes
_lib.parasail_sw_stats_striped_sat.restype = c_result_p
def sw_stats_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_diag_64.argtypes = _argtypes
_lib.parasail_sw_stats_diag_64.restype = c_result_p
def sw_stats_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_diag_32.argtypes = _argtypes
_lib.parasail_sw_stats_diag_32.restype = c_result_p
def sw_stats_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_diag_16.argtypes = _argtypes
_lib.parasail_sw_stats_diag_16.restype = c_result_p
def sw_stats_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_diag_8.argtypes = _argtypes
_lib.parasail_sw_stats_diag_8.restype = c_result_p
def sw_stats_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_diag_sat.argtypes = _argtypes
_lib.parasail_sw_stats_diag_sat.restype = c_result_p
def sw_stats_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_scan_64.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan_64.restype = c_result_p
def sw_stats_table_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_scan_32.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan_32.restype = c_result_p
def sw_stats_table_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_scan_16.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan_16.restype = c_result_p
def sw_stats_table_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_scan_8.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan_8.restype = c_result_p
def sw_stats_table_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_scan_sat.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan_sat.restype = c_result_p
def sw_stats_table_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_striped_64.argtypes = _argtypes
_lib.parasail_sw_stats_table_striped_64.restype = c_result_p
def sw_stats_table_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_striped_32.argtypes = _argtypes
_lib.parasail_sw_stats_table_striped_32.restype = c_result_p
def sw_stats_table_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_striped_16.argtypes = _argtypes
_lib.parasail_sw_stats_table_striped_16.restype = c_result_p
def sw_stats_table_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_striped_8.argtypes = _argtypes
_lib.parasail_sw_stats_table_striped_8.restype = c_result_p
def sw_stats_table_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_striped_sat.argtypes = _argtypes
_lib.parasail_sw_stats_table_striped_sat.restype = c_result_p
def sw_stats_table_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_diag_64.argtypes = _argtypes
_lib.parasail_sw_stats_table_diag_64.restype = c_result_p
def sw_stats_table_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_diag_32.argtypes = _argtypes
_lib.parasail_sw_stats_table_diag_32.restype = c_result_p
def sw_stats_table_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_diag_16.argtypes = _argtypes
_lib.parasail_sw_stats_table_diag_16.restype = c_result_p
def sw_stats_table_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_diag_8.argtypes = _argtypes
_lib.parasail_sw_stats_table_diag_8.restype = c_result_p
def sw_stats_table_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_table_diag_sat.argtypes = _argtypes
_lib.parasail_sw_stats_table_diag_sat.restype = c_result_p
def sw_stats_table_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_table_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_scan_64.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan_64.restype = c_result_p
def sw_stats_rowcol_scan_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_scan_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_scan_32.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan_32.restype = c_result_p
def sw_stats_rowcol_scan_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_scan_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_scan_16.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan_16.restype = c_result_p
def sw_stats_rowcol_scan_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_scan_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_scan_8.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan_8.restype = c_result_p
def sw_stats_rowcol_scan_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_scan_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_scan_sat.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan_sat.restype = c_result_p
def sw_stats_rowcol_scan_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_scan_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_striped_64.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_striped_64.restype = c_result_p
def sw_stats_rowcol_striped_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_striped_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_striped_32.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_striped_32.restype = c_result_p
def sw_stats_rowcol_striped_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_striped_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_striped_16.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_striped_16.restype = c_result_p
def sw_stats_rowcol_striped_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_striped_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_striped_8.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_striped_8.restype = c_result_p
def sw_stats_rowcol_striped_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_striped_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_striped_sat.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_striped_sat.restype = c_result_p
def sw_stats_rowcol_striped_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_striped_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_diag_64.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_diag_64.restype = c_result_p
def sw_stats_rowcol_diag_64(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_diag_64(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_diag_32.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_diag_32.restype = c_result_p
def sw_stats_rowcol_diag_32(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_diag_32(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_diag_16.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_diag_16.restype = c_result_p
def sw_stats_rowcol_diag_16(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_diag_16(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_diag_8.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_diag_8.restype = c_result_p
def sw_stats_rowcol_diag_8(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_diag_8(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_lib.parasail_sw_stats_rowcol_diag_sat.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_diag_sat.restype = c_result_p
def sw_stats_rowcol_diag_sat(s1, s2, open, extend, matrix):
    return Result(_lib.parasail_sw_stats_rowcol_diag_sat(
        s1, len(s1), s2, len(s2), open, extend, matrix),
        len(s1), len(s2))

_argtypes = [c_profile_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]


_lib.parasail_nw_scan_profile_64.argtypes = _argtypes
_lib.parasail_nw_scan_profile_64.restype = c_result_p
def nw_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_scan_profile_32.argtypes = _argtypes
_lib.parasail_nw_scan_profile_32.restype = c_result_p
def nw_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_scan_profile_16.argtypes = _argtypes
_lib.parasail_nw_scan_profile_16.restype = c_result_p
def nw_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_scan_profile_8.argtypes = _argtypes
_lib.parasail_nw_scan_profile_8.restype = c_result_p
def nw_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_scan_profile_sat.argtypes = _argtypes
_lib.parasail_nw_scan_profile_sat.restype = c_result_p
def nw_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_striped_profile_64.argtypes = _argtypes
_lib.parasail_nw_striped_profile_64.restype = c_result_p
def nw_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_striped_profile_32.argtypes = _argtypes
_lib.parasail_nw_striped_profile_32.restype = c_result_p
def nw_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_striped_profile_16.argtypes = _argtypes
_lib.parasail_nw_striped_profile_16.restype = c_result_p
def nw_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_striped_profile_8.argtypes = _argtypes
_lib.parasail_nw_striped_profile_8.restype = c_result_p
def nw_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_striped_profile_sat.argtypes = _argtypes
_lib.parasail_nw_striped_profile_sat.restype = c_result_p
def nw_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_table_scan_profile_64.argtypes = _argtypes
_lib.parasail_nw_table_scan_profile_64.restype = c_result_p
def nw_table_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_table_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_table_scan_profile_32.argtypes = _argtypes
_lib.parasail_nw_table_scan_profile_32.restype = c_result_p
def nw_table_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_table_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_table_scan_profile_16.argtypes = _argtypes
_lib.parasail_nw_table_scan_profile_16.restype = c_result_p
def nw_table_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_table_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_table_scan_profile_8.argtypes = _argtypes
_lib.parasail_nw_table_scan_profile_8.restype = c_result_p
def nw_table_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_table_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_table_scan_profile_sat.argtypes = _argtypes
_lib.parasail_nw_table_scan_profile_sat.restype = c_result_p
def nw_table_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_table_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_table_striped_profile_64.argtypes = _argtypes
_lib.parasail_nw_table_striped_profile_64.restype = c_result_p
def nw_table_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_table_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_table_striped_profile_32.argtypes = _argtypes
_lib.parasail_nw_table_striped_profile_32.restype = c_result_p
def nw_table_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_table_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_table_striped_profile_16.argtypes = _argtypes
_lib.parasail_nw_table_striped_profile_16.restype = c_result_p
def nw_table_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_table_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_table_striped_profile_8.argtypes = _argtypes
_lib.parasail_nw_table_striped_profile_8.restype = c_result_p
def nw_table_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_table_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_table_striped_profile_sat.argtypes = _argtypes
_lib.parasail_nw_table_striped_profile_sat.restype = c_result_p
def nw_table_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_table_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_rowcol_scan_profile_64.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan_profile_64.restype = c_result_p
def nw_rowcol_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_rowcol_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_rowcol_scan_profile_32.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan_profile_32.restype = c_result_p
def nw_rowcol_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_rowcol_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_rowcol_scan_profile_16.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan_profile_16.restype = c_result_p
def nw_rowcol_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_rowcol_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_rowcol_scan_profile_8.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan_profile_8.restype = c_result_p
def nw_rowcol_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_rowcol_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_rowcol_scan_profile_sat.argtypes = _argtypes
_lib.parasail_nw_rowcol_scan_profile_sat.restype = c_result_p
def nw_rowcol_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_rowcol_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_rowcol_striped_profile_64.argtypes = _argtypes
_lib.parasail_nw_rowcol_striped_profile_64.restype = c_result_p
def nw_rowcol_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_rowcol_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_rowcol_striped_profile_32.argtypes = _argtypes
_lib.parasail_nw_rowcol_striped_profile_32.restype = c_result_p
def nw_rowcol_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_rowcol_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_rowcol_striped_profile_16.argtypes = _argtypes
_lib.parasail_nw_rowcol_striped_profile_16.restype = c_result_p
def nw_rowcol_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_rowcol_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_rowcol_striped_profile_8.argtypes = _argtypes
_lib.parasail_nw_rowcol_striped_profile_8.restype = c_result_p
def nw_rowcol_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_rowcol_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_rowcol_striped_profile_sat.argtypes = _argtypes
_lib.parasail_nw_rowcol_striped_profile_sat.restype = c_result_p
def nw_rowcol_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_rowcol_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_scan_profile_64.argtypes = _argtypes
_lib.parasail_nw_stats_scan_profile_64.restype = c_result_p
def nw_stats_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_scan_profile_32.argtypes = _argtypes
_lib.parasail_nw_stats_scan_profile_32.restype = c_result_p
def nw_stats_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_scan_profile_16.argtypes = _argtypes
_lib.parasail_nw_stats_scan_profile_16.restype = c_result_p
def nw_stats_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_scan_profile_8.argtypes = _argtypes
_lib.parasail_nw_stats_scan_profile_8.restype = c_result_p
def nw_stats_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_scan_profile_sat.argtypes = _argtypes
_lib.parasail_nw_stats_scan_profile_sat.restype = c_result_p
def nw_stats_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_striped_profile_64.argtypes = _argtypes
_lib.parasail_nw_stats_striped_profile_64.restype = c_result_p
def nw_stats_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_striped_profile_32.argtypes = _argtypes
_lib.parasail_nw_stats_striped_profile_32.restype = c_result_p
def nw_stats_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_striped_profile_16.argtypes = _argtypes
_lib.parasail_nw_stats_striped_profile_16.restype = c_result_p
def nw_stats_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_striped_profile_8.argtypes = _argtypes
_lib.parasail_nw_stats_striped_profile_8.restype = c_result_p
def nw_stats_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_striped_profile_sat.argtypes = _argtypes
_lib.parasail_nw_stats_striped_profile_sat.restype = c_result_p
def nw_stats_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_table_scan_profile_64.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan_profile_64.restype = c_result_p
def nw_stats_table_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_table_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_table_scan_profile_32.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan_profile_32.restype = c_result_p
def nw_stats_table_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_table_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_table_scan_profile_16.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan_profile_16.restype = c_result_p
def nw_stats_table_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_table_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_table_scan_profile_8.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan_profile_8.restype = c_result_p
def nw_stats_table_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_table_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_table_scan_profile_sat.argtypes = _argtypes
_lib.parasail_nw_stats_table_scan_profile_sat.restype = c_result_p
def nw_stats_table_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_table_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_table_striped_profile_64.argtypes = _argtypes
_lib.parasail_nw_stats_table_striped_profile_64.restype = c_result_p
def nw_stats_table_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_table_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_table_striped_profile_32.argtypes = _argtypes
_lib.parasail_nw_stats_table_striped_profile_32.restype = c_result_p
def nw_stats_table_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_table_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_table_striped_profile_16.argtypes = _argtypes
_lib.parasail_nw_stats_table_striped_profile_16.restype = c_result_p
def nw_stats_table_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_table_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_table_striped_profile_8.argtypes = _argtypes
_lib.parasail_nw_stats_table_striped_profile_8.restype = c_result_p
def nw_stats_table_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_table_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_table_striped_profile_sat.argtypes = _argtypes
_lib.parasail_nw_stats_table_striped_profile_sat.restype = c_result_p
def nw_stats_table_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_table_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_rowcol_scan_profile_64.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan_profile_64.restype = c_result_p
def nw_stats_rowcol_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_rowcol_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_rowcol_scan_profile_32.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan_profile_32.restype = c_result_p
def nw_stats_rowcol_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_rowcol_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_rowcol_scan_profile_16.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan_profile_16.restype = c_result_p
def nw_stats_rowcol_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_rowcol_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_rowcol_scan_profile_8.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan_profile_8.restype = c_result_p
def nw_stats_rowcol_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_rowcol_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_rowcol_scan_profile_sat.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_scan_profile_sat.restype = c_result_p
def nw_stats_rowcol_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_rowcol_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_rowcol_striped_profile_64.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_striped_profile_64.restype = c_result_p
def nw_stats_rowcol_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_rowcol_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_rowcol_striped_profile_32.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_striped_profile_32.restype = c_result_p
def nw_stats_rowcol_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_rowcol_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_rowcol_striped_profile_16.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_striped_profile_16.restype = c_result_p
def nw_stats_rowcol_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_rowcol_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_rowcol_striped_profile_8.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_striped_profile_8.restype = c_result_p
def nw_stats_rowcol_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_rowcol_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_nw_stats_rowcol_striped_profile_sat.argtypes = _argtypes
_lib.parasail_nw_stats_rowcol_striped_profile_sat.restype = c_result_p
def nw_stats_rowcol_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_nw_stats_rowcol_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_scan_profile_64.argtypes = _argtypes
_lib.parasail_sg_scan_profile_64.restype = c_result_p
def sg_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_scan_profile_32.argtypes = _argtypes
_lib.parasail_sg_scan_profile_32.restype = c_result_p
def sg_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_scan_profile_16.argtypes = _argtypes
_lib.parasail_sg_scan_profile_16.restype = c_result_p
def sg_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_scan_profile_8.argtypes = _argtypes
_lib.parasail_sg_scan_profile_8.restype = c_result_p
def sg_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sg_scan_profile_sat.restype = c_result_p
def sg_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_striped_profile_64.argtypes = _argtypes
_lib.parasail_sg_striped_profile_64.restype = c_result_p
def sg_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_striped_profile_32.argtypes = _argtypes
_lib.parasail_sg_striped_profile_32.restype = c_result_p
def sg_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_striped_profile_16.argtypes = _argtypes
_lib.parasail_sg_striped_profile_16.restype = c_result_p
def sg_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_striped_profile_8.argtypes = _argtypes
_lib.parasail_sg_striped_profile_8.restype = c_result_p
def sg_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sg_striped_profile_sat.restype = c_result_p
def sg_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_table_scan_profile_64.argtypes = _argtypes
_lib.parasail_sg_table_scan_profile_64.restype = c_result_p
def sg_table_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_table_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_table_scan_profile_32.argtypes = _argtypes
_lib.parasail_sg_table_scan_profile_32.restype = c_result_p
def sg_table_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_table_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_table_scan_profile_16.argtypes = _argtypes
_lib.parasail_sg_table_scan_profile_16.restype = c_result_p
def sg_table_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_table_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_table_scan_profile_8.argtypes = _argtypes
_lib.parasail_sg_table_scan_profile_8.restype = c_result_p
def sg_table_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_table_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_table_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sg_table_scan_profile_sat.restype = c_result_p
def sg_table_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_table_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_table_striped_profile_64.argtypes = _argtypes
_lib.parasail_sg_table_striped_profile_64.restype = c_result_p
def sg_table_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_table_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_table_striped_profile_32.argtypes = _argtypes
_lib.parasail_sg_table_striped_profile_32.restype = c_result_p
def sg_table_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_table_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_table_striped_profile_16.argtypes = _argtypes
_lib.parasail_sg_table_striped_profile_16.restype = c_result_p
def sg_table_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_table_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_table_striped_profile_8.argtypes = _argtypes
_lib.parasail_sg_table_striped_profile_8.restype = c_result_p
def sg_table_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_table_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_table_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sg_table_striped_profile_sat.restype = c_result_p
def sg_table_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_table_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_rowcol_scan_profile_64.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan_profile_64.restype = c_result_p
def sg_rowcol_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_rowcol_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_rowcol_scan_profile_32.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan_profile_32.restype = c_result_p
def sg_rowcol_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_rowcol_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_rowcol_scan_profile_16.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan_profile_16.restype = c_result_p
def sg_rowcol_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_rowcol_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_rowcol_scan_profile_8.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan_profile_8.restype = c_result_p
def sg_rowcol_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_rowcol_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_rowcol_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sg_rowcol_scan_profile_sat.restype = c_result_p
def sg_rowcol_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_rowcol_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_rowcol_striped_profile_64.argtypes = _argtypes
_lib.parasail_sg_rowcol_striped_profile_64.restype = c_result_p
def sg_rowcol_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_rowcol_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_rowcol_striped_profile_32.argtypes = _argtypes
_lib.parasail_sg_rowcol_striped_profile_32.restype = c_result_p
def sg_rowcol_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_rowcol_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_rowcol_striped_profile_16.argtypes = _argtypes
_lib.parasail_sg_rowcol_striped_profile_16.restype = c_result_p
def sg_rowcol_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_rowcol_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_rowcol_striped_profile_8.argtypes = _argtypes
_lib.parasail_sg_rowcol_striped_profile_8.restype = c_result_p
def sg_rowcol_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_rowcol_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_rowcol_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sg_rowcol_striped_profile_sat.restype = c_result_p
def sg_rowcol_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_rowcol_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_scan_profile_64.argtypes = _argtypes
_lib.parasail_sg_stats_scan_profile_64.restype = c_result_p
def sg_stats_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_scan_profile_32.argtypes = _argtypes
_lib.parasail_sg_stats_scan_profile_32.restype = c_result_p
def sg_stats_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_scan_profile_16.argtypes = _argtypes
_lib.parasail_sg_stats_scan_profile_16.restype = c_result_p
def sg_stats_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_scan_profile_8.argtypes = _argtypes
_lib.parasail_sg_stats_scan_profile_8.restype = c_result_p
def sg_stats_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sg_stats_scan_profile_sat.restype = c_result_p
def sg_stats_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_striped_profile_64.argtypes = _argtypes
_lib.parasail_sg_stats_striped_profile_64.restype = c_result_p
def sg_stats_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_striped_profile_32.argtypes = _argtypes
_lib.parasail_sg_stats_striped_profile_32.restype = c_result_p
def sg_stats_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_striped_profile_16.argtypes = _argtypes
_lib.parasail_sg_stats_striped_profile_16.restype = c_result_p
def sg_stats_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_striped_profile_8.argtypes = _argtypes
_lib.parasail_sg_stats_striped_profile_8.restype = c_result_p
def sg_stats_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sg_stats_striped_profile_sat.restype = c_result_p
def sg_stats_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_table_scan_profile_64.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan_profile_64.restype = c_result_p
def sg_stats_table_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_table_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_table_scan_profile_32.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan_profile_32.restype = c_result_p
def sg_stats_table_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_table_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_table_scan_profile_16.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan_profile_16.restype = c_result_p
def sg_stats_table_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_table_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_table_scan_profile_8.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan_profile_8.restype = c_result_p
def sg_stats_table_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_table_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_table_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sg_stats_table_scan_profile_sat.restype = c_result_p
def sg_stats_table_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_table_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_table_striped_profile_64.argtypes = _argtypes
_lib.parasail_sg_stats_table_striped_profile_64.restype = c_result_p
def sg_stats_table_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_table_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_table_striped_profile_32.argtypes = _argtypes
_lib.parasail_sg_stats_table_striped_profile_32.restype = c_result_p
def sg_stats_table_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_table_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_table_striped_profile_16.argtypes = _argtypes
_lib.parasail_sg_stats_table_striped_profile_16.restype = c_result_p
def sg_stats_table_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_table_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_table_striped_profile_8.argtypes = _argtypes
_lib.parasail_sg_stats_table_striped_profile_8.restype = c_result_p
def sg_stats_table_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_table_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_table_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sg_stats_table_striped_profile_sat.restype = c_result_p
def sg_stats_table_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_table_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_rowcol_scan_profile_64.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan_profile_64.restype = c_result_p
def sg_stats_rowcol_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_rowcol_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_rowcol_scan_profile_32.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan_profile_32.restype = c_result_p
def sg_stats_rowcol_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_rowcol_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_rowcol_scan_profile_16.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan_profile_16.restype = c_result_p
def sg_stats_rowcol_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_rowcol_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_rowcol_scan_profile_8.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan_profile_8.restype = c_result_p
def sg_stats_rowcol_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_rowcol_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_rowcol_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_scan_profile_sat.restype = c_result_p
def sg_stats_rowcol_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_rowcol_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_rowcol_striped_profile_64.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_striped_profile_64.restype = c_result_p
def sg_stats_rowcol_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_rowcol_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_rowcol_striped_profile_32.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_striped_profile_32.restype = c_result_p
def sg_stats_rowcol_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_rowcol_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_rowcol_striped_profile_16.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_striped_profile_16.restype = c_result_p
def sg_stats_rowcol_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_rowcol_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_rowcol_striped_profile_8.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_striped_profile_8.restype = c_result_p
def sg_stats_rowcol_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_rowcol_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sg_stats_rowcol_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sg_stats_rowcol_striped_profile_sat.restype = c_result_p
def sg_stats_rowcol_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sg_stats_rowcol_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_scan_profile_64.argtypes = _argtypes
_lib.parasail_sw_scan_profile_64.restype = c_result_p
def sw_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_scan_profile_32.argtypes = _argtypes
_lib.parasail_sw_scan_profile_32.restype = c_result_p
def sw_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_scan_profile_16.argtypes = _argtypes
_lib.parasail_sw_scan_profile_16.restype = c_result_p
def sw_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_scan_profile_8.argtypes = _argtypes
_lib.parasail_sw_scan_profile_8.restype = c_result_p
def sw_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sw_scan_profile_sat.restype = c_result_p
def sw_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_striped_profile_64.argtypes = _argtypes
_lib.parasail_sw_striped_profile_64.restype = c_result_p
def sw_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_striped_profile_32.argtypes = _argtypes
_lib.parasail_sw_striped_profile_32.restype = c_result_p
def sw_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_striped_profile_16.argtypes = _argtypes
_lib.parasail_sw_striped_profile_16.restype = c_result_p
def sw_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_striped_profile_8.argtypes = _argtypes
_lib.parasail_sw_striped_profile_8.restype = c_result_p
def sw_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sw_striped_profile_sat.restype = c_result_p
def sw_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_table_scan_profile_64.argtypes = _argtypes
_lib.parasail_sw_table_scan_profile_64.restype = c_result_p
def sw_table_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_table_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_table_scan_profile_32.argtypes = _argtypes
_lib.parasail_sw_table_scan_profile_32.restype = c_result_p
def sw_table_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_table_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_table_scan_profile_16.argtypes = _argtypes
_lib.parasail_sw_table_scan_profile_16.restype = c_result_p
def sw_table_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_table_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_table_scan_profile_8.argtypes = _argtypes
_lib.parasail_sw_table_scan_profile_8.restype = c_result_p
def sw_table_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_table_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_table_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sw_table_scan_profile_sat.restype = c_result_p
def sw_table_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_table_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_table_striped_profile_64.argtypes = _argtypes
_lib.parasail_sw_table_striped_profile_64.restype = c_result_p
def sw_table_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_table_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_table_striped_profile_32.argtypes = _argtypes
_lib.parasail_sw_table_striped_profile_32.restype = c_result_p
def sw_table_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_table_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_table_striped_profile_16.argtypes = _argtypes
_lib.parasail_sw_table_striped_profile_16.restype = c_result_p
def sw_table_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_table_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_table_striped_profile_8.argtypes = _argtypes
_lib.parasail_sw_table_striped_profile_8.restype = c_result_p
def sw_table_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_table_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_table_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sw_table_striped_profile_sat.restype = c_result_p
def sw_table_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_table_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_rowcol_scan_profile_64.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan_profile_64.restype = c_result_p
def sw_rowcol_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_rowcol_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_rowcol_scan_profile_32.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan_profile_32.restype = c_result_p
def sw_rowcol_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_rowcol_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_rowcol_scan_profile_16.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan_profile_16.restype = c_result_p
def sw_rowcol_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_rowcol_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_rowcol_scan_profile_8.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan_profile_8.restype = c_result_p
def sw_rowcol_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_rowcol_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_rowcol_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sw_rowcol_scan_profile_sat.restype = c_result_p
def sw_rowcol_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_rowcol_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_rowcol_striped_profile_64.argtypes = _argtypes
_lib.parasail_sw_rowcol_striped_profile_64.restype = c_result_p
def sw_rowcol_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_rowcol_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_rowcol_striped_profile_32.argtypes = _argtypes
_lib.parasail_sw_rowcol_striped_profile_32.restype = c_result_p
def sw_rowcol_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_rowcol_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_rowcol_striped_profile_16.argtypes = _argtypes
_lib.parasail_sw_rowcol_striped_profile_16.restype = c_result_p
def sw_rowcol_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_rowcol_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_rowcol_striped_profile_8.argtypes = _argtypes
_lib.parasail_sw_rowcol_striped_profile_8.restype = c_result_p
def sw_rowcol_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_rowcol_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_rowcol_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sw_rowcol_striped_profile_sat.restype = c_result_p
def sw_rowcol_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_rowcol_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_scan_profile_64.argtypes = _argtypes
_lib.parasail_sw_stats_scan_profile_64.restype = c_result_p
def sw_stats_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_scan_profile_32.argtypes = _argtypes
_lib.parasail_sw_stats_scan_profile_32.restype = c_result_p
def sw_stats_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_scan_profile_16.argtypes = _argtypes
_lib.parasail_sw_stats_scan_profile_16.restype = c_result_p
def sw_stats_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_scan_profile_8.argtypes = _argtypes
_lib.parasail_sw_stats_scan_profile_8.restype = c_result_p
def sw_stats_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sw_stats_scan_profile_sat.restype = c_result_p
def sw_stats_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_striped_profile_64.argtypes = _argtypes
_lib.parasail_sw_stats_striped_profile_64.restype = c_result_p
def sw_stats_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_striped_profile_32.argtypes = _argtypes
_lib.parasail_sw_stats_striped_profile_32.restype = c_result_p
def sw_stats_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_striped_profile_16.argtypes = _argtypes
_lib.parasail_sw_stats_striped_profile_16.restype = c_result_p
def sw_stats_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_striped_profile_8.argtypes = _argtypes
_lib.parasail_sw_stats_striped_profile_8.restype = c_result_p
def sw_stats_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sw_stats_striped_profile_sat.restype = c_result_p
def sw_stats_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_table_scan_profile_64.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan_profile_64.restype = c_result_p
def sw_stats_table_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_table_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_table_scan_profile_32.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan_profile_32.restype = c_result_p
def sw_stats_table_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_table_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_table_scan_profile_16.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan_profile_16.restype = c_result_p
def sw_stats_table_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_table_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_table_scan_profile_8.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan_profile_8.restype = c_result_p
def sw_stats_table_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_table_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_table_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sw_stats_table_scan_profile_sat.restype = c_result_p
def sw_stats_table_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_table_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_table_striped_profile_64.argtypes = _argtypes
_lib.parasail_sw_stats_table_striped_profile_64.restype = c_result_p
def sw_stats_table_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_table_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_table_striped_profile_32.argtypes = _argtypes
_lib.parasail_sw_stats_table_striped_profile_32.restype = c_result_p
def sw_stats_table_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_table_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_table_striped_profile_16.argtypes = _argtypes
_lib.parasail_sw_stats_table_striped_profile_16.restype = c_result_p
def sw_stats_table_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_table_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_table_striped_profile_8.argtypes = _argtypes
_lib.parasail_sw_stats_table_striped_profile_8.restype = c_result_p
def sw_stats_table_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_table_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_table_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sw_stats_table_striped_profile_sat.restype = c_result_p
def sw_stats_table_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_table_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_rowcol_scan_profile_64.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan_profile_64.restype = c_result_p
def sw_stats_rowcol_scan_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_rowcol_scan_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_rowcol_scan_profile_32.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan_profile_32.restype = c_result_p
def sw_stats_rowcol_scan_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_rowcol_scan_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_rowcol_scan_profile_16.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan_profile_16.restype = c_result_p
def sw_stats_rowcol_scan_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_rowcol_scan_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_rowcol_scan_profile_8.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan_profile_8.restype = c_result_p
def sw_stats_rowcol_scan_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_rowcol_scan_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_rowcol_scan_profile_sat.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_scan_profile_sat.restype = c_result_p
def sw_stats_rowcol_scan_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_rowcol_scan_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_rowcol_striped_profile_64.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_striped_profile_64.restype = c_result_p
def sw_stats_rowcol_striped_profile_64(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_rowcol_striped_profile_64(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_rowcol_striped_profile_32.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_striped_profile_32.restype = c_result_p
def sw_stats_rowcol_striped_profile_32(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_rowcol_striped_profile_32(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_rowcol_striped_profile_16.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_striped_profile_16.restype = c_result_p
def sw_stats_rowcol_striped_profile_16(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_rowcol_striped_profile_16(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_rowcol_striped_profile_8.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_striped_profile_8.restype = c_result_p
def sw_stats_rowcol_striped_profile_8(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_rowcol_striped_profile_8(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))

_lib.parasail_sw_stats_rowcol_striped_profile_sat.argtypes = _argtypes
_lib.parasail_sw_stats_rowcol_striped_profile_sat.restype = c_result_p
def sw_stats_rowcol_striped_profile_sat(profile, s2, open, extend):
    return Result(_lib.parasail_sw_stats_rowcol_striped_profile_sat(
        profile, s2, len(s2), open, extend),
        profile.s1Len, len(s2))