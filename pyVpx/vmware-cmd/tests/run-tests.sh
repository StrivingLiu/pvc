for test_prog in ./*Tests.py; do
    echo "********** $test_prog ***********"
    echo
    ${test_prog} "$@"
    echo
    echo
done
