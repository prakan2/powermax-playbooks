from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import dellemc_ansible_utils as utils
import logging
from PyU4V.utils import constants

__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'
                    }

DOCUMENTATION = r'''
'''

EXAMPLES = r'''
-name: Get details of the Storage Group
    dellemc_powermax_unmapvolume:
      unispherehost: "{{unispherehost}}"
      universion: "{{universion}}"
      verifycert: "{{verifycert}}"
      user: "{{user}}"
      password: "{{password}}"
      serial_no: "{{serial_no}}"
      register: result      
'''

SLOPROVISIONING = constants.SLOPROVISIONING

HAS_PYU4V = utils.has_pyu4v_sdk()

PYU4V_VERSION_CHECK = utils.pyu4v_version_check()

LOG = utils.get_logger('dellemc_powermax_unmapvolume', log_devel=logging.INFO)
# Application Type
APPLICATION_TYPE = 'ansible_v1.1'


class PowerMaxUnmapVolume(object):
    def __init__(self):
        """Define all the parameters required by this module"""

        self.module_params = utils.get_powermax_management_host_parameters()
        self.array_id = self.module_params['serial_no']
        serial_no = self.module_params['serial_no']

        # initialize the ansible module
        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=False,
        )

        # result is a dictionary that contains changed status and
        # volume details
        self.result = {"changed": False, "unmapvolumes": {}}
        if HAS_PYU4V is False:
            self.module.fail_json(msg="Ansible modules for PowerMax require "
                                      "the PyU4V python library to be "
                                      "installed. Please install the library "
                                      "before using these modules.")

        if PYU4V_VERSION_CHECK is not None:
            self.module.fail_json(msg=PYU4V_VERSION_CHECK)
            LOG.error(PYU4V_VERSION_CHECK)

        universion_details = utils.universion_check(
            self.module.params['universion'])
        LOG.info("universion_details: {0}".format(universion_details))

        if not universion_details['is_valid_universion']:
            self.module.fail_json(msg=universion_details['user_message'])

        self.u4v_conn = utils.get_U4V_connection(
            self.module.params, application_type=APPLICATION_TYPE)
        self.provisioning = self.u4v_conn.provisioning
        LOG.info('Got PyU4V instance for provisioning on to VMAX ')

    def get_unmap_volume_list(self, params=None):
        msg = 'ARRAY ID:' + str(self.array_id) + '---------------'
        try:
            response = self.provisioning.get_resource(self.u4v_conn.array_id, SLOPROVISIONING, 'volume',
                                                      params='?mapped=true&&num_of_masking_views=0')
            unmap_volume_list = response.get('resultList', []) if response else []
            return str(unmap_volume_list)

        except Exception as e:
            msg += 'Get Volumes for array {0} failed with error {1} '.format(
                self.u4v_conn.array_id, str(e))
            LOG.error(msg)
            self.module.fail_json(msg=msg)

    def perform_module_operation(self):
        changed = False
        unmap_vol = self.get_unmap_volume_list()
        # Finally update the module changed state
        self.result["changed"] = changed
        self.result["volume_details"] = unmap_vol
        self.module.exit_json(**self.result)


def main():
        obj = PowerMaxUnmapVolume()
        resp = obj.perform_module_operation()
        self.module.exit_json(changed=True, meta=resp)


if __name__ == '__main__':
    main()

