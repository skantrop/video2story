import numpy as np
from pathlib import Path
from app.pipeline.extract import _process_frame, SnapshotConfig

def test_process_frame_resize(mocker, tmp_path):
    fake_img = np.ones((100, 200, 3), dtype=np.uint8)

    mocker.patch("cv2.imread", return_value=fake_img)
    mocker.patch("cv2.imwrite", return_value=True)

    cfg = SnapshotConfig(
        job_id="1",
        image_format="jpg",
        sampling_fps=1,
        resize_width=100,
        black_white=False,
    )

    path = tmp_path / "frame.jpg"
    path.touch()

    width, height = _process_frame(path, cfg)

    assert width == 100
    assert height > 0