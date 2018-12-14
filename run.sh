cd code
python main.py &
bro -Cr ../trace/dnp3.trace end_point.bro &
wait