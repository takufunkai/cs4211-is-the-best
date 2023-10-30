#!/bin/bash

# This script aims to reduce the number of lines that we need to process in the generate_pcsp.py script.
# We only take a chunk from the main csv file.
# TODO: Might need to change this to non-player specific data

P1='Novak Djokovic'
P2='Daniil Medvedev'
OUTPUT=output-test.csv

echo "P1 ${P1},P2 ${P2},Output ${OUTPUT}"

grep "\"${P1}\",\"${P2}\"" tennis* > $OUTPUT
grep "\"${P2}\",\"${P1}\"" tennis* >> $OUTPUT

wc -l < ${OUTPUT} | { read lines; echo "${lines} lines written to ${OUTPUT}"; }

