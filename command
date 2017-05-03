screen /dev/ttyACM0 38400
screen /dev/ttyACM1 115200
rm -f tmp && cat /dev/ttyACM1 > tmp
tail -f tmp