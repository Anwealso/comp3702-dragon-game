# Keep track of how many we passed or failed
passed=0
failed=0

for i in 1 2 3 4 5 6 7
do
    echo "UCS Test $i:"
    # Run the solution script
    python3 solution.py testcases/L$i.txt temp.txt ucs;
    # Preview the temp file
    # cat temp.txt
    # Run the tests
    python3 tester.py testcases/L$i.txt temp.txt
    # Save the output status
    echo $? > temp.txt
    exitcode=$(cat temp.txt)
    echo "[[ Exit status: $exitcode ]]"

    # If exit code == 0, then passed, otherwise failed
    if [ $exitcode -eq 0 ]
    then
        # code 0 = pass
        ((passed++))
    else
        # codes -1, 255 = fail
        ((failed++))
    fi

    # Delete the temp file
    rm -f temp.txt
    # Insert a space after each test
    echo ""

done

echo "Passed: $passed, Failed: $failed"
