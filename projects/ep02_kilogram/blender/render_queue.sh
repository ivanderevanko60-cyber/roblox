#!/bin/bash
cd "$(dirname "$0")"
B="/c/Program Files/Blender Foundation/Blender 5.1/blender.exe"
FF=$(ls /c/Users/apiwo/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg*/*/bin/ffmpeg.exe)
job() {
  local name=$1 script=$2 samples=$3; shift 3
  local dir="../renders/$name"; mkdir -p "$dir"
  echo "$(date +%T) start $name"
  env "$@" "$B" -b -P "$script" -- "$(cygpath -w "$PWD/$dir")\f" anim "$samples" > "$dir.log" 2>&1
  "$FF" -y -loglevel error -framerate 30 -i "$dir/f_%04d.png" -c:v libx264 -crf 14 -pix_fmt yuv420p "../renders/$name.mp4"
  echo "$(date +%T) done $name ($(ls "$dir" | wc -l) frames)"
}
job sphere sphere.py 40 FRAMES=120
job cylinder_close cylinder.py 32 CAM=close FRAMES=100
job cylinder_wide cylinder.py 32 FRAMES=120
echo ALL DONE
