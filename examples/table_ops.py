#
# Copyright (C) 2018, 2019 Oracle and/or its affiliates. All rights reserved.
#
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl
#
# Please see LICENSE.txt file included in the top-level directory of the
# appropriate download for a copy of the license and additional information.
#

#
# This is a simple example to demonstrate use of the Python driver for the
# Oracle NoSQL Database Cloud Service. It can be used to run against the
# cloud service itself or against the Cloud Simulator, which can be downloaded
# and run locally. See the comments in parameters.py about running in different
# environments. By default the example is ready to run against the Cloud
# Simulator.
#
# The example demonstrates:
# o configuring and creating a handle to access the service
# o create a table
# o create an index
# o get the table
# o get the index
# o get the table usage information
# o drop the table
#
# This example is not intended to be an exhaustive overview of the API, which
# has a number of additional operations.
#
# Requirements:
#  1. Python 2.7
#  2. Python dependencies (install using pip or other mechanism):
#   o requests
#  3. If running against the Cloud Simulator, it can be downloaded from here:
#   http://www.oracle.com/technetwork/topics/cloud/downloads/index.html#nosqlsdk
#  It requires Java
#  4. If running against the Oracle NoSQL Database Cloud Service an account
#  must be used along with additional authentication information. See
#  instructions in the comments in parameters.py
#
# To run:
#  1. set PYTHONPATH to include the parent directory of ../src/borneo
#  2. modify variables in parameters.py for the runtime environment after
#  reading instructions in the comments.
#  2. run
#    $ python example2.py
#

from __future__ import print_function
import traceback

from borneo import (
    GetIndexesRequest, GetTableRequest, ListTablesRequest, State, TableLimits,
    TableRequest, TableUsageRequest)

from parameters import drop_table, index_name, table_name, tenant_id
from utils import get_handle


def main():

    handle = None
    try:
        #
        # Create a handle
        #
        handle = get_handle(tenant_id)

        #
        # List any existing tables for this tenant
        #
        print('Listing tables')
        ltr = ListTablesRequest()
        lr_result = handle.list_tables(ltr)
        print('Existing tables: ' + str(lr_result))

        #
        # Create a table
        #
        statement = 'Create table if not exists ' + table_name + '(id integer, \
sid integer, name string, primary key(shard(sid), id))'
        print('Creating table: ' + statement)
        request = TableRequest().set_statement(statement).set_table_limits(
            TableLimits(30, 10, 1))
        result = handle.table_request(request)

        #
        # Table creation can take time, depending on the state of the system.
        # If if fails after 40s, re-run the program
        #
        result.wait_for_state(handle, table_name, State.ACTIVE, 40000, 3000)
        print('After create table')

        #
        # Create an index
        #
        statement = ('Create index if not exists ' + index_name + ' on ' +
                     table_name + '(name)')
        print('Creating index: ' + statement)
        request = TableRequest().set_statement(statement)
        result = handle.table_request(request)

        #
        # Index creation can take time, depending on the state of the system.
        # If if fails after 40s, re-run the program
        #
        result.wait_for_state(handle, table_name, State.ACTIVE, 40000, 3000)
        print('After create index')

        #
        # Get the table
        #
        request = GetTableRequest().set_table_name(table_name)
        result = handle.get_table(request)
        print('After get table: ' + str(result))

        #
        # Get the indexes
        #
        request = GetIndexesRequest().set_table_name(table_name)
        result = handle.get_indexes(request)
        print('The indexes for: ' + table_name)
        for idx in result.get_indexes():
            print('\t' + str(idx))

        #
        # Get the table usage information
        #
        request = TableUsageRequest().set_table_name(table_name)
        result = handle.get_table_usage(request)
        print('The table usage information for: ' + table_name)
        for record in result.get_usage_records():
            print('\t' + str(record))

        #
        # Drop the table
        #
        if drop_table:
            request = TableRequest().set_statement('drop table if exists ' +
                                                   table_name)
            result = handle.table_request(request)

            #
            # Table drop can take time, depending on the state of the system.
            # If this wait fails the table will still probably been dropped
            #
            result.wait_for_state(handle, table_name, State.DROPPED, 30000,
                                  2000)
            print('After drop table')
        else:
            print('Not dropping table')

        print('Example is complete')
    except Exception as e:
        print(e)
        traceback.print_exc()
    finally:
        # If the handle isn't closed Python will not exit properly
        if handle is not None:
            handle.close()


if __name__ == '__main__':
    main()
