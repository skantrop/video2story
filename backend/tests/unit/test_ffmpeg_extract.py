from pathlib import Path
from app.pipeline.extract import _run_ffmpeg_extract

def test_ffmpeg_called(mocker):
    mock_run = mocker.patch("subprocess.run")

    _run_ffmpeg_extract(Path("in.mp4"), Path("out_%06d.jpg"), 2.0)

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]

    assert "ffmpeg" in args
    assert "-vf" in args
    assert "fps=2.0" in args