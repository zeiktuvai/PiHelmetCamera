for f in camera/*.h264
do
  echo "Processing $f file..."
  filename=$(basename "$f")
  extension="${filename##*.}"
  filename="${filename%.*}"
  MP4Box -add $f camera/$filename.mp4
done
