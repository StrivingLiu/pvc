echo '#!/bin/bash'
#grep --no-filename '\./vmware-cmd2' operations/*.py | cut -c9-

for f in operations/*.py; do
    echo "echo '***' $(basename $f) '***'"
    grep '\$ \./vmware-cmd2' $f | awk '{ print $2, $3, $4, $5, $6, $7, $8, $9 "; echo" }' -
    echo "echo"
done

