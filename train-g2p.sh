

train_file="$1"
test_file="$2"

echo $train_file
echo $test_file

g2p.py --encoding utf-8 --train $train_file --devel 5% --write-model thai-g2p-model-1
echo "finish train step 1"

g2p.py --encoding utf-8 --train $train_file --ramp-up --model thai-g2p-model-1 --devel 5% --write-model thai-g2p-model-2
echo "finish train step 2"

g2p.py --encoding utf-8 --train $train_file --ramp-up --model thai-g2p-model-2 --devel 5% --write-model thai-g2p-model-3
echo "finish train step 3"

g2p.py --encoding utf-8 --train $train_file --ramp-up --model thai-g2p-model-3 --devel 5% --write-model thai-g2p-model-4
echo "finish train step 4"

g2p.py --encoding utf-8 --train $train_file --ramp-up --model thai-g2p-model-4 --devel 5% --write-model thai-g2p-model-5
echo "finish train step 5"

g2p.py --encoding utf-8 --test $test_file --model thai-g2p-model-5 > test.log
