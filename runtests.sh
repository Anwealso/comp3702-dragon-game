# Keep track of how many we passed or failed
passed=0
failed=0

for i in 1 2 3 4 5 6 7
do
    echo "Test $i:"
    # Run the solution script
    python solution.py testcases/L$i.txt temp.txt ucs;
    # Preview the temp file
    # cat temp.txt
    # Run the tests
    python tester.py testcases/L$i.txt temp.txt
    # Save the output status
    echo $? > temp.txt
    exitcode=$(cat temp.txt)
    echo "[[ Exit status: $exitcode ]]"

    # If exit code == 255, then failed, otherwise passed
    if [ $exitcode -eq 255 ]
    then
        $((failed++))
    else
        $((passed++))
    fi

    # Delete the temp file
    # rm -f temp.txt
    # Insert a space after each test
    echo ""

done

echo "Passed: $passed, Failed: $failed"
