from pathlib import Path
from app.pipeline.extract import _sorted_frame_files

def test_sorted_frame_files(tmp_path):
    # create fake files
    (tmp_path / "frame10.jpg").touch()
    (tmp_path / "frame2.jpg").touch()
    (tmp_path / "frame1.jpg").touch()

    result = _sorted_frame_files(tmp_path, "jpg")

    names = [p.name for p in result]
    assert names == ["frame1.jpg", "frame2.jpg", "frame10.jpg"]