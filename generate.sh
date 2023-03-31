#!/bin/bash
for i in {1..1000000}
do
  cp "/mnt/c/Users/admin/Desktop/test/test.pdf" "/mnt/c/Users/admin/Desktop/test/test2/${i}.pdf"
  echo $i
done