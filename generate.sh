#!/bin/bash
folder_name=1
mkdir "/mnt/c/Users/admin/Desktop/test/$folder_name"
for i in {1..5000}
do
  if [ $((i % 100)) -eq 0 ]; then
    folder_name=$((folder_name+1))
    mkdir "/mnt/c/Users/admin/Desktop/test/$folder_name"
  fi
  folder_path="/mnt/c/Users/admin/Desktop/test/$folder_name"
  cp "/mnt/c/Users/admin/Desktop/test/test.pdf" "$folder_path/$i.pdf"
  echo $i
done