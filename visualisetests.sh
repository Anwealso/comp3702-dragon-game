# Keep track of how many we passed or failed
passed=0
failed=0

if [ $1 ]
then
    # If user inputs a specific test no., then run that
    echo "UCS Test $1:"
    # Run the solution script
    python3 solution.py testcases/L$1.txt temp.txt ucs;
    # Preview the temp file
    # cat temp.txt
    # Run the tests
    python3 visualiser.py testcases/L$1.txt temp.txt
    # Save the output status, overwriting temp
    echo $? > temp.txt
    exitcode=$(cat temp.txt)
    # echo "[[ Exit status: $exitcode ]]"

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

else
    # If user doesn't give a specific test no., do all the tests
    for i in 1 2 3 4 5 6 7 8
    do
        echo "UCS Test $i:"
        # Run the solution script
        python3 solution.py testcases/L$i.txt temp.txt ucs;
        # Preview the temp file
        # cat temp.txt
        # Run the tests
        python3 visualiser.py testcases/L$i.txt temp.txt
        # Save the output status, overwriting temp
        echo $? > temp.txt
        exitcode=$(cat temp.txt)
        # echo "[[ Exit status: $exitcode ]]"

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
fi

echo "Passed: $passed, Failed: $failed"
