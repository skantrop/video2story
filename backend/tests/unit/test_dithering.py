import numpy as np
from app.pipeline.extract import bayer_dither_4x4

def test_bayer_dither_output_shape():
    img = np.random.randint(0, 256, (8, 8), dtype=np.uint8)

    result = bayer_dither_4x4(img)

    assert result.shape == img.shape
    assert result.dtype == np.uint8
    assert set(np.unique(result)).issubset({0, 255})