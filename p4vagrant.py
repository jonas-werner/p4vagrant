#####################################################
#          ___                                  _
#         /   |                                | |
#  _ __  / /| |_   ____ _  __ _ _ __ __ _ _ __ | |_
# | '_ \/ /_| \ \ / / _` |/ _` | '__/ _` | '_ \| __|
# | |_) \___  |\ V / (_| | (_| | | | (_| | | | | |_
# | .__/    |_/ \_/ \__,_|\__, |_|  \__,_|_| |_|\__|
# | |                      __/ |
# |_|                     |___/
#####################################################
# Title:    p4vagrant
# Version:  1.6
# Author:   Jonas Werner
#####################################################

from flask import Flask, jsonify, request
from subprocess import Popen, PIPE
import os
import json

app = Flask(__name__)
debug = 1


# Vagrant command functions
################################################

# Get vms
def cmdGetVms():

    vmList = []

    process = Popen(['vboxmanage', 'list', 'vms'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    stdout = stdout.decode() # stdout is in bytes format, decode to str
    entries = stdout.split() # Split on space

    for entry in entries:
        if '"' in entry: # Only VMs will have the quotation, so filter on that
            vmList.append(entry.strip('"'))

    return vmList


# Get vms
def cmdGetRunningVms():

    vmList = []

    process = Popen(['vboxmanage', 'list', 'runningvms'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    stdout = stdout.decode() # stdout is in bytes format, decode to str
    entries = stdout.split() # Split on space

    for entry in entries:
        if '"' in entry: # Only VMs will have the quotation, so filter on that
            vmList.append(entry.strip('"'))

    return vmList


# Get boxes
def cmdGetBoxes():

    boxList = []

    process = Popen(['vagrant', 'box', 'list'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    stdout = stdout.decode() # stdout is in bytes format, decode to str
    lines = stdout.split('\n') # split into lines and create list format

    for box in range(0, len(lines)-1):
        boxName = lines[box].partition(' ')[0] # grab first "word" which is the box name
        boxList.append(boxName)

    return boxList


# Create Vagrant VM
def cmdVmDeploy(name, box, ip):

    # Set our file and directory names
    vagrantBaseDir  = "/home/jonas/ENV/VAGRANT"
    template        = os.path.join(vagrantBaseDir, "templates/VagrantTemplateBasic")
    fullPath        = os.path.join(vagrantBaseDir, name)
    filename        = os.path.join(fullPath, "Vagrantfile")

    # Create directory
    if not os.path.exists(fullPath):
        if debug: print("Creating %s" % fullPath)
        os.makedirs(fullPath)

    # Read in the template
    with open(template, 'r') as file :
      vagrantFile = file.read()

    # Replace placeholders with real values for this VM
    vagrantFile = vagrantFile.replace('PARSENAME', name)
    vagrantFile = vagrantFile.replace('PARSEBOX', box)
    vagrantFile = vagrantFile.replace('PARSEIP', ip)

    # Write the new Vagrantfile
    with open(filename, 'w') as file:
      file.write(vagrantFile)

    # Vagrant up
    process = Popen(['vagrant', 'up'], cwd=fullPath, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    stdout = stdout.decode() # stdout is in bytes format, decode to str

    print("%s" % stdout)




# REST Endpoints:
############################################

# Get vms API endpoint
@app.route('/api/v1/vagrant/view',methods=['GET'])
def vagrantVmView():
    req = request.args
    command = req['cmd']

    if command == "vms":
        vmList = cmdGetVms()
        vmOutput = json.dumps(vmList)
        returnCode = 200

    elif command == "runningvms":
        vmList = cmdGetRunningVms()
        vmOutput = json.dumps(vmList)
        returnCode = 200

    elif command == "boxes":
        boxList = cmdGetBoxes()
        vmOutput = json.dumps(boxList)
        returnCode = 200

    else:
        contOutput = "Invalid command provided. Plz try again."
        returnCode = 400

    returnData  = vmOutput
    code        = returnCode

    return returnData, code


# Deploy VM API endpoint
@app.route('/api/v1/vagrant/deploy',methods=['GET'])
def vagrantVmDeploy():
    req     = request.args
    name    = req['boxName']
    box     = req['boxImage']
    ip      = req['boxIp']

    output = cmdVmDeploy(name, box, ip)
    vmOutput = json.dumps(output)
    returnCode = 201

    returnData  = vmOutput
    code        = returnCode

    return returnData, code




if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=int(os.getenv('PORT', '5200')))
