# Application Load Balancer (ALB) Management
Provides a way to interact real-time with your Visitor Prioritization Cloudlet via Open APIs and without manually having to go into the Luna Portal. Provides various functionality such as viewing current policies, current status, rule details, and the ability to invoke actual percentage changes.

<strong><span style="color:red">This code is currently work in progress. This section will show the completed parts of the code:<br />Code is now able to pull down all the ALB policies.</span></strong>

## Local Install
* Python 3+
* pip install edgegrid-python

### Credentials
In order to use this module, you need to:
* Set up your credential files as described in the [authorization](https://developer.akamai.com/introduction/Prov_Creds.html) and [credentials](https://developer.akamai.com/introduction/Conf_Client.html) sections of the Get Started pagegetting started guide on developer.akamai.comthe developer portal.  
* When working through this process you need to give grants for the Cloudlets Policy Manager API.  The section in your configuration file should be called 'cloudlets'.
```
[cloudlets]
client_secret = [CLIENT_SECRET]
host = [HOST]
access_token = [ACCESS_TOKEN_HERE]
client_token = [CLIENT_TOKEN_HERE]
```

## Functionality (version 1.0.0)
The initial version of the cloudlet-visitor-prioritization provides the following functionality:
* One-time setup/download of local policy ids necessary to invoke APIs quickly
* List current policy details, previous versions, and rules
* Throttle (make percentage updates) rule for the specified policy and invoke change immediately
* Download the specified policy rules file in .json format to edit if necessary
* Create a new policy version based on a raw json file
* Activate a specific policy version

## cli-cloudlet-visitor-prioritization
Main program that wraps this functionality in a command line utility:
* [setup](#setup)
* [list](#list)
* [show](#show)
* [throttle](#throttle)
* [activate](#activate)
* [download](#download)
* [create-version](#create-version)

### setup
Does a one time download of Visitor Prioritization Cloudlet policyIds and groupIds and stores them in /setup folder for faster local retrieval. This command can be run anytime and will refresh the /setup folder based on the current list of policies. 

```bash
%  akamai-visitor-prioritization setup
```

### list
List current Visitor Prioritization Cloudlet policy names  

```bash
%  akamai-visitor-prioritization list
```

### show
Get specific details for a policy name. Available information include configurations that reference that policy, current version numbers on Akamai staging and production, version history, and current rule settings.

```bash
%  akamai-visitor-prioritization show --policy samplePolicyName
%  akamai-visitor-prioritization show --policy samplePolicyName --from-version 37
%  akamai-visitor-prioritization show --policy samplePolicyName --version 66
%  akamai-visitor-prioritization show --policy samplePolicyName --version 66 --verbose
```

The flags of interest for show are:

```
--policy <policyName>        Specified Visitor Prioritization Cloudlet policy name
--version <version>          Specific version number for that policy name (optional)
--from-version <fromVersion> If --version is not specified, list policy version details starting from --from-version value (optional)
--verbose                    If --version is specified, add --verbose to get full rule details including url paths and match criteria (optional)

```

### throttle
Make an actual change to percentage value for a specific rule name in the policy.

```bash
%  akamai-visitor-prioritization throttle --percent 50 --policyName samplePolicyName --rule 'ruleName' --network staging
%  akamai-visitor-prioritization throttle --percent -1 --policyName samplePolicyName --rule 'ruleName' --network staging
%  akamai-visitor-prioritization throttle --disable --policy samplePolicyName --rule 'ruleName' --network production
%  akamai-visitor-prioritization throttle --disable --policy samplePolicyName --rule 'ruleName' --network production --force
%  akamai-visitor-prioritization throttle --disable --policy samplePolicyName --rule 'ruleName' --network staging
```

The flags of interest for throttle are:

```
--percent <value>       Acceptable values are -1 (= All to Waiting Room), 0 <= 100 (100 = everyone allowed)
--disable               If specifed instead of --percent, disables the rule in the policy
--policy <policyName>   Specified Visitor Prioritization Cloudlet policy name
--rule <ruleName>       Name of rule in policy that should be changed. Use single quotes ('') in case rule name has spaces. If multiple rules exist for the same name, all of them will be updated.
--network <network>     Either staging or production ; will make change based on latest version on that network
--force                 Use this flag if you want to proceed without confirmation (only for --network production)
```

### activate
Activate a specified version for a policy to the appropriate network (staging or production)

```bash
%  akamai-visitor-prioritization activate --policy samplePolicyName --version 87 --network staging
%  akamai-visitor-prioritization activate --policy samplePolicyName --version 71 --network production
```

The flags of interest for activate are:

```
--policy <policyName>   Specified Visitor Prioritization Cloudlet policy name
--version <version>     Specific version number for that policy name
--network <network>     Either staging or production

```

### download
Download the raw policy rules for a specified version in json format for local editing if desired.

```bash
%  akamai-visitor-prioritization download --policy samplePolicyName --version 87
%  akamai-visitor-prioritization download --policy samplePolicyName --version 71 --output-file savefilename.json
```

The flags of interest for download are:

```
--policy <policyName>     Specified Visitor Prioritization Cloudlet policy name
--version <version>       Specific version number for that policy name
--output-file <filename>  Filename to be saved in /rules folder (optional) 

```

### create-version
Create a new policy version from a raw json file

```bash
%  akamai-visitor-prioritization create-version --policy samplePolicyName
%  akamai-visitor-prioritization create-version --policy samplePolicyName --file filename.json
%  akamai-visitor-prioritization create-version --policy samplePolicyName --file filename.json --force
```

The flags of interest for create-version are:

```
--policy <policyName>  Specified Visitor Prioritization Cloudlet policy name
--file <file>	         Filename of raw .json file to be used as policy details. This file should be in the /rules folder (optional)
--force                Use this flag if you want to proceed without confirmation if description field in json has not been updated
```
