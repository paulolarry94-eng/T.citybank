#!/bin/bash
# usage: convert_all_ticks.sh SYM "YEARS" ; clones each year branch, converts, deletes the clone
SYM=$1; YEARS=$2; LOW=$(echo $SYM | tr A-Z a-z)
REPO=https://github.com/paulolarry94-eng/FX-Data-${SYM}-DS
for Y in $YEARS; do
  [ -f data/${SYM}_M1_bid_${Y}.npz ] && { echo "$SYM $Y: already done"; continue; }
  D=/tmp/ticks/${SYM}${Y}; rm -rf $D; mkdir -p /tmp/ticks
  for try in 1 2 3; do
    timeout 1500 git clone -q --depth 1 --single-branch -b ${SYM}-${Y} $REPO $D 2>&1 | tail -1 && [ -d $D/$SYM ] && break
    echo "$SYM $Y: clone retry $try"; rm -rf $D; sleep $((try*5))
  done
  python3 tools/ticks_to_m1.py $D $SYM $Y || echo "$SYM $Y: CONVERT FAILED"
  rm -rf $D
done
echo "WORKER $SYM DONE"
