
# B/c the module is not compiled we can import the current version
from sys import path
from os.path import join, exists, dirname
path.insert(0, join(dirname(__file__),'..'))

import pytest
import numpy as np
from mffpy.raw_bin_files import RawBinFile, SEEK_END, SEEK_BEGIN, SEEK_RELATIVE

PATH = join(dirname(__file__), '..', 'examples', 'example_1.mff')

@pytest.fixture
def rawbin():
    ans = join(PATH, 'signal1.bin')
    assert exists(ans), ans
    return RawBinFile(ans)

def test_close(rawbin):
    f = rawbin.file
    rawbin.close()
    assert rawbin.file.closed

def test_tell(rawbin):
    rawbin.file.seek(10)
    assert rawbin.tell() == 10

def test_seek(rawbin):
    rawbin.seek(10, SEEK_BEGIN)
    assert rawbin.tell() == 10
    rawbin.seek(10, SEEK_RELATIVE)
    assert rawbin.tell() == 20
    rawbin.seek(-10, SEEK_END)
    assert rawbin.tell() == rawbin.bytes_in_file-10

def test_read(rawbin):
    r = rawbin.read('4i')
    assert all(ri == exp for ri, exp in zip(r,[1, 2100, 55512, 257]))

@pytest.mark.parametrize("prop,expected", [
    ('bytes_in_file', 4270376),
    ('num_channels', 257),
    ('sampling_rate', 250.0),
    ('duration', 16.6),
])
def test_property(prop, expected, rawbin):
    assert getattr(rawbin, prop) == expected

@pytest.mark.parametrize("attr,expected", [
   ('num_channels', 257),
   ('sampling_rate', 250.0),
   ('n_blocks', 2),
   ('num_samples_by_block', [54, 4096]),
   ('header_sizes', [2100, 2076]),
])
def test_signal_blocks(attr, expected, rawbin):
    val = rawbin.signal_blocks[attr]
    if isinstance(val, list):
        assert all(v==e for v, e in zip(val, expected))
    else:
        assert val == expected

def test_read_raw_samples(rawbin):
    vals = rawbin.read_raw_samples(1.0, 1.0)[:3,:3]
    expected = np.array([
      [-14.11438,    -9.307861,    0.15258789],
      [-18.005371,  -13.2751465,  -4.348755  ],
      [-19.14978,   -13.35144,    -2.746582  ]
    ], dtype=np.float32)
    assert all([v == e for v, e in zip(vals.flatten(), expected.flatten())])