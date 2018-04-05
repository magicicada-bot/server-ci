#!/bin/bash

# Copyright 2008-2015 Canonical
# Copyright 2015-2018 Chicharreros (https://launchpad.net/~chicharreros)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  http://launchpad.net/magicicada-server

# run the minimal infraestructure to run the sdtests isolated from the current session
ROOTDIR=${ROOTDIR:-`bzr root`}
ADDRESS_FILE="${ROOTDIR}/tmp/dbus.address"
make start-dbus
env DEBUG="file $DEBUG" SERVER_DEBUG="$SERVER_DEBUG" ROOTDIR=$ROOTDIR DBUS_SESSION_BUS_ADDRESS=$(cat $ADDRESS_FILE) XDG_CACHE_HOME="${ROOTDIR}/tmp/xdg_cache" \
${PYTHON:-python} -Wignore ./test $@
EXIT_VAL=$?
make stop-dbus
exit $EXIT_VAL
