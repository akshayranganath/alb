"""
Copyright 2017 Akamai Technologies, Inc. All Rights Reserved.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import argparse
import configparser
import json
import logging
import os
import requests
import shutil
import sys

from akamai.edgegrid import EdgeGridAuth, EdgeRc
from cloudlet_api_wrapper import Cloudlet


"""
This code leverages Akamai OPEN API. to control Visitor Prioritization cloudlets.
In case you need quick explanation contact the initiators.
Initiators: vbhat@akamai.com and aetsai@akamai.com
"""

PACKAGE_VERSION = "0.1.0"

# Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')
log_file = os.path.join('logs', 'visitor-prioritization.log')

# Set the format of logging in console and file separately
log_formatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
console_formatter = logging.Formatter("%(message)s")
root_logger = logging.getLogger()

logfile_handler = logging.FileHandler(log_file, mode='w')
logfile_handler.setFormatter(log_formatter)
root_logger.addHandler(logfile_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)
# Set Log Level to DEBUG, INFO, WARNING, ERROR, CRITICAL
root_logger.setLevel(logging.INFO)


def init_config(edgerc_file, section):
    if not edgerc_file:
        if not os.getenv("AKAMAI_EDGERC"):
            edgerc_file = os.path.join(os.path.expanduser("~"), '.edgerc')
        else:
            edgerc_file = os.getenv("AKAMAI_EDGERC")

    if not os.access(edgerc_file, os.R_OK):
        root_logger.error("Unable to read edgerc file \"%s\"" % edgerc_file)
        exit(1)

    if not section:
        if not os.getenv("AKAMAI_EDGERC_SECTION"):
            section = "cloudlets"
        else:
            section = os.getenv("AKAMAI_EDGERC_SECTION")

    try:
        edgerc = EdgeRc(edgerc_file)
        base_url = edgerc.get(section, 'host')

        session = requests.Session()
        session.auth = EdgeGridAuth.from_edgerc(edgerc, section)

        return base_url, session
    except configparser.NoSectionError:
        root_logger.error("Edgerc section \"%s\" not found" % section)
        exit(1)
    except Exception:
        root_logger.info(
            "Unknown error occurred trying to read edgerc file (%s)" %
            edgerc_file)
        exit(1)


def cli():
    prog = get_prog_name()
    if len(sys.argv) == 1:
        prog += " [command]"

    parser = argparse.ArgumentParser(
        description='Akamai CLI for Visitor Prioritization',
        add_help=False,
        prog=prog)
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s ' +
                PACKAGE_VERSION)

    subparsers = parser.add_subparsers(
        title='Commands', dest="command", metavar="")

    actions = {}

    subparsers.add_parser(
        name="help",
        help="Show available help",
        add_help=False).add_argument(
        'args',
        metavar="",
        nargs=argparse.REMAINDER)

    actions["setup"] = create_sub_command(
        subparsers,
        "setup",
        "Initial setup to download all necessary policy "
        "information")

    actions["show"] = create_sub_command(
        subparsers, "show",
        "Display general policy details, active policy versions, "
        "or specific policy version details",
        [{"name": "version", "help": "Version number of the policy"},
         {"name": "verbose",
          "help": "Display detailed rule information for a specific version",
          "action": "store_true"},
         {"name": "from-version",
          "help":
              "Display policy versions starting from the version number specified"}],
        [{"name": "policy", "help": "Policy name"}])

    actions["download"] = create_sub_command(
        subparsers, "download",
        "Download the policy version rules json and output to "
        "rules folder. (Optionally, use --output-file to specify "
        "location of outputfile)",
        [{"name": "output-file",
          "help": "Output filename to store the rules"}],
        [{"name": "policy", "help": "Policy name"},
         {"name": "version", "help": "Version number of the policy"}])

    actions["create-version"] = create_sub_command(
        subparsers, "create-version",
        "Create a new policy version using a local file from the "
        "rules folder with name <policy>.json",
        [{"name": "force", "help": "Do not prompt for user confirmation",
          "action": "store_true"}],
        [{"name": "policy", "help": "Policy name"},
         {"name": "file", "help": "File path for input rules file"}])

    actions["activate"] = create_sub_command(
        subparsers, "activate", "Activate a specific policy version",
        [{"name": "policy", "help": "Policy name"}],
        [{"name": "network",
          "help": "Network to be activated on (case-insensitive).",
          "type": str.lower, "choices": {"staging", "production"}},
         {"name": "version", "help": "Version number of the policy"}])

    actions["throttle"] = create_sub_command(
        subparsers, "throttle", "Throttle traffic by rule name",
        [{"name": "percent", "help": "Throttle percentage (-1 to 100)"},
         {"name": "disable", "help": "Disable all throttling",
          "action": "store_true"},
         {"name": "network",
          "help": "Network to be activated on (case-insensitive).",
          "type": str.lower, "choices": {"staging", "production"}},
         {"name": "rule",
          "help":
              "Rule name to update (use 'single quotes' to honor "
              "spaces in rule name))"},
         {"name": "force", "help": "Do not prompt for user confirmation",
          "action": "store_true"}],
        [{"name": "policy", "help": "Policy name"}])

    actions["list"] = create_sub_command(
        subparsers, "list", "List all Visitor Prioritization policy names")

    args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_help()
        return 0

    if args.command == "help":
        if len(args.args) > 0:
            if actions[args.args[0]]:
                actions[args.args[0]].print_help()
        else:
            parser.prog = get_prog_name() + " help [command]"
            parser.print_help()
        return 0

    if args.command != "setup":
        confirm_setup(args)

    return getattr(sys.modules[__name__], args.command.replace("-", "_"))(args)


def create_sub_command(
        subparsers,
        name,
        help,
        optional_arguments=None,
        required_arguments=None):
    action = subparsers.add_parser(name=name, help=help, add_help=False)

    if required_arguments:
        required = action.add_argument_group("required arguments")
        for arg in required_arguments:
            name = arg["name"]
            del arg["name"]
            required.add_argument("--" + name,
                                  required=True,
                                  **arg,
                                  )

    optional = action.add_argument_group("optional arguments")
    if optional_arguments:
        for arg in optional_arguments:
            name = arg["name"]
            del arg["name"]
            optional.add_argument("--" + name,
                                  required=False,
                                  **arg,
                                  )

    optional.add_argument(
        "--edgerc",
        help="Location of the credentials file [$AKAMAI_EDGERC]",
        default=os.path.join(
            os.path.expanduser("~"),
            '.edgerc'))

    optional.add_argument(
        "--section",
        help="Section of the credentials file [$AKAMAI_EDGERC_SECTION]",
        default="cloudlets")

    optional.add_argument(
        "--debug",
        help="DEBUG mode to generate additional logs for troubleshooting",
        action="store_true")

    return action


def setup(args):
    base_url, session = init_config(args.edgerc, args.section)

    root_logger.info('Setting up required files... please wait')
    # Create the wrapper object to make calls
    cloudlet_object = Cloudlet(base_url)
    group_response = cloudlet_object.list_cloudlet_groups(session)
    root_logger.info('Processing groups...')
    if group_response.status_code == 200:
        group_path = 'groups'
        # Delete the groups folder before we start
        if os.path.exists('groups'):
            shutil.rmtree('groups')
        if not os.path.exists(group_path):
            os.makedirs(group_path)
        with open(os.path.join(group_path, 'groups.json'), 'w') as group_file:
            groups_response_json = group_response.json()
            # Find number of groups using len function
            total_groups = len(groups_response_json)
            group_output = []
            for every_group in groups_response_json:
                group_info = {'groupName': every_group['groupName'], 'groupId': every_group['groupId']}
                group_output.append(group_info)
            group_file.write(json.dumps(group_output, indent=4))

        policy_path = os.path.join(get_cache_dir(), 'policies')
        policies_list = []
        # Delete the policies folder before we start
        if os.path.exists('policies'):
            shutil.rmtree('policies')
        if not os.path.exists(policy_path):
            os.makedirs(policy_path)
        root_logger.info('Total groups found: ' + str(total_groups))
        root_logger.info('Fetching VP cloudlet policies under each group..')
        counter = 1
        for every_group in group_response.json():
            group_id = every_group['groupId']
            group_name = every_group['groupName']
            root_logger.info('Processing ' + str(counter) + ' of ' + str(total_groups) +
                             ' groups, groupId and name is: ' + str(group_id) + ': ' + group_name)
            counter += 1
            cloudlet_policies = cloudlet_object.list_policies(
                session=session, group_id=group_id, cloudlet_code='VP')
            if cloudlet_policies.status_code == 200:
                for every_policy in cloudlet_policies.json():
                    policy_name = every_policy['name'] + '.json'
                    root_logger.debug('Generating policy file: ' + policy_name)
                    policy_details = {'name': every_policy['name'], 'description': every_policy['description'],
                                      'policyId': every_policy['policyId'], 'groupId': every_policy['groupId']}
                    if every_policy['name'] not in policies_list:
                        policies_list.append(every_policy['name'])
                        with open(os.path.join(policy_path, policy_name), 'w') as policy_file_handler:
                            policy_file_handler.write(
                                json.dumps(policy_details, indent=4))
                    else:
                        # This policy is already processed so move on
                        root_logger.debug(
                            'Duplicate policy in another group again ' +
                            every_policy['name'])
                        pass
            else:
                root_logger.debug('groupId: ' + str(group_id) + ' has no policy details')
        root_logger.info(
            '\nFound these policies below and stored in ' +
            policy_path +
            " folder:")
        for every_policy_name in policies_list:
            root_logger.info(every_policy_name)

    return 0


def show(args):
    base_url, session = init_config(args.edgerc, args.section)

    policy = args.policy
    version = args.version
    verbose = args.verbose
    from_version = args.from_version

    cloudlet_object = Cloudlet(base_url)
    policies_folder = os.path.join(get_cache_dir(), 'policies')
    for root, dirs, files in os.walk(policies_folder):
        local_policy_file = policy + '.json'
        if local_policy_file in files:
            with open(os.path.join(policies_folder, local_policy_file), mode='r') as policy_file_handler:
                policy_string_content = policy_file_handler.read()
            policy_json_content = json.loads(policy_string_content)
            policy_policy_id = policy_json_content['policyId']
            root_logger.info('Fetching policy details...')
            if version:
                policy_detail = cloudlet_object.get_cloudlet_policy(
                    session, policy_policy_id, version=args.version)
                root_logger.debug(json.dumps(policy_detail.json()))
                every_version_detail = policy_detail.json()
                if policy_detail.status_code == 200:
                    if not every_version_detail['deleted']:
                        root_logger.info('\nDetails of version: ' +
                                         str(every_version_detail['version']))
                        root_logger.info(
                            'Policy created by: ' +
                            every_version_detail['createdBy'] +
                            '\n')
                        # Need to check for match rules, sometimes we see null
                        # values
                        if every_version_detail['matchRules'] is not None:
                            if not verbose:
                                for every_match_rule in every_version_detail['matchRules']:
                                    # Loop each match condition within each rule
                                    # Check whether rules is disabled, if yes
                                    # display accordingly
                                    if 'disabled' in every_match_rule and every_match_rule['disabled'] is True:
                                        status = 'DISABLED'
                                    else:
                                        status = 'ACTIVE'
                                    root_logger.info('   ' +
                                          every_match_rule['name'] +
                                          ' -> ' +
                                          str(every_match_rule['passThroughPercent']) +
                                          ' -> ' +
                                          status)
                                root_logger.info(
                                    '\nNOTE: You can pass --verbose as an additional argument to get detailed rule '
                                    'information')
                            if verbose:
                                root_logger.info(
                                    '     Match Criteria and Rule Details are: ')
                                root_logger.info(
                                    '\n       ----------------------------------------------       \n')
                                for every_match_rule in every_version_detail['matchRules']:
                                    multiple_matches = 0
                                    root_logger.info(
                                        '       Rule Name: ' + every_match_rule['name'])
                                    root_logger.info(
                                        '       Traffic Percentage: ' + str(every_match_rule['passThroughPercent']))
                                    root_logger.info('')
                                    # Loop each match conditon within each rule
                                    for every_match_condition in every_match_rule['matches']:
                                        if multiple_matches == 1:
                                            root_logger.info('       AND')
                                        root_logger.info(
                                            '       Match Type: ' + every_match_condition['matchType'])
                                        root_logger.info(
                                            '       Match Value: ' + every_match_condition['matchValue'])
                                        multiple_matches = 1
                                    # Check wthether rules is disabled, if yes
                                    # display accordingly
                                    if 'disabled' in every_match_rule and every_match_rule['disabled'] is True:
                                        root_logger.info(
                                            '\n       Rule is DISABLED')
                                    else:
                                        root_logger.info(
                                            '\n       Rule is ACTIVE')
                                    root_logger.info(
                                        '\n       ----------------------------------------------       \n')
                        else:
                            root_logger.info('\nThere are no match criteria for this rule\n')
                else:
                    root_logger.info('Requested policy version does not exist - please check version number')
            else:
                policy_details = cloudlet_object.get_cloudlet_policy(
                    session, policy_policy_id)
                root_logger.info('\nPolicy Details:')
                root_logger.info('-----------------')
                root_logger.info(
                    'Policy Description: ' +
                    policy_details.json()['description'] +
                    '\n')
                for every_activation_detail in policy_details.json()['activations']:
                    if every_activation_detail['policyInfo']['status'] == 'active':
                        root_logger.info('Version ' +
                                         str(every_activation_detail['policyInfo']['version']) +
                                         ' is live in ' +
                                         str(every_activation_detail['network']) +
                                         ' for configuration: ' +
                                         str(every_activation_detail['propertyInfo']['name']) +
                                         ' v' +
                                         str(every_activation_detail['propertyInfo']['version']))

                if not from_version:
                    policy_versions = cloudlet_object.list_policy_versions(
                        session, policy_policy_id, page_size='10')
                    root_logger.info(
                        '\nFetching last 10 policy version details... You can pass --from-version to list more versions.')
                else:
                    policy_versions = cloudlet_object.list_policy_versions(
                        session, policy_policy_id)
                    root_logger.info(
                        '\nShowing policy version details from version ' +
                        str(from_version))
                root_logger.info('\nVersion Details (Version : Description)')
                root_logger.info('------------------------------------------')
                for every_version in policy_versions.json():
                    if from_version:
                        if int(every_version['version']) >= int(from_version):
                            root_logger.info(
                                str(every_version['version']) + ' : ' +
                                str(every_version['description']))
                    else:
                        root_logger.info(
                            str(every_version['version']) + ' : ' +
                            str(every_version['description']))

                root_logger.info(
                    '\nNOTE: You can pass --version <version_number> as an additional argument to get version specific '
                    'details\n')

        else:
            root_logger.info(
                '\nLocal datastore does not have this policy. Please double check policy name or run "setup" first')
            exit(1)


def download(args):
    base_url, session = init_config(args.edgerc, args.section)

    policy = args.policy
    version = args.version
    output_file = args.output_file

    cloudlet_object = Cloudlet(base_url)
    policies_folder = os.path.join(get_cache_dir(), 'policies')
    for root, dirs, files in os.walk(policies_folder):
        local_policy_file = policy + '.json'
        if local_policy_file in files:
            with open(os.path.join(policies_folder, local_policy_file), mode='r') as policy_file_handler:
                policy_string_content = policy_file_handler.read()
            policy_json_content = json.loads(policy_string_content)
            policy_policy_id = policy_json_content['policyId']
            root_logger.info('\nFetching policy rule details...')
            policy_details = cloudlet_object.get_cloudlet_policy(
                session, policy_policy_id, version=version)
            if policy_details.status_code == 200:
                # Update the local copy to latest details
                new_policy_folder = 'rules'
                if output_file:
                    output_filename = os.path.join(
                        new_policy_folder, output_file)
                else:
                    if not os.path.exists(new_policy_folder):
                        os.makedirs(new_policy_folder)
                    new_policy_file = policy + '_rules.json'
                    output_filename = os.path.join(
                        new_policy_folder, new_policy_file)
                policy_details_to_file = {}
                every_detail_of_policy = policy_details.json()
                if 'description' in every_detail_of_policy:
                    policy_details_to_file['description'] = every_detail_of_policy['description']
                if 'matchRules' in every_detail_of_policy:
                    # Check whether it is null value
                    if every_detail_of_policy['matchRules'] is not None:
                        match_rules_section = every_detail_of_policy['matchRules']
                        for every_match_rule in match_rules_section:
                            if 'location' in every_match_rule:
                                del every_match_rule['location']
                        policy_details_to_file['matchRules'] = every_detail_of_policy['matchRules']
                if 'description' in every_detail_of_policy is None:
                    policy_details_to_file['description'] = 'This is a version created using API'

                with open(output_filename, mode='w') as policy_file_handler:
                    policy_file_handler.write(json.dumps(
                        policy_details_to_file, indent=4))
                root_logger.info(
                    '\nGenerated policy rule details in json format. File output location is: ' +
                    output_filename)
            else:
                root_logger.info(
                    'Unable to fetch version details. Check the version number')
                return 1
        else:
            root_logger.info(
                '\nLocal datastore does not have this policy. Please double check policy name or run "setup" first')
            return 1

    return 0


def create_version(args):
    base_url, session = init_config(args.edgerc, args.section)

    if not args.force:
        root_logger.info(
            '\nThe description field will be used as comments for this version\n')
        root_logger.info(
            '\nDoes your rules json file have the proper description field updated? [y/N]\n')
        if not str.lower(input()) == "y":
            root_logger.info(
                '\nExiting the program, you may run it again after updating description\n')
            return 1

    policy = args.policy
    file = args.file

    cloudlet_object = Cloudlet(base_url)
    policies_folder = os.path.join(get_cache_dir(), 'policies')
    for root, dirs, files in os.walk(policies_folder):
        local_policy_file = policy + '.json'
        if local_policy_file in files:
            root_logger.info(
                'Found policy: ' +
                policy +
                ' and using policyId from local store...')
            with open(os.path.join(policies_folder, local_policy_file), mode='r') as policy_file_handler:
                policy_string_content = policy_file_handler.read()
            policy_json_content = json.loads(policy_string_content)
            policy_policy_id = policy_json_content['policyId']

            new_policy_folder = 'rules'
            new_policy_file = policy + '_rules.json'
            if file:
                custom_file = file
                rules_file = os.path.join(new_policy_folder, custom_file)
            else:
                root_logger.info(
                    '\n--file option was not specified. Picking rules file from: ' +
                    os.path.join(
                        new_policy_folder,
                        new_policy_file))
                rules_file = os.path.join(new_policy_folder, new_policy_file)
            try:
                with open(rules_file, mode='r') as policy_data:
                    policy_details = json.load(policy_data)
                    policy_details_json = json.dumps(policy_details)
                policy_create_response = cloudlet_object.create_policy_version(
                    session, policy_id=policy_policy_id)
                root_logger.info(
                    'Trying to create a new version of this policy...')
                if policy_create_response.status_code == 200 or 201:
                    new_version = policy_create_response.json()['version']
                    policy_update_response = cloudlet_object.update_policy_version(
                        session, policy_policy_id, policy_details_json, new_version)
                    if policy_update_response.status_code == 200:
                        root_logger.info(
                            'Success! Created policy version number ' + str(
                                policy_update_response.json()['version']))
                    else:
                        root_logger.info(
                            'Cannot create new policy version, Reason: ' +
                            policy_update_response.json()['detail'])
                        root_logger.debug(
                            'Detailed Json response is: ' +
                            policy_update_response.json())
                else:
                    root_logger.info('Unable to create the policy.')
            except FileNotFoundError:
                root_logger.info(
                    '\n' +
                    os.path.join(
                        new_policy_folder,
                        new_policy_file) +
                    ' is not found. This file is the default source for uploading rules.\n')
                root_logger.info(
                    'You may want to use "download <policyname>" first\n')
        else:
            root_logger.info(
                '\nLocal datastore does not have this policy. Please double check policy name or run "setup" first')

    return 0


def activate(args):
    base_url, session = init_config(args.edgerc, args.section)

    policy = args.policy
    version = args.version
    network = args.network

    if network == 'production':
        network = 'prod'

    cloudlet_object = Cloudlet(base_url)
    policies_folder = os.path.join(get_cache_dir(), 'policies')
    for root, dirs, files in os.walk(policies_folder):
        local_policy_file = policy + '.json'
        if local_policy_file in files:
            root_logger.info(
                policy +
                ' file is Found... Using policyId from local store...')
            with open(os.path.join(policies_folder, local_policy_file), mode='r') as policy_file_handler:
                policy_string_content = policy_file_handler.read()
            policy_json_content = json.loads(policy_string_content)
            policy_policy_id = policy_json_content['policyId']

            # Update the local copy to latest details
            root_logger.info(
                'Trying to activate policy ' +
                policy +
                ' version ' +
                version +
                ' to ' +
                network +
                ' network')

            activation_response = cloudlet_object.activate_policy_version(
                session, policy_policy_id, version, network)
            if activation_response.status_code == 200:
                root_logger.info('Success! Policy version is activated')
            else:
                root_logger.info(
                    'Unable to activate, check the version number.')
                return 1
        else:
            root_logger.info(
                '\nLocal datastore does not have this policy. Please double check policy name or run "setup" first')
            return 1

    return 0


def throttle(args):
    base_url, session = init_config(args.edgerc, args.section)

    policy = args.policy
    network = args.network
    rule = args.rule
    percent = args.percent
    disable = args.disable
    force = args.force

    if not disable and not percent:
        root_logger.info("One of --percent or --disable must be specified")
        return 1

    if disable and percent:
        root_logger.info("One of --percent or --disable must be specified, not both")
        return 1

    if not network:
        root_logger.info("--network must be specified")
        return 1

    if not rule:
        root_logger.info("--rule must be specified")
        return 1

    if percent:
        if int(percent) < -1 or int(percent) > 100:
            root_logger.info("Invalid --percent value, please specify a value between -1 and 100")
            return 1

    if not force and network == "production":
        if not disable:
            root_logger.info(
                'You are about to throttle ' +
                rule +
                ' at value = ' +
                str(percent) +
                ' for ' +
                policy +
                ' on the Akamai ' +
                network +
                ' network. Do you wish to continue? [y/N]')
        else:
            root_logger.info(
                'You are about to disable ' +
                rule +
                ' for ' +
                policy +
                ' on the Akamai ' +
                network +
                ' network. Do you wish to continue? [y/N]')

        if str.lower(input()) != 'y':
            root_logger.info('Exiting...')
            exit(1)

    if network == 'production':
        network = 'prod'

    cloudlet_object = Cloudlet(base_url)
    policies_folder = os.path.join(get_cache_dir(), 'policies')
    for root, dirs, files in os.walk(policies_folder):
        local_policy_file = policy + '.json'
        # Read the policy file to fetch policy ID
        if local_policy_file in files:
            with open(os.path.join(policies_folder, local_policy_file), mode='r') as policy_file_handler:
                policy_string_content = policy_file_handler.read()
            policy_json_content = json.loads(policy_string_content)
            policy_policy_id = policy_json_content['policyId']
            root_logger.info('Fetching policy details...')

            # Fetch policy details to identify the version
            policy_details = cloudlet_object.get_cloudlet_policy(
                session, policy_policy_id)
            staging_version = str(-1)
            prod_version = str(-1)
            for every_activation_detail in policy_details.json()['activations']:
                if every_activation_detail['policyInfo']['status'] == 'active':
                    if every_activation_detail['network'] == 'staging':
                        staging_version = str(
                            every_activation_detail['policyInfo']['version'])
                    elif every_activation_detail['network'] == 'prod':
                        prod_version = str(
                            every_activation_detail['policyInfo']['version'])

            # Check which network is of interest, and base the version number
            if network == 'staging' and staging_version != '-1':
                version = staging_version
            elif network == 'prod' and prod_version != '-1':
                version = prod_version
            else:
                root_logger.info(
                    'No current version live in ' +
                    network +
                    ' network. Exiting...')
                exit(1)

            root_logger.info(
                'Found version ' +
                version +
                ' live in ' +
                network +
                ' network. Using this version...')
            policy_details = cloudlet_object.get_cloudlet_policy(
                session, policy_policy_id, version=version)

            # Filter the details of policy
            rule_found = 0
            rule_count = 0
            policy_details_to_modify = {}
            every_detail_of_policy = policy_details.json()
            root_logger.info('\nSearching for Rule: ' + rule)
            if 'matchRules' in every_detail_of_policy:
                # Check whether it is null value
                if every_detail_of_policy['matchRules'] is None:
                    root_logger.info('No rules exist in the policy. Exiting...')
                    exit(1)
                if every_detail_of_policy['matchRules'] is not None:
                    match_rules_section = every_detail_of_policy['matchRules']
                    for every_match_rule in match_rules_section:
                        # Delete the location tag, as it causes error while
                        # uploading
                        if 'location' in every_match_rule:
                            del every_match_rule['location']
                        # Match the rule name (case insensitive)
                        if every_match_rule['name'].lower() == rule.lower():
                            # Update the throttle value now
                            rule_found = 1
                            rule_count = rule_count + 1
                            if not disable:
                                every_match_rule['passThroughPercent'] = int(percent)
                                # Check whether rules is disabled, if yes
                                # enable it by deleting the disable entry
                                if 'disabled' in every_match_rule and every_match_rule['disabled'] is True:
                                    del every_match_rule['disabled']
                            else:
                                every_match_rule['disabled'] = True

                    policy_details_to_modify['matchRules'] = every_detail_of_policy['matchRules']
                    policy_details_to_modify['description'] = 'Created from v' + str(version) + \
                                                              ': Throttle Rule = ' + rule + ' to value = ' \
                                                              + str(percent) if not disable else "disabled" + \
                                                              ' (Akamai CLI for Visitor Prioritization)'
                    if rule_found == 0:
                        root_logger.info(
                            'Rule: ' + rule + ' is not found. Exiting...')
                        return 1
                    if rule_count == 1:
                        root_logger.info('1 rule has been found...')
                    else:
                        root_logger.info(
                            str(rule_count) + ' rules have been found...')
            else:
                root_logger.info('No rules exist in the policy. Exiting...')
                return 1

            # Let us now create a new version and update the rules
            policy_create_response = cloudlet_object.create_policy_version(
                session, policy_id=policy_policy_id)
            root_logger.info(
                '\nTrying to create a new version of this policy with updated rule throttle.')
            if policy_create_response.status_code == 200 or 201:
                new_version = policy_create_response.json()['version']
                # Let us now update the rules with new throttle values
                policy_update_response = cloudlet_object.update_policy_version(
                    session, policy_policy_id, json.dumps(policy_details_to_modify), new_version)
                if policy_update_response.status_code == 200:
                    root_logger.info(
                        'Successfully created new policy version : v' + str(
                            policy_update_response.json()['version']))
                    # Let us now activate the version
                    root_logger.info(
                        'Now activating v' +
                        str(policy_update_response.json()['version']) +
                        ' to Akamai ' + network + ' network ')
                    activation_response = cloudlet_object.activate_policy_version(
                        session, policy_policy_id, str(policy_update_response.json()['version']), network)
                    if activation_response.status_code == 200:
                        root_logger.info('Success! Throttle change is live...')
                    else:
                        root_logger.info(
                            'Unable to activate, check for invalid version')
                        return 1
                else:
                    root_logger.info(
                        'Cannot create new policy version, Reason: ' +
                        str(policy_update_response.json()['detail']))
                    root_logger.debug(
                        'Detailed Json response is: ' +
                        str(policy_update_response.json()))
                    return 1
            else:
                root_logger.info('Unable to create the new version of policy.')
                return 1
        else:
            root_logger.info(
                '\nLocal datastore does not have this policy. Please double check policy name or run "setup" first')
            return 1

    return 0


def list(args=None):
    counter = 1
    policies_folder = os.path.join(get_cache_dir(), 'policies')

    root_logger.info('\n\nAvailable policies are: ')
    root_logger.info('--------------------------\n')
    for root, dirs, files in os.walk(policies_folder):
        for every_file in files:
            if every_file.endswith('json'):
                file_name = every_file.split('.')
                root_logger.info(str(counter) + '. ' + file_name[0])
                counter += 1
    root_logger.info('\n--------------------------\n')

    return 0


def confirm_setup(args):
    policies_dir = os.path.join(get_cache_dir(), 'policies')

    if not os.access(policies_dir, os.W_OK):
        print(
            "Cache not found. You must create it to continue [Y/n]:",
            end=' ')

        if str.lower(input()) == 'n':
            root_logger.info('Exiting.')
            exit(1)

        return setup(args)

    return


def get_prog_name():
    prog = os.path.basename(sys.argv[0])
    if os.getenv("AKAMAI_CLI"):
        prog = "akamai visitor-prioritization"
    return prog


def get_cache_dir():
    if os.getenv("AKAMAI_CLI_CACHE_DIR"):
        return os.getenv("AKAMAI_CLI_CACHE_DIR")

    return os.curdir


if __name__ == '__main__':
    try:
        status = cli()
        exit(status)
    except KeyboardInterrupt:
        exit(1)
