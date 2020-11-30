# Splunk Attack Range Local ⚔️

## Purpose 🛡
The Attack Range is a detection development platform, which solves three main challenges in detection engineering. First, the user is able to build quickly a small lab infrastructure as close as possible to a production environment. Second, the Attack Range performs attack simulation using different engines such as Atomic Red Team or Caldera in order to generate real attack data. Third, it integrates seamlessly into any Continuous Integration / Continuous Delivery (CI/CD) pipeline to automate the detection rule testing process.  

## Building 👷‍♂️

Attack Range can be built in three different ways:

- **locally** with vagrant and virtualbox
- **cloud** using terraform and AWS or Azure, see [attack_range](https://github.com/splunk/attack_range)
- **cloud-only** see [attack_range_cloud](https://github.com/splunk/attack_range_cloud/)

## Installation 🏗

### [For Ubuntu 18.04](https://github.com/splunk/attack_range_local/wiki/Ubuntu-18.04-Installation)

### [For MacOS](https://github.com/splunk/attack_range_local/wiki/MacOS-Installation)

## Architecture 🏯
![Logical Diagram](docs/attack_range_local_architecture.png)

The virtualized deployment of Attack Range consists of one or more of the following
systems:

- Windows Domain Controller
- Windows Server
- Windows Workstation
- A Kali Machine
- Splunk Server
- Phantom Server

More machines such as Phantom, Linux server, Linux client, MacOS clients are currently under development.

#### Logging
The following log sources are collected from the machines:

- Windows Event Logs (```index = win```)
- Sysmon Logs (```index = win```)
- Powershell Logs (```index = win```)
- Network Logs with Splunk Stream (```index = main```)
- Attack Simulation Logs from Atomic Red Team and Caldera (```index = attack```)

## Configuring the Attack Range
The configuration of the Attack Range is managed using the command
line program `psec` from the [python_secrets](https://pypi.org/project/python_secrets)
package.

All configuration settings are stored outside of the repository directory
preventing accidental leakage of secrets and allowing you to do things like
maintain multiple different configurations (e.g., for different sets of hosts
or different attack scenarios) and switch between them before building the
Attack Range.

### Creating an environment to hold configuration settings
After cloning the `attack_range_local` repository for the first time, you need
to bootstrap a new `python_secrets` _environment_ to store your configuration
settings. This environment will remain, even if you delete the repo directory
and re-clone it (e.g., to work on local modifications for Pull Requests).

To get going, create an environment by cloning from the group
descriptions in the directory `secrets.d`.

```
$ psec environments create --clone-from secrets.d
[+] environment 'attack_range_local' (/home/youraccount/.secrets/attack_range_local) created
```

You can see all of the variables and their descriptions, their group, and
other information, with `psec secrets describe`:

```
$ psec secrets describe --fit-width
+------------------------------------+---------------------------+----------+------------------------------------+------------------------------------+
| Variable                           | Group                     | Type     | Prompt                             | Options                            |
+------------------------------------+---------------------------+----------+------------------------------------+------------------------------------+
| windows_client_private_ip          | windows_client            | string   | Windows client private IP          | 10.0.1.17,*                        |
|                                    |                           |          | (terraform mode should be in       |                                    |
|                                    |                           |          | 10.0.1.0/24)                       |                                    |
| windows_client_os                  | windows_client            | string   | Windows client operating system    | Windows-10,*                       |
|                                    |                           |          | (Vagrant use 'Windows-10')         |                                    |
| windows_client_join_domain         | windows_client            | string   | Should the Windows client join the | 0,1                                |
|                                    |                           |          | Windows Domain                     |                                    |
| splunk_admin_password              | splunk_settings           | password | Password for Splunk 'admin' user   | *                                  |
             . . .
| phantom_server                     | environment               | string   | Enable a phantom server            | 0,1                                |
| windows_domain_controller          | environment               | string   | Enable a Windows Domain Controller | 1,0                                |
| windows_server                     | environment               | string   | Enable a Windows Server            | 0,1                                |
| kali_machine                       | environment               | string   | Enable a Kali Linux machine        | 0,1                                |
| windows_client                     | environment               | string   | Enable a Windows client (Vagrant   | 0,1                                |
|                                    |                           |          | only)                              |                                    |
| caldera_password                   | caldera                   | password | Caldera password for user 'admin'  | *                                  |
+------------------------------------+---------------------------+----------+------------------------------------+------------------------------------+
```

When you want to change the values of one or more variables later, you may get
prompted with the string in `Prompt` and may be presented options you can enter
from `Options`.  The first option in the list will be used to set "default"
values for some variables in just a minute.

> **NOTE**: Variables of type `password` can be set manually, but do not have
> defaults. You either generate a new random value, or manually set a desired
> value. This mitigates "default password" security problems and leakage of
> secrets through accidental commits.

### Initial Configuration
After cloning a new environment, no variables are set (just defined,
as shown above). If you show the values of variables with the
`secrets show --no-redact` subcommand, they show up at first
as `None`. Here are just the two seen in the output above:

```
$ psec secrets show --no-redact win_password splunk_admin_password
+-----------------------+-------+-----------------------+
| Variable              | Value | Export                |
+-----------------------+-------+-----------------------+
| splunk_admin_password | None  | splunk_admin_password |
| win_password          | None  | win_password          |
+-----------------------+-------+-----------------------+
```

Generate a secure, single common password for all variables like these
with the type `password`, then set all of the rest of the variables of type
`string` to their defaults, with the following command:

```
$ psec secrets generate && psec secrets set --from-options
```

At this point, you are ready to build the Attack Range with
default settings and secure unique passwords.

```
$ psec secrets show --no-redact --type password
+----------------------------+----------------------------+----------------------------+
| Variable                   | Value                      | Export                     |
+----------------------------+----------------------------+----------------------------+
| splunk_admin_password      | versus.exhume.shield.trial | splunk_admin_password      |
| phantom_community_password | versus.exhume.shield.trial | phantom_community_password |
| phantom_admin_password     | versus.exhume.shield.trial | phantom_admin_password     |
| win_password               | versus.exhume.shield.trial | win_password               |
| caldera_password           | versus.exhume.shield.trial | caldera_password           |
+----------------------------+----------------------------+----------------------------+
```

> **NOTE**: When Ansible is configuring Windows VMs, it may fail due to the
> Windows password policy requiring greater complexity. If this happens, you may
> need to set a separate password for the Windows host.

```
$ psec secrets set win_password='#Versus1Exhume2Shield3Trial!'
```

### Changing the configuration
The variables controlling which systems are enabled are found in the
`environment` group.

Defaults are defined by the first item in the list of `Options` for
each variable. The only system enabled by default in this case is
the `windows_domain_controller` system.

```
$ psec secrets describe --group environment
+---------------------------+-------------+--------+----------------------------------------+---------+
| Variable                  | Group       | Type   | Prompt                                 | Options |
+---------------------------+-------------+--------+----------------------------------------+---------+
| phantom_server            | environment | string | Enable a phantom server                | 0,1     |
| windows_domain_controller | environment | string | Enable a Windows Domain Controller     | 1,0     |
| windows_server            | environment | string | Enable a Windows Server                | 0,1     |
| kali_machine              | environment | string | Enable a Kali Linux machine            | 0,1     |
| windows_client            | environment | string | Enable a Windows client (Vagrant only) | 0,1     |
+---------------------------+-------------+--------+----------------------------------------+---------+
```

You can see the current settings with this command:

```
$ psec secrets show --no-redact --group environment
+---------------------------+-------+---------------------------+
| Variable                  | Value | Export                    |
+---------------------------+-------+---------------------------+
| phantom_server            | 0     | phantom_server            |
| windows_domain_controller | 1     | windows_domain_controller |
| windows_server            | 0     | windows_server            |
| kali_machine              | 0     | kali_machine              |
| windows_client            | 0     | windows_client            |
+---------------------------+-------+---------------------------+
```

To enable a system, set its variable to the value `1`:

```
$ psec secrets set kali_machine=1
```

## Running 🏃‍♀️
Attack Range supports different actions:

- Build Attack Range
- Perform Attack Simulation
- Destroy Attack Range
- Stop Attack Range
- Resume Attack Range
- Dump Attack Data

### Build Attack Range Local
- Build Attack Range Local
```
python attack_range_local.py -a build
```

### Perform Attack Simulation
- Perform Attack Simulation
```
python attack_range_local.py -a simulate -st T1003.001 -t attack-range-windows-domain-controller
```

### Show Attack Range Status
- Show Attack Range Status
```
python attack_range_local.py -lm
```

### Destroy Attack Range Local
- Destroy Attack Range Local
```
python attack_range_local.py -a destroy
```

### Stop Attack Range Local
- Stop Attack Range Local
```
python attack_range_local.py -a stop
```

### Resume Attack Range Local
- Resume Attack Range Local
```
python attack_range_local.py -a resume
```

## Dump Attack Data
- Dump Attack Range Data
```
python attack_range_local.py -a dump -dn dump_data_folder
```

## Features 💍
- [Splunk Server](https://github.com/splunk/attack_range/wiki/Splunk-Server)
  * Indexing of Microsoft Event Logs, PowerShell Logs, Sysmon Logs, DNS Logs, ...
  * Preconfigured with multiple TAs for field extractions
  * Out of the box Splunk detections with Enterprise Security Content Update ([ESCU](https://splunkbase.splunk.com/app/3449/)) App
  * Preinstalled Machine Learning Toolkit ([MLTK](https://splunkbase.splunk.com/app/2890/))
  * Splunk UI available through port 8000 with user admin
  * ssh connection over configured ssh key

- [Splunk Enterprise Security](https://splunkbase.splunk.com/app/263/)
  * [Splunk Enterprise Security](https://splunkbase.splunk.com/app/263/) is a premium security solution requiring a paid license.
  * Enable or disable [Splunk Enterprise Security](https://splunkbase.splunk.com/app/263/) in [attack_range.conf](attack_range.conf)
  * Purchase a license, download it and store it in the apps folder to use it.

- [Splunk Phantom](https://www.splunk.com/en_us/software/splunk-security-orchestration-and-automation.html)
  * [Splunk Phantom](https://www.splunk.com/en_us/software/splunk-security-orchestration-and-automation.html) is a Security Orchestration and Automation platform
  * For a free development license (100 actions per day) register [here](https://my.phantom.us/login/?next=/)
  * Enable or disable [Splunk Phantom](https://www.splunk.com/en_us/software/splunk-security-orchestration-and-automation.html) in [attack_range.conf](attack_range.conf)

- [Windows Domain Controller & Window Server & Windows 10 Client](https://github.com/splunk/attack_range/wiki/Windows-Infrastructure)
  * Can be enabled, disabled and configured over [attack_range.conf](attack_range.conf)
  * Collecting of Microsoft Event Logs, PowerShell Logs, Sysmon Logs, DNS Logs, ...
  * Sysmon log collection with customizable Sysmon configuration
  * RDP connection over port 3389 with user Administrator

- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)
  * Attack Simulation with [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)
  * Will be automatically installed on target during first execution of simulate
  * Atomic Red Team already uses the new Mitre sub-techniques

- [Caldera](https://github.com/mitre/caldera)
  * Adversary Emulation with [Caldera](https://github.com/mitre/caldera)
  * Installed on the Splunk Server and available over port 8888 with user admin
  * Preinstalled Caldera agents on windows machines

- [Kali Linux](https://www.kali.org/)
  * Preconfigured Kali Linux machine for penetration testing
  * ssh connection over configured ssh key


## Support 📞
Please use the [GitHub issue tracker](https://github.com/splunk/attack_range/issues) to submit bugs or request features.

If you have questions or need support, you can:

* Post a question to [Splunk Answers](http://answers.splunk.com)
* Join the [#security-research](https://splunk-usergroups.slack.com/archives/C1S5BEF38) room in the [Splunk Slack channel](http://splunk-usergroups.slack.com)
* If you are a Splunk Enterprise customer with a valid support entitlement contract and have a Splunk-related question, you can also open a support case on the https://www.splunk.com/ support portal

## Contributing 🥰
We welcome feedback and contributions from the community! Please see our [contribution guidelines](docs/CONTRIBUTING.md) for more information on how to get involved.

## Author
* [Jose Hernandez](https://twitter.com/d1vious)
* [Patrick Bareiß](https://twitter.com/bareiss_patrick)

## Contributors
* [Bhavin Patel](https://twitter.com/hackpsy)
* [Rod Soto](https://twitter.com/rodsoto)
* Russ Nolen
* Phil Royer
* [Joseph Zadeh](https://twitter.com/JosephZadeh)
* Rico Valdez
* [Dimitris Lambrou](https://twitter.com/etz69)
* [Dave Herrald](https://twitter.com/daveherrald)
* [Kai Seidenschnur](https://www.linkedin.com/in/kai-seidenschnur-ab42889a)


## License

Copyright 2020 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
