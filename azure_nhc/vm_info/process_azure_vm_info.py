#!/usr/bin/env python3
import json as js
#####################################################################################
### Output File
js_output_file = "azure_vm_info_processed_w_addons.json"
### Input File: original azure dataset
js_filename = "azure_vm_info.json"
### Input File: original NHC dataset
js_filename2 = "azure_vm_info_addon.json"

#####################################################################################

js_file = open(js_filename)
vm_data = js.load(js_file)

tmp_data = {}
for vm in vm_data:
#    print(vm["name"])
    if "resourceType" in vm and vm["resourceType"] == "virtualMachines":
        if vm["name"] not in tmp_data:
            tmp_data[vm["name"]] = vm

vm_data = tmp_data

js_file2 = open(js_filename2)
vm_data2 = js.load(js_file2)

mod_vm = vm_data

#adding the nhc data for vm families to the file
for vm in vm_data.keys():
    for vmt in vm_data2["family"].keys():
        if vm_data[vm]["family"] == vmt:
            mod_vm[vm]['nhc_values'] = vm_data2["family"][vmt]


#adding the vm specific exceptions for the nhc data
for vm in mod_vm.keys():
    for vmt in vm_data2["vm_sizes"].keys():
        if vmt == vm:
            for en in vm_data2["vm_sizes"][vmt].keys():
                mod_vm[vmt]['nhc_values'][en] = vm_data2["vm_sizes"][vmt][en]


with open(js_output_file, "w") as outfile:
        js.dump(mod_vm, outfile, indent=4)

