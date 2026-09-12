#!/usr/bin/env bash
# Konsil imaging pipeline setup — idempotent. Run once before first /konsil:imaging use.
set -euo pipefail

VENV="${KONSIL_VENV:-$HOME/.konsil-venv}"

echo "== Konsil imaging setup =="

if ! command -v dcm2niix >/dev/null 2>&1; then
  echo "-- installing dcm2niix (brew)"
  brew install dcm2niix
else
  echo "-- dcm2niix: $(dcm2niix -v 2>&1 | head -1)"
fi

if [ ! -d "$VENV" ]; then
  echo "-- creating venv at $VENV"
  python3 -m venv "$VENV"
fi

echo "-- installing python deps (TotalSegmentator downloads ~GB of weights on first run)"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet TotalSegmentator nibabel scikit-image trimesh

if "$VENV/bin/python" -c "import pydicom, PIL" 2>/dev/null; then
  echo "-- pydicom/Pillow: already installed"
else
  echo "-- installing pydicom + Pillow (dicom_to_png.py deps)"
  "$VENV/bin/pip" install --quiet pydicom pillow
fi

echo "-- verifying"
"$VENV/bin/python" -c "import totalsegmentator, nibabel, skimage, trimesh, pydicom, PIL; print('python deps OK')"
"$VENV/bin/TotalSegmentator" --version || true

echo "== done. Use: $VENV/bin/python scripts/dicom_to_scene.py <dicom_dir> <out_dir> --fast --device mps =="
echo "==       or: $VENV/bin/python scripts/dicom_to_png.py <in.dcm> <out.png>  # off-protocol read input (deterministic render only) =="
