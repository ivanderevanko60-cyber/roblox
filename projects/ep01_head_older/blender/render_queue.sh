#!/bin/bash
# Sequential final renders for EP01 3D shots. Each shot -> renders/<name>/ frames -> renders/<name>.mp4
cd "$(dirname "$0")"
B="/c/Program Files/Blender Foundation/Blender 5.1/blender.exe"
FF=$(ls /c/Users/apiwo/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg*/*/bin/ffmpeg.exe)
job() {  # name script samples [ENV=VAL ...]
  local name=$1 script=$2 samples=$3; shift 3
  local dir="../renders/$name"
  mkdir -p "$dir"
  echo "$(date +%T) start $name"
  env "$@" "$B" -b -P "$script" -- "$(cygpath -w "$PWD/$dir")\f" anim "$samples" > "$dir.log" 2>&1
  "$FF" -y -loglevel error -framerate 30 -i "$dir/f_%04d.png" -c:v libx264 -crf 14 -pix_fmt yuv420p "../renders/$name.mp4"
  echo "$(date +%T) done $name ($(ls "$dir" | wc -l) frames)"
}
job globe_routes globe.py 32 FRAMES=150
job two_clocks two_clocks.py 32 FRAMES=150
job lattice lattice.py 32 FRAMES=120
job atom_macro atom_cell.py 32 CAM=macro FRAMES=100
job atom_orbit atom_cell.py 32 CAM=orbit FRAMES=100
echo ALL DONE
