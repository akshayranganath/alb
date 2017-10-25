# Demonstrating the CLI for Application Load Balancer

## Cloudlet Policiy details

### Setup the policies
    python3 akamai-alb setup
    
### See a specific cloudlet policy
    python3 akamai-alb show --policy akrangan_alb2

### See details of the policy-version
    python3 akamai-alb show --policy akrangan_alb2 --version 2 --verbose

### Download a policy
    python3 akamai-alb download --policy akrangan_alb2 --version 2
    
## Create a new policy version
    python3 akamai-alb create-version --policy akrangan_alb2 --file akrangan_alb2_rules.json

## Activate the new version
    python3 akamai-alb activate --policy akrangan_alb2 --version 3 --network STAGING
            
## Origin Policy Details
    
### See a specific origin policy
    python3 akamai-alb show --origin_policy --policy akrangan_alb

### See details of an origin-policy version
    python3 akamai-alb show --origin_policy --policy akrangan_alb --version 4

### See full details of the origin policy
    python3 akamai-alb show --origin_policy --policy akrangan_alb --version 4 --verbose

## Download an origin policy
    python3 akamai-alb download --origin_policy --policy akrangan_alb --version 4

## Create a new origin policy version
    python3 akamai-alb create-version --policy akrangan_alb --origin_policy --file akrangan_alb_rules.json

## Activate new version
    python3 akamai-alb activate --policy akrangan_alb --origin_policy --version 5 --network STAGING    


            
        