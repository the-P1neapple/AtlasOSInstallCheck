# AtlasOSInstallCheck
## A tool to check the integrity of the current Atlas OS installation

# Usage:
Download the requirements with `pip install -r requirements.txt`

Run the script with `py main.py <path to Atlas Playbook Directory>`

### Please run the script with Admin privileges to avoid any permission errors (even so, some may occur)

Note: this tool is still under developpement so bugs may still be present. If you find some, please take the time to report them

Moreover, this tool only checks registry entries and files.


# Planned additionnal features
- [x] Add compatibilty for AtlasOS 0.3.0
- [ ] Check task scheduler entries
- [ ] Check services
- [ ] Add Trusted Installer / SYSTEM privilege escalation to avoid any permission errors
- [ ] Add CLI arguments to only run specific checks

### To request additional features, or report bugs, please open an issue on the GitHub repository

# Support
This tool is meant to be used with the Atlas OS playbook, but should work with any other AME Wizard compatible playbooks. Use it at your own risk

# Credit
Huge thanks to the AME and Atlas OS team for their amazing work to unbloat Windows and make it more private.
- [Atlas OS](altasos.net)
- [AME Wizard](ameliorated.io)
