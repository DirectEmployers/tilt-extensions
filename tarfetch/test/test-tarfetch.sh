#!/usr/bin/env bash
set -eu

successes=0
failures=0

print_test() {
  message="$1"
  shift

  if [ $@ ]; then
    state="\033[32mPASSED\033[0m"
    successes=$((successes + 1))
  else
    state="\033[31mFAILED\033[0m"
    failures=$((failures + 1))
  fi

  echo -e "${state} - ${message}"
}

./trigger.sh btn-tarfetch-tarfetch-example
sleep 2

echo
echo "Test results:"

print_test "Test files/ exists" -d files/
print_test "Test do.sync exists" -f files/do.sync
print_test "Test dont.sync does not exist" ! -f files/dont.sync
print_test "Test do/ exists" -d files/do/
print_test "Test do/do.sync exists" -f files/do/do.sync
print_test "Test do/dont.sync does not exist" ! -f files/do/dont.sync
print_test "Test dont/ does not exist" ! -d files/dont/

echo
echo "Ran $((failures + successes)) tests"
if [ "$failures" = "0" ]; then
  echo -e "\033[32mOK\033[0m"
else
  echo -e "\033[31mFAILED (failures=${failures}, successes=${successes})\033[0m"
fi
echo
