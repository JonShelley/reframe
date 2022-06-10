# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
# Currently runs only on HB series VMs, will be upgraded to work with N series and HC as well
import os
import json as js
import re

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps

# rfmdocstart: HPLBenchmar on Single VMs
class FioBenchmarkTestBase(rfm.RunOnlyRegressionTest):
    '''Base class of Fio benchmark runtime tests'''

    valid_systems = ['*:default']
    valid_prog_environs = ['gnu-azhpc']
    sourcesdir = None

    # rfmdocstart: set_deps
    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FioInstallTest', udeps.fully)
    # rfmdocend: set_deps

@rfm.simple_test
class FioWriteIOPSTest(FioBenchmarkTestBase):
    descr = 'Fio Write IOPS test'

    prerun_cmds = [
       "TEMP_DIR=$(mount | grep sdb1 | awk '{print $3}')/fiotest",
	'mkdir -p $TEMP_DIR',
	'rm -rf $TEMP_DIR/*',
	'sleep 5'
    ]
    executable = 'fio'
    executable_opts = [
        '--name=write_iops',
	' --directory=$TEMP_DIR',
	' --numjobs=2',
	'--size=2G',
	' --time_based',
	' --runtime=300s',
	' --ramp_time=2s',
	' --ioengine=libaio',
	' --direct=1',
	' --verify=0',
	' --bs=4K',
	' --iodepth=128',
	' --rw=randwrite'
	' --group_reporting=1'
	'--minimal',
	'--output-format=json',
	'--output=fio-write-iops.json'
    ]
    postrun_cmds = [
	'echo PWD=$PWD',
        'cat fio-write-iops.json',
    ]

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FioInstallTest', udeps.fully)

    @sanity_function
    def check_results(self):
        return sn.assert_true(os.path.exists('fio-write-iops.json'))

    @performance_function('k')
    def extract_iops(self, op="write"):
        with open('fio-write-iops.json') as g:
            test_results = js.load(g)

        res = test_results["jobs"][0][op]["iops"]/1000.0
        return res 

    @run_before('performance')
    def set_perf_variables(self):
        '''Build the dictionary with all the performance variables.'''

        self.perf_variables = {}

        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        temp = {vm_series: {}}

        if vm_info != None and 'nhc_values' in vm_info:
            temp[vm_series]["WRITE_IOPS"] = (vm_info['nhc_values']['ssd_wriops'],
                                        vm_info['nhc_values']['ssd_wriops_limits'][0],
                                        vm_info['nhc_values']['ssd_wriops_limits'][1],
                                        'k')

        self.reference = temp


        self.perf_variables["WRITE_IOPS"] = self.extract_iops("write")

@rfm.simple_test
class FioReadIOPSTest(FioBenchmarkTestBase):
    descr = 'Fio Read IOPS test'

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FioWriteIOPSTest', udeps.fully)


    prerun_cmds = [
        "TEMP_DIR=$(mount | grep sdb1 | awk '{print $3}')/fiotest",
	'mkdir -p $TEMP_DIR',
	'rm -rf $TEMP_DIR/*',
	'sleep 5'
    ]
    executable = 'fio'
    executable_opts = [
	'--name=read_iops',
	' --directory=$TEMP_DIR',
	' --numjobs=2',
	' --size=2G',
	' --time_based',
	' --runtime=240s',
	' --ramp_time=2s',
	' --ioengine=libaio',
	' --direct=1',
	' --verify=0',
	' --bs=4K',
	' --iodepth=128',
	' --rw=randread',
	' --group_reporting=1',
	'--minimal',
	'--output-format=json',
	'--output=fio-read-iops.json'
    ]
    postrun_cmds = [
	'echo PWD=$PWD',
        'cat fio-read-iops.json',
    ]

    @sanity_function
    def check_results(self):
        return sn.assert_true(os.path.exists('fio-read-iops.json'))

    @performance_function('k')
    def extract_bw(self, op="write"):
        with open('fio-read-iops.json') as f:
            test_results = js.load(f)

        res = test_results["jobs"][0][op]["iops"]/1000.0
        return res 

    @run_before('performance')
    def set_perf_variables(self):
        '''Build the dictionary with all the performance variables.'''

        self.perf_variables = {}

        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        temp = {vm_series: {}}

        if vm_info != None and 'nhc_values' in vm_info:
            temp[vm_series]["READ_IOPS"] = (vm_info['nhc_values']['ssd_rdiops'],
                                        vm_info['nhc_values']['ssd_rdiops_limits'][0],
                                        vm_info['nhc_values']['ssd_rdiops_limits'][1],
                                        'k')


        self.reference = temp
        self.perf_variables["READ_IOPS"] = self.extract_bw("read")


@rfm.simple_test
class FioWriteTPTTest(FioBenchmarkTestBase):
    descr = 'Fio Write Throughput test'

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FioReadIOPSTest', udeps.fully)


    prerun_cmds = [
        "TEMP_DIR=$(mount | grep sdb1 | awk '{print $3}')/fiotest",
	'mkdir -p $TEMP_DIR',
	'rm -rf $TEMP_DIR/*',
	'sleep 5'
    ]
    executable = 'fio'
    executable_opts = [
        '--name=write_throughput',
	' --directory=$TEMP_DIR',
	' --numjobs=16',
	' --size=10G',
	' --time_based',
	' --runtime=120s',
	' --ramp_time=2s',
	' --ioengine=libaio',
	' --direct=1',
	' --verify=0',
	' --bs=1M',
	' --iodepth=64',
	' --rw=write',
	' --group_reporting=1',
	'--minimal',
	'--output-format=json',
	'--output=fio-write-tpt.json'
    ]
    postrun_cmds = [
	'echo PWD=$PWD',
        'cat fio-write-tpt.json',
    ]

    @sanity_function
    def check_results(self):
        return sn.assert_true(os.path.exists('fio-write-tpt.json'))

    @performance_function('MiB/s')
    def extract_bw(self, op="write"):
        with open('fio-write-tpt.json') as f:
            test_results = js.load(f)

        res = test_results["jobs"][0][op]["bw"]/1024.0
        return res 

    @run_before('performance')
    def set_perf_variables(self):
        '''Build the dictionary with all the performance variables.'''

        self.perf_variables = {}

        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        temp = {vm_series: {}}

        if vm_info != None and 'nhc_values' in vm_info:
            temp[vm_series]["WRITE_TPT"] = (vm_info['nhc_values']['ssd_wrtpt'],
                                        vm_info['nhc_values']['ssd_wrtpt_limits'][0],
                                        vm_info['nhc_values']['ssd_wrtpt_limits'][1],
                                        'MiB/s')

        self.reference = temp
        self.perf_variables["WRITE_TPT"] = self.extract_bw("write")

@rfm.simple_test
class FioReadTPTTest(FioBenchmarkTestBase):
    descr = 'Fio Read Throughput test'

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FioWriteTPTTest', udeps.fully)


    prerun_cmds = [
        "TEMP_DIR=$(mount | grep sdb1 | awk '{print $3}')/fiotest",
	'mkdir -p $TEMP_DIR',
	'rm -rf $TEMP_DIR/*',
	'sleep 5'
    ]
    executable = 'fio'
    executable_opts = [
	'--name=read_throughput',
	' --directory=$TEMP_DIR',
	' --numjobs=16',
	' --size=10G', 
	'--time_based',
	' --runtime=120s',
	' --ramp_time=2s',
	' --ioengine=libaio',
	' --direct=1',
	' --verify=0',
	' --bs=1M',
	' --iodepth=64',
	' --rw=read',
	' --group_reporting=1',
	'--minimal',
	'--output-format=json',
	'--output=fio-read-tpt.json'
    ]
    postrun_cmds = [
	'echo PWD=$PWD',
        'cat fio-read-tpt.json',
    ]

    @sanity_function
    def check_results(self):
        return sn.assert_true(os.path.exists('fio-read-tpt.json'))

    @performance_function('MiB/s')
    def extract_bw(self, op="write"):
        with open('fio-read-tpt.json') as f:
            test_results = js.load(f)

        res = test_results["jobs"][0][op]["bw"]/1024.0
        return res 

    @run_before('performance')
    def set_perf_variables(self):
        '''Build the dictionary with all the performance variables.'''

        self.perf_variables = {}

        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        temp = {vm_series: {}}

        if vm_info != None and 'nhc_values' in vm_info:
            temp[vm_series]["READ_TPT"] = (vm_info['nhc_values']['ssd_rdtpt'],
                                        vm_info['nhc_values']['ssd_rdtpt_limits'][0],
                                        vm_info['nhc_values']['ssd_rdtpt_limits'][1],
                                        'MiB/s')

        self.reference = temp
        self.perf_variables["READ_TPT"] = self.extract_bw("read")


@rfm.simple_test
class FioInstallTest(rfm.RunOnlyRegressionTest):
    descr = 'Install FIO benchmarks'
    valid_systems = ['*:default']
    valid_prog_environs = ['gnu-azhpc']
    executable = 'sudo yum install fio -y'

    @sanity_function
    def validate_download(self):
        return sn.assert_true(os.path.exists('/usr/bin/fio'))

