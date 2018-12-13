# Application Load Balancer (ALB) Management
Provides a way to interact real-time with your Application Load Balancer (ALB) Cloudlet via Open APIs and without manually having to go into the Luna Portal. 

The CLI provides various functionality such as 

- viewing current policies, 
- downloading policies
- updating the policiy and 
- activating changes

When it comes to Application Load Balancer, there are 2 kinds of settings:

- ALB Cloudlet policies itself
- Origin policies associated with the ALB

The CLI provides an ability to work with either of the configurations. 

## Local Install
* Python 3+
* pip install edgegrid-python

### Credentials
In order to use this module, you need to:
* Set up your credential files as described in the [authorization](https://developer.akamai.com/introduction/Prov_Creds.html) and [credentials](https://developer.akamai.com/introduction/Conf_Client.html) sections of the Get Started pagegetting started guide on the [developer portal](https://developer.akamai.com/).  
* When working through this process you need to give grants for the Cloudlets Policy Manager API.  The section in your configuration file should be called 'cloudlets'.
```
[cloudlets]
client_secret = [CLIENT_SECRET]
host = [HOST]
access_token = [ACCESS_TOKEN_HERE]
client_token = [CLIENT_TOKEN_HERE]
```

## Functionality (version 1.0.0)
The initial version of the CLI provides the following functionality:
* One-time setup/download of local policy ids necessary to invoke APIs quickly
* List current policy details, previous versions, and rules
* Download the specified policy rules file in .json format to edit if necessary
* Create a new policy version based on a raw json file
* Activate a specific policy version

Except for the one-time setup, each of the other functionalities can be invoked either for the ALB cloudlet or for the ALB origin configuration.
 
## cli-alb
Main program that wraps this functionality in a command line utility:
* [setup](#setup)
* [list](#list)
* [show](#show)
* [activate](#activate)
* [download](#download)
* [create-version](#create-version)

### setup
Does a one time download of Application Load Balancer (ALB) Cloudlet policyIds, origin policies ids and groupIds and stores them in /setup folder for faster local retrieval. This command can be run anytime and will refresh the /setup folder based on the current list of policies. 

```bash
%  akamai-alb setup
```

### list
List current ALB Cloudlet policy  or ALB Cloudlet Origin policy names  

```bash
%  akamai-alb list
```

Use the optional parameter ```--origin_policy``` to see the ALB origin configuration details.

### show
Get specific details for a policy name. Available information include configurations that reference that policy, current version numbers on Akamai staging and production, version history, and current rule settings.

```bash
%  akamai-alb show --policy samplePolicyName
%  akamai-alb show --policy samplePolicyName --from-version 37
%  akamai-alb show --policy samplePolicyName --version 66
%  akamai-alb show --policy samplePolicyName --version 66 --verbose
```

The flags of interest for show are:

```
--policy <policyName>        Specified ALB Cloudlet / ALB Oriign policy name
--version <version>          Specific version number for that policy name (optional)
--from-version <fromVersion> If --version is not specified, list policy version details starting from --from-version value (optional)
--verbose                    If --version is specified, add --verbose to get full rule details including url paths and match criteria (optional)
```

Use the optional parameter ```--origin_policy``` to see the ALB origin configuration details.

### activate
Activate a specified version for a policy to the appropriate network (staging or production)

```bash
%  akamai-alb activate --policy samplePolicyName --version 87 --network staging
%  akamai-alb activate --policy samplePolicyName --version 71 --network production
```

The flags of interest for activate are:

```
--policy <policyName>   Specified ALB Cloudlet / ALB Oriign policy name
--version <version>     Specific version number for that policy name
--network <network>     Either staging or production

```

Use the optional parameter ```--origin_policy``` to see the ALB origin configuration details.


### download
Download the raw policy rules for a specified version in json format for local editing if desired.

```bash
%  akamai-alb download --policy samplePolicyName --version 87
%  akamai-alb download --policy samplePolicyName --version 71 --output-file savefilename.json
```

The flags of interest for download are:

```
--policy <policyName>     Specified ALB Cloudlet / ALB Oriign policy name
--version <version>       Specific version number for that policy name
--output-file <filename>  Filename to be saved in /rules folder (optional) 

```

Use the optional parameter ```--origin_policy``` to see the ALB origin configuration details.


### create-version
Create a new policy version from a raw json file

```bash
%  akamai-alb create-version --policy samplePolicyName
%  akamai-alb create-version --policy samplePolicyName --file filename.json
%  akamai-alb create-version --policy samplePolicyName --file filename.json --force
```

The flags of interest for create-version are:

```
--policy <policyName>  Specified ALB Cloudlet / ALB Oriign policy name
--file <file>	         Filename of raw .json file to be used as policy details. This file should be in the /rules folder (optional)
--force                Use this flag if you want to proceed without confirmation if description field in json has not been updated
```

Use the optional parameter ```--origin_policy``` to see the ALB origin configuration details.
