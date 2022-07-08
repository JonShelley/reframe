# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import json as js
import re

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
<<<<<<< HEAD

class HPLBenchmarkTestBase(rfm.RunOnlyRegressionTest):
    '''Base class of HPL benchmark runtime tests'''

    valid_systems = ['*:default']
    valid_prog_environs = ['gnu-azhpc']
    sourcesdir = None
    
    # rfmdocstart: set_deps
    @run_after('init')
    def set_dependencies(self):
        self.depends_on('HPLBuildTest', udeps.by_env)
    # rfmdocend: set_deps

@rfm.simple_test
class HPLSingleVMTest(HPLBenchmarkTestBase):
    descr = 'HPL Single VM test using pssh'
    num_tasks = 0
    
    @require_deps
    def set_sourcedir(self, HPLBuildTest):
        stage_path = os.path.join(
            HPLBuildTest(part='default', environ='gnu-azhpc').stagedir,
            ''
        )
        repo_path = stage_path.replace("stage","repo")
        self.sourcesdir = repo_path
=======
from reframe.core.backends import getlauncher

@rfm.simple_test
class HPLSingleVMTest(rfm.RunOnlyRegressionTest):
    descr = 'HPL Single VM test using pssh'
    valid_systems = ['*']
    valid_prog_environs = ['*']
#    num_tasks = 1
    
#    @run_after('init')
    @run_before('run')
    def copy_files(self):
        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        vmtype = vm_series.split("_",1)[0]
        source_path = self.prefix.split("reframe",1)[0]+'reframe'+'/azure_nhc/system/hpl-utils'
        #self.sourcesdir = source_path
        stage_path = self.stagedir 
        os.system(f"cp -r {source_path}/xhpl-{vmtype} {stage_path}/") 
        os.system(f"cp -r {source_path}/appfile_ccx_{vm_series} {stage_path}/")
        os.system(f"cp -r {source_path}/xhpl_ccx.sh {stage_path}/")
        os.system(f"cp -r {source_path}/HPL.dat {stage_path}/")
>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0
  
    @run_after('init')
    def set_hpl_prerun_options(self):
        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
<<<<<<< HEAD
        self.prerun_cmds = [
            'echo $(hostname)',
            'mkdir HPL-$(hostname)',
            'cd HPL-$(hostname)',
            'echo $(hostname) > hosts.txt',
            'cp ../HPL.dat .',
            'cp ../appfile*_ccx .',
            'cp ../xhpl_ccx.sh .',
            'cp ../xhpl .',
            'echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled',
            'echo always | sudo tee /sys/kernel/mm/transparent_hugepage/defrag'
=======
        vmtype = vm_series.split("_",1)[0]
        self.prerun_cmds = [
            f"export SYSTEM={vmtype}",
            'echo $(hostname)',
            'echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled',
            'echo always | sudo tee /sys/kernel/mm/transparent_hugepage/defrag',
>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0
            ]
        if vm_series == 'hbrs_v2':
            self.prerun_cmds.append('sed -i "s/4           Ps/6           Ps/g" HPL.dat')
            self.prerun_cmds.append('sed -i "s/4            Qs/5            Qs/g" HPL.dat')
<<<<<<< HEAD

    executable = 'mpirun'
    cmda = "echo "
    cmdb = "system: $(hostname) HPL: $(grep WR hpl*.log | awk -F ' ' '{print $7}')"
    cmdc = "  >> ../hpl-test-results.log"
=======
        if vm_series == 'hbrs':
            self.prerun_cmds.append('sed -i "s/4           Ps/5           Ps/g" HPL.dat')
            self.prerun_cmds.append('sed -i "s/4            Qs/3            Qs/g" HPL.dat')

    executable = 'mpirun'
    cmda = "echo "
    cmdb = "system: $HOSTNAME HPL: $(grep WR hpl*.log | awk -F ' ' '{print $7}')"
    cmdc = "  >> hpl-test-results.log"
>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0
    cmd = cmda+cmdb+cmdc
    postrun_cmds = [
        'cat hpl*.log',
        cmd,
<<<<<<< HEAD
        'cp hosts.txt ../',
        'cd ../',
        'cat hpl-test-results.log',
=======
>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0
    ]

    @run_before('run')
    def set_hpl_options(self):
<<<<<<< HEAD
=======
        self.prerun_cmds.append(f"cd {self.stagedir}")
>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0
        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        if vm_series == 'hbrs_v3':
            self.executable_opts = [
<<<<<<< HEAD
=======
                '-np 16',
>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0
                '--mca mpi_leave_pinned 1',
                '--bind-to none',
                '--report-bindings',
                '--mca btl self,vader',
                '--map-by ppr:1:l3cache',
                '-x OMP_NUM_THREADS=6',
                '-x OMP_PROC_BIND=TRUE',
                '-x OMP_PLACES=cores',
                '-x LD_LIBRARY_PATH',
<<<<<<< HEAD
                '-app ./appfile_ccx  >> hpl-$(hostname).log'
=======
                '-app ./appfile_ccx_hbrs_v3  >> hpl-$HOSTNAME.log'
            ]
            self.job.options = [
                '--nodes=1',
                '--ntasks=16',
                '--cpus-per-task=6',
                '--threads-per-core=1'
>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0
            ]
        elif vm_series == 'hbrs_v2':
            self.executable_opts = [
                '-np 30',
<<<<<<< HEAD
                '--report-bindings',
                '--mca btl self,vader',
                '--map-by ppr:1:l3cache:pe=4',
=======
                '--mca mpi_leave_pinned 1',
                '--bind-to none',
                '--report-bindings',
                '--mca btl self,vader',
                '--map-by ppr:1:l3cache',
>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0
                '-x OMP_NUM_THREADS=4',
                '-x OMP_PROC_BIND=TRUE',
                '-x OMP_PLACES=cores',
                '-x LD_LIBRARY_PATH',
<<<<<<< HEAD
                './xhpl >> hpl-$(hostname).log'
            ]

=======
                '-app ./appfile_ccx_hbrs_v2  >> hpl-$HOSTNAME.log'
            ]
            self.job.options = [
                '--nodes=1',
                '--ntasks=30',
                '--cpus-per-task=4',
                '--threads-per-core=1'
            ]
        elif vm_series == 'hbrs':
            self.executable_opts = [
                '-np 15',
                '--mca mpi_leave_pinned 1',
                '--bind-to none',
                '--report-bindings',
                '--mca btl self,vader',
                '--map-by ppr:1:l3cache',
                '-x OMP_NUM_THREADS=4',
                '-x OMP_PROC_BIND=TRUE',
                '-x OMP_PLACES=cores',
                '-x LD_LIBRARY_PATH',
                '-app ./appfile_ccx_hbrs  >> hpl-$HOSTNAME.log'
            ]
            self.job.options = [
                '--nodes=1',
                '--ntasks=15',
                '--cpus-per-task=4',
                '--threads-per-core=1'
            ]

    @run_before('run')
    def replace_launcher(self):
        self.job.launcher = getlauncher('local')()

>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0
    @sanity_function
    def assert_num_messages(self):
        num_tests = sn.len(sn.findall(r'HPL: (\S+)',
                                         self.stagedir+'/hpl-test-results.log'))
<<<<<<< HEAD
        num_nodes = sum(1 for _ in open(self.stagedir+'/hosts.txt'))
        return sn.assert_eq(num_tests, num_nodes)
=======
        return sn.assert_eq(num_tests, 1)
>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0

    @performance_function('Gflops')
    def extract_hpl_s(self, vm='c5e'):
         return sn.extractsingle(rf'system: {vm} HPL: (\S+)',self.stagedir+'/hpl-test-results.log', 1, float)


    @run_before('performance')
    def set_perf_variables(self):
        
        self.perf_variables = {}
        with open(self.stagedir+'/hpl-test-results.log',"r") as f:
            sys_names = f.read()

        systems = re.findall(r"system:\s(\S+)\s+.*",sys_names,re.M)
        hpl = re.findall(r"HPL: (\S+)",sys_names,re.M)

        vm_info = self.current_system.node_data
        vm_series = vm_info['vm_series']
        temp = {vm_series: {}}

        if vm_info != None and 'nhc_values' in vm_info:
            for i in systems:
                temp[vm_series][i] = (vm_info['nhc_values']['hpl_performance'], 
                                        vm_info['nhc_values']['hpl_performance_limits'][0],
                                        vm_info['nhc_values']['hpl_performance_limits'][1],
                                        'Gflops')

        self.reference = temp

        for i in systems:
            self.perf_variables[i] = self.extract_hpl_s(i)

        results = {}
        for i in range(len(systems)):
            results[systems[i]] = hpl[i]

        with open(self.outputdir+"/hpl_test_results.json", "w") as outfile:
            js.dump(results, outfile, indent=4)


<<<<<<< HEAD
@rfm.simple_test
class HPLBuildTest(rfm.RunOnlyRegressionTest):
    descr = 'HPL benchmark build test'
    valid_systems = ['*:default']
    valid_prog_environs = ['gnu-azhpc']
    executable = './hpl_build_script.sh'

    @run_after('init')
    def inject_dependencies(self):
        self.depends_on('HPLDownloadTest', udeps.fully)

    @require_deps
    def set_sourcedir(self, HPLDownloadTest):
        stage_path = os.path.join(
            HPLDownloadTest(part='default', environ='gnu-azhpc').stagedir,
            ''
        )
        repo_path = stage_path.replace("stage","repo")
        self.sourcesdir = repo_path

    @run_before('run')
    def check_if_already_exists(self):
        stage_path = self.stagedir
        repo_path = stage_path.replace("stage","repo")
        if os.path.exists(repo_path) and os.path.exists(f"{repo_path}/xhpl"):
            os.system(f"cp -r {repo_path}/* {stage_path}/")
            self.executable = 'echo'
            self.executable_opts = [
                'already ran'  # noqa: E501
            ]
            self.postrun_cmds = [
                'rm -rf blis/.git'
            ]

    @run_after('run')
    def copy_to_repo(self):
        stage_path = self.stagedir
        repo_path = stage_path.replace("stage","repo")
        os.system(f"mkdir -p {repo_path}") 
        os.system(f"cp -r {stage_path}/* {repo_path}/") 

    @sanity_function
    def validate_download(self):
        return sn.assert_true(os.path.exists('xhpl'))

@rfm.simple_test
class HPLDownloadTest(rfm.RunOnlyRegressionTest):
    descr = 'HPL benchmarks download sources'
    valid_systems = ['*:default']
    valid_prog_environs = ['gnu-azhpc']
    executable = 'wget'
    executable_opts = [
        'https://raw.githubusercontent.com/arstgr/hpl/main/hpl_build_script.sh'  # noqa: E501
    ]
    postrun_cmds = [
        'chmod +x hpl_build_script.sh'
    ]

    @run_before('run')
    def check_if_already_exists(self):
        stage_path = self.stagedir
        repo_path = stage_path.replace("stage","repo")
        if os.path.exists(repo_path) and os.path.exists(f"{repo_path}/hpl_build_script.sh"):
            self.executable = 'echo'
            self.executable_opts = [
                'already ran'  # noqa: E501
            ]
            self.postrun_cmds = [
                'chmod +x hpl_build_script.sh'
            ]
            
    @run_after('run')
    def copy_to_repo(self):
        stage_path = self.stagedir
        repo_path = stage_path.replace("stage","repo")
        os.system(f"mkdir -p {repo_path}") 
        os.system(f"cp -r {stage_path}/* {repo_path}/") 

    @sanity_function
    def validate_download(self):
        stage_path = self.stagedir
        repo_path = stage_path.replace("stage","repo")
        return sn.assert_true(os.path.exists(f"{repo_path}/hpl_build_script.sh"))
=======
>>>>>>> 10539b53efb7951d09267d9d39b8f9d195eff5f0
