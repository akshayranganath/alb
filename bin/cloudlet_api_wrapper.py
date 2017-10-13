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
    def __init__(self, access_hostname):
        self.access_hostname = access_hostname

    def list_cloudlet_groups(self, session):
        """
        Function to fetch all groups

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        cloudlet_group_response : cloudlet_group_response
            (cloudlet_group_response) Object with all details
        """
        cloudlet_group_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/group-info'
        cloudlet_group_response = session.get(cloudlet_group_url)
        return cloudlet_group_response


    def get_all_group_ids(self, session):
        """
        Function to fetch all groupIDs only

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        group_id_list : List
            group_id_list with list of all groupIds
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
        Function to fetch all cloudlets

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        cloudlet_list : List
            cloudlet_list with list of all cloudlets
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
        Function to fetch Policies from cloudletId and GroupId

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        policies_response : policies_response
            Policies of cloudlet Id
        """
        policies_response = None
        if cloudlet_code == 'optional':
            policies_url = 'https://' + self.access_hostname + \
                           '/cloudlets/api/v2/policies?gid=' + str(group_id) + '&cloudletId=' + str(cloudlet_id)
            policies_response = session.get(policies_url)
        elif cloudlet_code == 'VP':
            policies_url = 'https://' + self.access_hostname + \
                           '/cloudlets/api/v2/policies?gid=' + str(group_id) + '&cloudletId=' + str(1)
            policies_response = session.get(policies_url)
        return policies_response

    def get_cloudlet_policy(self, session, policy_id, version='optional'):
        """
        Function to fetch a cloudlet policy detail

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        cloudlet_policy_response : cloudlet_policy_response
            Json object details of specific cloudlet policy
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
        Function to fetch a cloudlet policy versions

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        cloudletPolicyResponse : cloudletPolicyResponse
            Json object details of specific cloudlet policy versions
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
        Function to create a policy version

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        cloudlet_policy_create_response : cloudlet_policy_create_response
            Json object details of created cloudlet policy version
        """
        headers = {
            "Content-Type": "application/json"
        }
        if clone_version == 'optional':
            cloudlet_policy_create_url = 'https://' + self.access_hostname + \
                '/cloudlets/api/v2/policies/' + str(policy_id) + '/versions' + '?includeRules=true'
        else:
            cloudlet_policy_create_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/policies/' + \
                str(policy_id) + '/versions' + '?includeRules=true&cloneVersion=' + clone_version
        cloudlet_policy_create_response = session.post(
            cloudlet_policy_create_url, headers=headers)
        return cloudlet_policy_create_response

    def update_policy_version(
            self,
            session,
            policy_id,
            policy_details,
            version):
        """
        Function to update a policy version

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        cloudlet_policy_update_response : cloudlet_policy_update_response
            Json object details of updated cloudlet policy version
        """
        headers = {
            "Content-Type": "application/json"
        }
        cloudlet_policy_update_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/policies/' + \
                                     str(policy_id) + '/versions/' + str(version) + '?omitRules=false'
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
        Function to activate a policy version

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        cloudlet_policy_activate_response : cloudlet_policy_activate_response
            Json object details of activated cloudlet policy version
        """
        headers = {
            "Content-Type": "application/json"
        }
        network_data = """{
            "network" : "%s"
        }""" % network
        cloudlet_policy_activate_url = 'https://' + self.access_hostname + \
            '/cloudlets/api/v2/policies/' + str(policy_id) + '/versions/' + str(version) + '/activations'
        cloudlet_policy_activate_response = session.post(
            cloudlet_policy_activate_url, data=network_data, headers=headers)
        return cloudlet_policy_activate_response

    def delete_policy_version(self, session, policy_id, version):
        """
        Function to delete a policy version

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        cloudlet_policy_delete_response : cloudlet_policy_delete_response
            Json object details of deleted cloudlet policy version
        """

        cloudlet_policy_delete_url = 'https://' + self.access_hostname + \
                                     '/cloudlets/api/v2/policies/' + str(policy_id) + '/versions/' + str(version)
        cloudlet_policy_delete_response = session.delete(
            cloudlet_policy_delete_url)
        return cloudlet_policy_delete_response

    def get_all_origin_ids(self, session):
        """
        Function to fetch all the ALB cloudlets

        :param session: <string>
            An EdgeGrid Auth akamai session object

        :return: cloudlet_origin_response : Object
            (cloudlet_origin_response) Object with all details

        """
        cloudlet_origin_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/origins??type=APPLICATION_LOAD_BALANCER'
        cloudlet_origin_response = session.get(cloudlet_origin_url)
        return cloudlet_origin_response

    def get_cloudlet_origin_versions(self, session, origin_id):
       """

       :param session: Object
            An EdgeGrid Auth akamai session object
       :param origin_id: String
            The origin id for the Cloudlet policies

       :return: cloudlet_origin_response : Object
            (cloudlet_origin_response) Object with all details
       """
       cloudlet_policy_url = 'https://' + self.access_hostname + '/cloudlets/api/v2/origins/' + \
                                  str(origin_id) + '/versions/'
        cloudlet_policy_response = session.get(cloudlet_policy_url)
        return cloudlet_policy_response