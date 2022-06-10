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
class FIOBenchmarkTestBase(rfm.RunOnlyRegressionTest):
    '''Base class of FIO Multi VM benchmark runtime tests'''

    valid_systems = ['*:default']
    valid_prog_environs = ['gnu-azhpc']
    sourcesdir = None

    # rfmdocstart: set_deps
    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FIODownloadScriptsTest', udeps.fully)
    # rfmdocend: set_deps

@rfm.simple_test
class FIOAllVMsTest(FIOBenchmarkTestBase):
    descr = 'FIO benchmarks ALL VMs test using pssh'

    # rfmdocstart: set_exec
    @require_deps
    def set_sourcedir(self, FIODownloadScriptsTest):
        self.sourcesdir = os.path.join(
            FIODownloadScriptsTest(part='default', environ='gnu-azhpc').stagedir,
            ''
        )

    executable = './fio_pssh_test.sh'
    postrun_cmds = [
        'cat fio-test-results.log',
    ]

    @sanity_function
    def assert_num_success(self):
        num_tests = sn.len(sn.findall(r'RdIOPS: (\S+)',
                                         self.stagedir+'/fio-rd-iops-results.log'))
        num_nodes = sum(1 for _ in open(self.stagedir+'/hosts.txt'))
        return sn.assert_eq(num_tests, num_nodes)


@rfm.simple_test
class FIOWrTPTTest(FIOBenchmarkTestBase):
    descr = 'FIO benchmark Write Throughput test'

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FIOAllVMsTest', udeps.fully)

    # rfmdocstart: set_exec
    @require_deps
    def set_sourcedir(self, FIOAllVMsTest):
        self.sourcesdir = os.path.join(
            FIOAllVMsTest(part='default', environ='gnu-azhpc').stagedir,
            ''
        )

    executable = 'echo "WrTPTTest"'

    @sanity_function
    def assert_num_success(self):
        num_tests = sn.len(sn.findall(r'WrTPT: (\S+)',
                                         self.stagedir+'/fio-wr-tpt-results.log'))
        num_nodes = sum(1 for _ in open(self.stagedir+'/hosts.txt'))
        return sn.assert_eq(num_tests, num_nodes)

    @performance_function('MiB/s')
    def extract_WrTPT(self, vm='c5e'):
         return sn.extractsingle(rf'system: {vm} WrTPT: (\S+)',self.stagedir+'/fio-wr-tpt-results.log', 1, float)

    @run_before('performance')
    def set_perf_variables(self):
        '''Build the dictionary with all the performance variables.'''

        self.perf_variables = {}
        with open(self.stagedir+'/fio-wr-tpt-results.log',"r") as f:
            sys_names = f.read()

        systems = re.findall(r"system:\s(\S+)\s+.*",sys_names,re.M)
        fio = re.findall(r"WrTPT: (\S+)",sys_names,re.M)

        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        temp = {vm_series: {}}

        if vm_info != None and 'nhc_values' in vm_info:
            for i in systems:
                temp[vm_series][i] = (vm_info['nhc_values']['ssd_wrtpt'],
                                        vm_info['nhc_values']['ssd_wrtpt_limits'][0],
                                        vm_info['nhc_values']['ssd_wrtpt_limits'][1],
                                        'MiB/s')

        self.reference = temp

        for i in systems:
            self.perf_variables[i] = self.extract_WrTPT(i)

        results = {}
        for i in range(len(systems)):
            results[systems[i]] = fio[i]

        with open(self.outputdir+"/fio-wr-tpt-results.json", "w") as outfile:
            js.dump(results, outfile, indent=4)

@rfm.simple_test
class FIOWrIOPSTest(FIOBenchmarkTestBase):
    descr = 'FIO benchmark Write IOPS test'

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FIOAllVMsTest', udeps.fully)

    # rfmdocstart: set_exec
    @require_deps
    def set_sourcedir(self, FIOAllVMsTest):
        self.sourcesdir = os.path.join(
            FIOAllVMsTest(part='default', environ='gnu-azhpc').stagedir,
            ''
        )

    executable = 'echo "WrIOPSTest"'

    @sanity_function
    def assert_num_success(self):
        num_tests = sn.len(sn.findall(r'WrIOPS: (\S+)',
                                         self.stagedir+'/fio-wr-iops-results.log'))
        num_nodes = sum(1 for _ in open(self.stagedir+'/hosts.txt'))
        return sn.assert_eq(num_tests, num_nodes)

    @performance_function('k')
    def extract_WrIOPS(self, vm='c5e'):
         return sn.extractsingle(rf'system: {vm} WrIOPS: (\S+)',self.stagedir+'/fio-wr-iops-results.log', 1, float)

    @run_before('performance')
    def set_perf_variables(self):
        '''Build the dictionary with all the performance variables.'''

        self.perf_variables = {}
        with open(self.stagedir+'/fio-wr-iops-results.log',"r") as f:
            sys_names = f.read()

        systems = re.findall(r"system:\s(\S+)\s+.*",sys_names,re.M)
        fio = re.findall(r"WrIOPS: (\S+)",sys_names,re.M)

        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        temp = {vm_series: {}}

        if vm_info != None and 'nhc_values' in vm_info:
            for i in systems:
                temp[vm_series][i] = (vm_info['nhc_values']['ssd_wriops'],
                                        vm_info['nhc_values']['ssd_wriops_limits'][0],
                                        vm_info['nhc_values']['ssd_wriops_limits'][1],
                                        'k')

        self.reference = temp

        for i in systems:
            self.perf_variables[i] = self.extract_WrIOPS(i)

        results = {}
        for i in range(len(systems)):
            results[systems[i]] = fio[i]

        with open(self.outputdir+"/fio-wr-iops-results.json", "w") as outfile:
            js.dump(results, outfile, indent=4)

@rfm.simple_test
class FIORdTPTTest(FIOBenchmarkTestBase):
    descr = 'FIO benchmark Read TPT test'

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FIOAllVMsTest', udeps.fully)

    # rfmdocstart: set_exec
    @require_deps
    def set_sourcedir(self, FIOAllVMsTest):
        self.sourcesdir = os.path.join(
            FIOAllVMsTest(part='default', environ='gnu-azhpc').stagedir,
            ''
        )

    executable = 'echo "RdTPTTest"'

    @sanity_function
    def assert_num_success(self):
        num_tests = sn.len(sn.findall(r'RdTPT: (\S+)',
                                         self.stagedir+'/fio-rd-tpt-results.log'))
        num_nodes = sum(1 for _ in open(self.stagedir+'/hosts.txt'))
        return sn.assert_eq(num_tests, num_nodes)

    @performance_function('MiB/s')
    def extract_RdTPT(self, vm='c5e'):
         return sn.extractsingle(rf'system: {vm} RdTPT: (\S+)',self.stagedir+'/fio-rd-tpt-results.log', 1, float)

    @run_before('performance')
    def set_perf_variables(self):
        '''Build the dictionary with all the performance variables.'''

        self.perf_variables = {}
        with open(self.stagedir+'/fio-rd-tpt-results.log',"r") as f:
            sys_names = f.read()

        systems = re.findall(r"system:\s(\S+)\s+.*",sys_names,re.M)
        fio = re.findall(r"RdTPT: (\S+)",sys_names,re.M)

        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        temp = {vm_series: {}}

        if vm_info != None and 'nhc_values' in vm_info:
            for i in systems:
                temp[vm_series][i] = (vm_info['nhc_values']['ssd_rdtpt'],
                                        vm_info['nhc_values']['ssd_rdtpt_limits'][0],
                                        vm_info['nhc_values']['ssd_rdtpt_limits'][1],
                                        'MiB/s')

        self.reference = temp

        for i in systems:
            self.perf_variables[i] = self.extract_RdTPT(i)

        results = {}
        for i in range(len(systems)):
            results[systems[i]] = fio[i]

        with open(self.outputdir+"/fio-rd-tpt-results.json", "w") as outfile:
            js.dump(results, outfile, indent=4)

@rfm.simple_test
class FIORdIOPSTest(FIOBenchmarkTestBase):
    descr = 'FIO benchmark Read IOPS test'

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FIOAllVMsTest', udeps.fully)

    # rfmdocstart: set_exec
    @require_deps
    def set_sourcedir(self, FIOAllVMsTest):
        self.sourcesdir = os.path.join(
            FIOAllVMsTest(part='default', environ='gnu-azhpc').stagedir,
            ''
        )

    executable = 'echo "RdIOPSTest"'

    @sanity_function
    def assert_num_success(self):
        num_tests = sn.len(sn.findall(r'RdIOPS: (\S+)',
                                         self.stagedir+'/fio-rd-iops-results.log'))
        num_nodes = sum(1 for _ in open(self.stagedir+'/hosts.txt'))
        return sn.assert_eq(num_tests, num_nodes)

    @performance_function('k')
    def extract_RdIOPS(self, vm='c5e'):
         return sn.extractsingle(rf'system: {vm} RdIOPS: (\S+)',self.stagedir+'/fio-rd-iops-results.log', 1, float)

    @run_before('performance')
    def set_perf_variables(self):
        '''Build the dictionary with all the performance variables.'''

        self.perf_variables = {}
        with open(self.stagedir+'/fio-rd-iops-results.log',"r") as f:
            sys_names = f.read()

        systems = re.findall(r"system:\s(\S+)\s+.*",sys_names,re.M)
        fio = re.findall(r"RdIOPS: (\S+)",sys_names,re.M)

        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        temp = {vm_series: {}}

        if vm_info != None and 'nhc_values' in vm_info:
            for i in systems:
                temp[vm_series][i] = (vm_info['nhc_values']['ssd_rdiops'],
                                        vm_info['nhc_values']['ssd_rdiops_limits'][0],
                                        vm_info['nhc_values']['ssd_rdiops_limits'][1],
                                        'k')

        self.reference = temp

        for i in systems:
            self.perf_variables[i] = self.extract_RdIOPS(i)

        results = {}
        for i in range(len(systems)):
            results[systems[i]] = fio[i]

        with open(self.outputdir+"/fio-rd-iops-results.json", "w") as outfile:
            js.dump(results, outfile, indent=4)

@rfm.simple_test
class FIODownloadScriptsTest(rfm.RunOnlyRegressionTest):
    descr = 'FIO benchmark download scripts'
    valid_systems = ['*:default']
    valid_prog_environs = ['gnu-azhpc']

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('FioInstallTest', udeps.fully)

    executable = 'wget'
    executable_opts = [
        'https://raw.githubusercontent.com/arstgr/fio/main/fio_test.sh'  
    ]
    postrun_cmds = [
        'wget https://raw.githubusercontent.com/arstgr/fio/main/fio_pssh_test.sh',
	'chmod +x *.sh'
    ]

    @sanity_function
    def validate_download(self):
        return sn.assert_true(os.path.exists('fio_test.sh')) and sn.assert_true(os.path.exists('fio_pssh_test.sh'))

@rfm.simple_test
class FioInstallTest(rfm.RunOnlyRegressionTest):
    descr = 'Install FIO benchmarks'
    valid_systems = ['*:default']
    valid_prog_environs = ['gnu-azhpc']
    executable = 'sudo yum install fio -y'

    @sanity_function
    def validate_download(self):
        return sn.assert_true(os.path.exists('/usr/bin/fio'))

