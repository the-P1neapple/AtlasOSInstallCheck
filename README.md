# AtlasOSInstallCheck
## A tool to check the integrity of the current Atlas OS installation

# Usage:
Download the requirements with `pip install -r requirements.txt`

Run the script with `run.cmd <path to Atlas Playbook (.apbx or extracted directory)> [-r] [-f] [-s] [-t] [-y]`

Parameters description :
- `-r` : Check registry entries
- `-f` : Check files
- `-s` : Check services
- `-t` : Check task scheduler entries
- `-y` : Skip confirmation prompts

If no parameters are specified, all checks will be run

### Please run the script with Admin privileges to avoid any permission errors (even so, some may occur)

Note: this tool is still under developpement so bugs may still be present. If you find some, please take the time to report them


# Planned additionnal features
- [x] Add compatibilty for AtlasOS 0.3.0
- [x] Check task scheduler entries
- [x] Check services
- [x] Add Trusted Installer / SYSTEM privilege escalation to avoid any permission errors
- [x] Kill related programs when deleting files
- [x] Add CLI arguments to only run specific checks

### To request additional features, or report bugs, please open an issue on the GitHub repository

# Support
This tool is meant to be used with the Atlas OS playbook, but should work with any other AME Wizard compatible playbooks. Use it at your own risk

# Credit
Huge thanks to the AME and Atlas OS team for their amazing work to unbloat Windows and make it more private.
- [Atlas OS](https://atlasos.net/)
- [AME Wizard](https://ameliorated.io/)
- Credit to the Atlas OS team for the RunAsTI.cmd script
