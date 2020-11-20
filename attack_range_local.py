import os
import sys
import argparse
from modules import logger
from pathlib import Path
from psec.secrets import SecretsEnvironment
from modules.CustomConfigParser import CustomConfigParser
from modules.VagrantController import VagrantController


# need to set this ENV var due to a OSX High Sierra forking bug
# see this discussion for more details: https://github.com/ansible/ansible/issues/34056#issuecomment-352862252
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

# Identify the default python_secrets environment that will
# be used. In the simple case, it will be same as the current
# directory ("attack_range_local" for normal clone.)
# Change with 'psec environments default' if you want to
# change the default, or select the environment you want
# to use. See also 'psec environments help'.
default_environment = SecretsEnvironment().environment()
VERSION = 1


if __name__ == "__main__":
    # grab arguments
    parser = argparse.ArgumentParser(description="starts a attack range ready to collect attack data into splunk")
    parser.add_argument("-a", "--action", required=False, choices=['build', 'destroy', 'simulate', 'stop', 'resume', 'dump'],
                        help="action to take on the range, defaults to \"build\", build/destroy/simulate/stop/resume allowed")
    parser.add_argument("-t", "--target", required=False,
                        help="target for attack simulation. For mode vagrant use name of the vbox")
    parser.add_argument("-e", "--environment", required=False, default=default_environment,
                        help="environment to use for configuration settings")
    parser.add_argument("-st", "--simulation_technique", required=False, type=str, default="",
                        help="comma delimited list of MITRE ATT&CK technique ID to simulate in the attack_range, example: T1117, T1118, requires --simulation flag")
    parser.add_argument("-sa", "--simulation_atomics", required=False, type=str, default="",
                        help="specify dedicated Atomic Red Team atomics to simulate in the attack_range, example: Regsvr32 remote COM scriptlet execution for T1117")
    parser.add_argument("-lm", "--list_machines", required=False, default=False, action="store_true", help="prints out all available machines")
    parser.add_argument("-dn", "--dump_name", required=False, help="define the dump name")
    parser.add_argument("-v", "--version", default=False, action="store_true", required=False,
                        help="shows current attack_range version")

    # parse them
    args = parser.parse_args()
    ARG_VERSION = args.version
    action = args.action
    environment = args.environment
    target = args.target
    simulation_techniques = args.simulation_technique
    simulation_atomics = args.simulation_atomics
    list_machines = args.list_machines
    dump_name = args.dump_name

    print("""
starting program loaded for B1 battle droid
          ||/__'`.
          |//()'-.:
          |-.||
          |o(o)
          |||\\\  .==._
          |||(o)==::'
           `|T  ""
            ()
            |\\
            ||\\
            ()()
            ||//
            |//
           .'=`=.
    """)

    # Load configuration from default python-secrets environment
    # and export them environment variables for programs running
    # in child processes (e.g., Vagrant) to access.
    env = SecretsEnvironment(environment=environment,
                             export_env_vars=True)
    if not env.environment_exists():
        print((f"ERROR: environment '{str(env)}' does not exist "
               "(try 'psec environments list'?)"), file=sys.stderr)
        sys.exit(1)

    env.read_secrets()
    print(f"attack_range is using python_secrets environment '{str(env)}'")
    config = env._secrets

    log = logger.setup_logging(config['log_path'], config['log_level'])
    log.info("INIT - attack_range v" + str(VERSION))

    if ARG_VERSION:
        log.info("version: {0}".format(VERSION))
        sys.exit(0)

    if not action and not list_machines:
        log.error('ERROR: Use -a to perform an action or -lm to list available machines')
        sys.exit(1)

    if action == 'simulate' and not target:
        log.error('ERROR: Specify target for attack simulation')
        sys.exit(1)

    if action == 'dump' and not dump_name:
        log.error('ERROR: Specify --dump_name for dump command')
        sys.exit(1)


    # lets give CLI priority over config file for pre-configured techniques
    if simulation_techniques:
        pass
    else:
        simulation_techniques = config['art_run_techniques']

    if not simulation_atomics:
        simulation_atomics = 'no'

    controller = VagrantController(config, log)

    if list_machines:
        controller.list_machines()
        sys.exit(0)

    if action == 'build':
        controller.build()

    if action == 'destroy':
        controller.destroy()

    if action == 'stop':
        controller.stop()

    if action == 'resume':
        controller.resume()

    if action == 'simulate':
        controller.simulate(target, simulation_techniques, simulation_atomics)

    if action == 'dump':
        controller.dump(dump_name)


# rnfgre rtt ol C4G12VPX
