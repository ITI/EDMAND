cd code
python main.py &
bro -Cr ../test_trace/dnp3.trace end_point.bro &
wait
