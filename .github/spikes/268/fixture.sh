#!/bin/sh
# This fixed fixture returns data for an external assertion.
set -eu
case "$1:$2" in
  alpha:normal) printf '%s\n' ALPHA ;;
  beta:normal) printf '%s\n' BETA ;;
  gamma:normal) printf '%s\n' GAMMA ;;
  alpha:negative) printf '%s\n' DELIBERATE_MISMATCH ;;
  *) exit 2 ;;
esac
