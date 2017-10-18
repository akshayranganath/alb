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

import json


class Cloudlet(object):
    """
        Place holder for all the cloudlet related API calls. The whole class is a wrapper to the API and no
        real decision logic is executed in this file.
    """

    def __init__(self, access_hostname):
        """

        :param access_hostname: <string>
            This is the host filed from the edgerc file
        """
        self.access_hostname = access_hostname

    def list_cloudlet_groups(self, session):
        """
        Function to fetch all groups
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :return: cloudlet_group_response: <Requests.response>
                HTTP response for the API call.
        """
        cloudlet_group_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/group-info'
        cloudlet_group_response = session.get(cloudlet_group_url)
        return cloudlet_group_response

    def get_all_group_ids(self, session):
        """
        Get All group
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :return: group_id_list: <List>
                List of group IDs. This will typically be used for finding all the cloudlet policies.
        """
        cloudlet_group_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/group-info'
        cloudlet_group_response = session.get(cloudlet_group_url)
        group_id_list = []
        if cloudlet_group_response.status_code == 200:
            for everyItem in cloudlet_group_response.json():
                group_id_list.append(everyItem['groupId'])
        return group_id_list

    def list_all_cloudlets(self, session):
        """
        List all cloudlets
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :return: cloudlet_list : <List>
                This function loops through all the available cloudlets in a group and returns the ALB cloudlets,
                if present.
        """
        group_id_list = self.get_all_group_ids(session)
        cloudlet_list = []
        for every_group_id in group_id_list:
            list_all_cloudlets_url = 'https://' + self.access_hostname + \
                                     '/cloudlets/api/v2/cloudlet-info?gid=' + str(every_group_id)
            print('Fetching cloudlet for Group: ' + str(every_group_id))
            list_all_cloudlets_response = session.get(list_all_cloudlets_url)
            if list_all_cloudlets_response.status_code == 200:
                cloudlet_list.append(list_all_cloudlets_response.json())
                print(json.dumps(list_all_cloudlets_response.json()))
                print(
                    'Added cloudlet info for Group: ' +
                    str(every_group_id) +
                    ' to a list\n')
            else:
                print(
                    'Group: ' +
                    str(every_group_id) +
                    ' did not yield any cloudlets\n')
        return cloudlet_list

    def list_policies(
            self,
            session,
            group_id,
            cloudlet_id='optional',
            cloudlet_code='optional'):
        """
        List all the available policies for a cloudlet type.

            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param group_id: <int>
                groupId field
            :param cloudlet_id: <int>
                This is hard coded to be 9. This indicates the ALB cloudlet.
            :param cloudlet_code: <String> Default - optional
                For ALB, this is set to "ALB" in the calling function

            :return: policies_response : <Requests.response>
                HTTP response for the API call.

        """
        policies_response = None
        if cloudlet_code == 'optional':
            policies_url = 'https://' + self.access_hostname + \
                           '/cloudlets/api/v2/policies?gid=' + str(group_id) + '&cloudletId=' + str(cloudlet_id)
            policies_response = session.get(policies_url)
        elif cloudlet_code == 'ALB':
            # ALB has a cloudletId value of 9
            policies_url = 'https://' + self.access_hostname + \
                           '/cloudlets/api/v2/policies?gid=' + str(group_id) + '&cloudletId=' + str(9)
            policies_response = session.get(policies_url)
        return policies_response

    def get_cloudlet_policy(self, session, policy_id, version='optional'):
        """
        Get the details for a cloudlet policy
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param policy_id: <int>
                This will contain the policyId field for a cloudlet or the originId
            :param version: <int>
                The version for which we need the details.

            :return: cloudlet_policy_response: <Requests.response>
                HTTP response for the API call.
        """
        if version == 'optional':
            cloudlet_policy_url = 'https://' + self.access_hostname + \
                                  '/cloudlets/api/v2/policies/' + str(policy_id)
        else:
            cloudlet_policy_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/policies/' + \
                                  str(policy_id) + '/versions/' + str(version) + '?omitRules=false'
        cloudlet_policy_response = session.get(cloudlet_policy_url)
        return cloudlet_policy_response

    def list_policy_versions(self, session, policy_id, page_size='optional'):
        """
        List the policy versions for a cloudlet.

            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param policy_id: <int>
                This will contain the policyId field for a cloudlet or the originId
            :param page_size: <String>
                An optional parameter that specific the number of responses returned.
                By default, we return everything.

            :return:  cloudlet_policy_versions_response : <Requests.response>
                HTTP response for the API call.
        """
        if page_size == 'optional':
            cloudlet_policy_versions_url = 'https://' + self.access_hostname + \
                                           '/cloudlets/api/v2/policies/' + str(
                policy_id) + '/versions?includeRules=true'
        else:
            cloudlet_policy_versions_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/policies/' + \
                                           str(policy_id) + '/versions?includeRules=true&pageSize=' + page_size
        cloudlet_policy_versions_response = session.get(
            cloudlet_policy_versions_url)
        return cloudlet_policy_versions_response

    def create_policy_version(
            self,
            session,
            policy_id,
            clone_version='optional'):
        """
        Create a new version of the cloudlet or origin policy
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param policy_id: <int>
                This will contain the policyId field for the cloudlet
            :param clone_version: <int>
                The version to clone from. This is applicable for cloudlet policy as origin policy does not support
                cloning functionality.

            :return: cloudlet_policy_create_response : : <Requests.response>
                HTTP response for the API call.
        """
        headers = {
            "Content-Type": "application/json"
        }
        if clone_version == 'optional':
            cloudlet_policy_create_url = 'https://' + self.access_hostname + \
                                         '/cloudlets/api/v2/policies/' + str(
                policy_id) + '/versions' + '?includeRules=true'
        else:
            cloudlet_policy_create_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/policies/' + \
                                         str(
                                             policy_id) + '/versions' + '?includeRules=true&cloneVersion=' + clone_version
        cloudlet_policy_create_response = session.post(
            cloudlet_policy_create_url, headers=headers)
        return cloudlet_policy_create_response

    def create_origin_policy_version(
            self,
            session,
            policy_id,
            policy_details,
            clone_version='optional'):
        """
        Create a new origin policy
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param policy_id: <int>
                This will contain the originId field for the ALB policy
            :param clone_version: <int>
                The version to clone from. This is applicable for cloudlet policy as origin policy does not support
                cloning functionality.

            :return: cloudlet_policy_create_response : : <Requests.response>
                HTTP response for the API call.
        """
        headers = {
            "Content-Type": "application/json"
        }
        if clone_version == 'optional':
            cloudlet_policy_create_url = 'https://' + self.access_hostname + \
                                         '/cloudlets/api/v2/origins/' + policy_id + '/versions'
        else:
            cloudlet_policy_create_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/policies/' + \
                                         policy_id + '/versions' + '?cloneVersion=' + clone_version
        print ('Using URL: ' + cloudlet_policy_create_url )
        cloudlet_policy_create_response = session.post(
            cloudlet_policy_create_url, headers=headers, data=policy_details)
        return cloudlet_policy_create_response

    def update_policy_version(
            self,
            session,
            policy_id,
            policy_details,
            version):
        """
        Update a specific version of the cloudlet policy
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param policy_id: <int>
                This will contain the policyId field for the cloudlet
            :param policy_details: <JSON>
                This is the raw JSON to be used for the policy
            :param version: <int>
                The version for which we need the details.

            :return: cloudlet_policy_update_response: <Requests.response>
                HTTP response for the API call.
        """
        headers = {
            "Content-Type": "application/json"
        }
        cloudlet_policy_update_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/policies/' + \
                                     str(policy_id) + '/versions/' + str(version) + '?omitRules=false'
        cloudlet_policy_update_response = session.put(
            cloudlet_policy_update_url, data=policy_details, headers=headers)
        return cloudlet_policy_update_response

    def update_origin_policy_version(
            self,
            session,
            policy_id,
            policy_details,
            version):
        """
        Update a specific version of the cloudlet origin policy
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param policy_id: <int>
                This will contain the originId field for the cloudlet origin
            :param policy_details: <JSON>
                This is the raw JSON to be used for the policy
            :param version: <int>
                The version for which we need the details.

            :return: cloudlet_policy_update_response: <Requests.response>
                HTTP response for the API call.
        """
        headers = {
            "Content-Type": "application/json"
        }
        cloudlet_policy_update_url = 'https://' + self.access_hostname + \
                                         '/cloudlets/api/v2/origins/' + policy_id + '/versions' + str(version) + '?omitRules=false'
        cloudlet_policy_update_response = session.put(
            cloudlet_policy_update_url, data=policy_details, headers=headers)
        return cloudlet_policy_update_response

    def activate_policy_version(
            self,
            session,
            policy_id,
            version,
            network='staging'):
        """
        Activate a specific cloudlet policy version to the Akamai staging or production network
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param policy_id: <int>
                This will contain the cloudletId field for the cloudlet policy
            :param version: <int>
                The version for which we need the details.
            :param network: <String> (staging | production)
                The nework on which this ocnfiguration needs to be activated.

            :return: cloudlet_policy_activate_response: <Requests.response>
                HTTP response for the API call.

        """
        headers = {
            "Content-Type": "application/json"
        }
        network_data = """{
            "network" : "%s"
        }""" % network
        cloudlet_policy_activate_url = 'https://' + self.access_hostname + \
                                       '/cloudlets/api/v2/policies/' + str(policy_id) + '/versions/' + str(
            version) + '/activations'
        cloudlet_policy_activate_response = session.post(
            cloudlet_policy_activate_url, data=network_data, headers=headers)
        return cloudlet_policy_activate_response

    def activate_origin_policy_version(
            self,
            session,
            origin_policy_id,
            version,
            network='staging'):
        """
        Activate a specific origin policy version to the Akamai netowork.
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param origin_policy_id: <int>
                This will contain the originId field for the cloudlet origin
            :param version: <int>
                The version for which we need the details.
            :param network: <String> (staging | production)
                The nework on which this ocnfiguration needs to be activated.

            :return: cloudlet_policy_activate_response: <Requests.response>
                HTTP response for the API call.
        """
        headers = {
            "Content-Type": "application/json"
        }
        network_data = {"dryrun": False,"network": network.upper(),"originId" : origin_policy_id,"version": int(version)}
        # now convert it to a string format
        network_data = json.dumps(network_data, indent=4)
        cloudlet_policy_activate_url = 'https://' + self.access_hostname + \
                                       '/cloudlets/api/v2/origins/' + origin_policy_id + '/activations'
        cloudlet_policy_activate_response = session.post(
            cloudlet_policy_activate_url, data=network_data, headers=headers)
        return cloudlet_policy_activate_response

    def delete_policy_version(
            self,
            session,
            policy_id,
            version
    ):
        """
        Delete a policy version
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param policy_id: <int>
                This will contain the cloudletId field for the cloudlet policy
            :param version: <int>
                The version for which we need the details.

            :return: cloudlet_policy_delete_response : <Requests.response>
                HTTP response for the API call.
        """

        cloudlet_policy_delete_url = 'https://' + self.access_hostname + \
                                     '/cloudlets/api/v2/policies/' + str(policy_id) + '/versions/' + str(version)
        cloudlet_policy_delete_response = session.delete(
            cloudlet_policy_delete_url)
        return cloudlet_policy_delete_response

    def list_origins(self, session):
        """
        List all the origins
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object

            :return: cloudlet_origin_response : <Requests.response>
                HTTP response for the API call.
        """
        cloudlet_origin_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/origins?type=APPLICATION_LOAD_BALANCER'
        cloudlet_origin_response = session.get(cloudlet_origin_url)
        return cloudlet_origin_response

    def get_cloudlet_origin_version(
            self,
            session,
            origin_id,
            version
    ):
        """
        Get a cloudlet origin version.
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param origin_id: <int>
                The originId for the clouldlet origin policy
            :param version: <int>
                The version for which we need the details.

            :return: cloudlet_policy_response : <Requests.response>
                HTTP response for the API call.
        """
        cloudlet_policy_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/origins/' + \
                              str(origin_id) + '/versions/' + version
        cloudlet_policy_response = session.get(cloudlet_policy_url)
        return cloudlet_policy_response

    def list_origin_policy_activiations(
            self,
            session,
            origin_id
    ):
        """
        List all the origin policy activations
            :param session: <Requests.session>
                An EdgeGrid Auth akamai session object
            :param origin_id: <int>
                The originId for the clouldlet origin policy

            :return: cloudlet_policy_response : <Requests.response>
                HTTP response for the API call.
        """
        cloudlet_policy_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/origins/' + \
                              str(origin_id) + '/activations/'
        cloudlet_policy_response = session.get(cloudlet_policy_url)
        return cloudlet_policy_response