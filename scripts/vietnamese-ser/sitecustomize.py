"""Route torchaudio.load/save through `soundfile` on this Windows box.

torchaudio >= 2.9 delegates all audio I/O to `torchcodec`, which needs the
FFmpeg *shared* DLLs (libavcodec-*.dll ...). The FFmpeg here is a static
`full_build` (no shared DLLs), so torchcodec can't load and every
`torchaudio.load`/`.save` raises ModuleNotFoundError/RuntimeError. The venv
already ships a self-contained `soundfile` (bundled libsndfile, no FFmpeg), so
we monkeypatch the two public entrypoints to use it for PCM wav.

Activated by putting this file's directory on PYTHONPATH — Python auto-imports
`sitecustomize` at interpreter startup, so it also patches the demucs subprocess
(which inherits the env). No edit to pilot_extract.py. If torchcodec ever loads
cleanly, the patch is skipped and stock torchaudio is used.

See docs/tasks/vn-tv-ser-pilot.md (Decision Log, 2026-07-03).
"""

from __future__ import annotations


def _install() -> None:
    try:
        import torchaudio
    except Exception:
        return  # torchaudio not in play for this process

    # If torchcodec loads, leave stock torchaudio alone.
    try:
        import torchcodec

        _ = torchcodec._core  # touch the native lib; raises if DLLs are missing
        return
    except Exception:
        pass

    import soundfile as sf
    import torch

    _subtype = {
        (16, "PCM_S"): "PCM_16",
        (24, "PCM_S"): "PCM_24",
        (32, "PCM_S"): "PCM_32",
        (32, "PCM_F"): "FLOAT",
    }

    def load(
        uri,
        frame_offset=0,
        num_frames=-1,
        normalize=True,
        channels_first=True,
        format=None,
        buffer_size=4096,
        backend=None,
    ):
        data, sr = sf.read(
            str(uri), start=frame_offset, frames=num_frames, dtype="float32", always_2d=True
        )
        wav = torch.from_numpy(data.T.copy())  # (channels, frames)
        if not channels_first:
            wav = wav.t()
        return wav, sr

    def save(
        uri,
        src,
        sample_rate,
        channels_first=True,
        format=None,
        encoding=None,
        bits_per_sample=None,
        buffer_size=4096,
        backend=None,
        compression=None,
    ):
        wav = src.detach().cpu()
        if channels_first:
            wav = wav.t()  # soundfile wants (frames, channels)
        subtype = _subtype.get((bits_per_sample or 16, encoding or "PCM_S"))
        sf.write(str(uri), wav.numpy(), int(sample_rate), subtype=subtype)

    torchaudio.load = load
    torchaudio.save = save


_install()
