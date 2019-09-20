#!/bin/sh

VMWARE_CMD_DIR=$(cd $(dirname $0) && pwd)
exec $VMWARE_CMD_DIR/../py.sh $VMWARE_CMD_DIR/Main.py $@
