# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import pathlib

import pytest

from voogle import transcription

pytestmark = pytest.mark.integration


@pytest.mark.skip(reason="not reliable between different versions")
@pytest.mark.description("Tests audio transcription with Whisper, CSV storage, and retrieval")
def test_audio_transcription(
    jobs_mp3_path: pathlib.Path,
    jobs_csv_path: pathlib.Path,
    jobs_transcription: transcription.Transcription,
) -> None:
    tr = transcription.transcribe(jobs_mp3_path)
    assert len(tr) > 0
    assert len(tr[0]) == 3
    assert tr[0][0] == 0.0
    assert isinstance(tr[0][1], float)
    assert isinstance(tr[0][2], str)
    transcription.store_transcription(tr, jobs_csv_path)
    read = transcription.read_transcription(jobs_csv_path)

    original_text = "".join([r[2] for r in jobs_transcription])
    current_text = "".join([r[2] for r in read])

    assert original_text == current_text
