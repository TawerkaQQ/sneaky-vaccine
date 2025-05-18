for f in *.webp; do ffmpeg -i "$f" "${f%.*}.jpg"; done
for f in *.avif; do ffmpeg -i "$f" "${f%.*}.jpg"; done