#!/bin/bash

P1='Novak Djokovic'
P2='Daniil Medvedev'
OUTPUT=output-test.csv

echo "P1 ${P1},P2 ${P2},Output ${OUTPUT}"

grep "\"${P1}\",\"${P2}\"" tennis* > $OUTPUT
grep "\"${P2}\",\"${P1}\"" tennis* >> $OUTPUT

wc -l < ${OUTPUT} | { read lines; echo "${lines} lines written to ${OUTPUT}"; }

