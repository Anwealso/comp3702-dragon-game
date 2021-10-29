#!/usr/bin/env bash
# Keep track of how many we passed or failed
passed=0
failed=0

if [ $1 ]
then
    # If user inputs a specific test no., then run that
    echo "[[ Test $1: ]]"
    # Run the visualiser script
#    python3 visualiser.py testcases/a3-t$1.txt 2> temp.txt;
    python3 visualiser.py testcases/a3-t$1.txt;
    # Save the output status (255=crash, 254=overtime, otherwise returns the score /50)
    echo $? > temp.txt
    exitcode=$(cat temp.txt)
    echo "[[ Exit status: $exitcode ]]"

    # If exit code < 254, then passed, otherwise failed
    if [ $exitcode -lt 51 ]
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
    for i in 1 2 3 4 5
    do
        echo "[[ Test $i: ]]"
        # Run the visualiser script
#        python3 visualiser.py testcases/a3-t$i.txt 2> temp.txt;
        python3 visualiser.py testcases/a3-t$i.txt;
        # Save the output status (255=crash, 254=overtime, otherwise returns the score /50)
        echo $? > temp.txt
        exitcode=$(cat temp.txt)
        echo "[[ Exit status: $exitcode ]]"

        # If exit code < 254, then passed, otherwise failed
        if [ $exitcode -lt 51 ]
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

echo "[[ Passed: $passed, Failed: $failed ]]"
