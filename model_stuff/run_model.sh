#!/usr/bin/env bash

set -e

python simple_baseline.py --train-file socialIQa_v1.4/socialIQa_v1.4_trn.jsonl --input-file socialIQa_v1.4/socialIQa_v1.4_tst.jsonl  --output-file predictions.lst
#python random_baseline.py --input-file socialIQa_v1.4/socialIQa_v1.4_tst.jsonl --output-file predictions.lst