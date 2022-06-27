#!/usr/bin/sh

cd /home/pi
echo "Staring Rubik Robot code" > log.txt
/usr/bin/python3 rubik.py >> log.txt
if [ $? -eq 0 ]
then
  echo "Normal exit"
  sudo halt
  exit 0
else
  echo "Failure"
  exit 1
fi
