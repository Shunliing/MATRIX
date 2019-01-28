import os
import json
import certifi
from datetime import datetime
from elasticsearch import Elasticsearch


class E2E:
    def __init__(self, protocol_config, protocol_config_path):
        self.protocol_config = protocol_config
        self.protocol_config_path = protocol_config_path
        self.es = Elasticsearch('https://search-escryptobiu-fyopgg3zepk6dtda4zerc53apy.us-east-1.es.amazonaws.com/',
                                use_ssl=True, ca_certs=certifi.where())

    def pre_process(self):
        working_directory = self.protocol_config['workingDirectory']
        pre_process_task = self.protocol_config['preProcessTask']
        os.system('fab -f Execution/fabfile.py pre_process:%s,%s --parallel'
                  % (working_directory, pre_process_task))

    def install_experiment(self):
        protocol_name = self.protocol_config['protocol']
        working_directory = self.protocol_config['workingDirectory']
        external_protocol = json.loads(self.protocol_config['isExternal'])
        git_address = self.protocol_config['CloudProviders']['aws']['git']['gitAddress']
        git_branch = self.protocol_config['CloudProviders']['aws']['git']['gitBranch']

        for idx in range(len(working_directory)):
            doc = {}
            doc['protocolName'] = protocol_name
            doc['message'] = 'Installing %s at %s' % (protocol_name, working_directory)
            doc['timestamp'] = datetime.utcnow()
            self.es.index(index='execution_matrix_ui', doc_type='execution_matrix_ui', body=doc)
            os.system('fab -f Execution/fabfile.py install_git_project:%s,%s,%s,%s --parallel'
                      % (git_branch[idx], working_directory[idx], git_address[idx], external_protocol))

    def execute_experiment(self):
        protocol_name = self.protocol_config['protocol']
        number_of_repetitions = self.protocol_config['numOfRepetitions']
        configurations = self.protocol_config['configurations']
        working_directory = self.protocol_config['workingDirectory']
        executables = self.protocol_config['executableName']
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    doc = {}
                    doc['protocolName'] = protocol_name
                    doc['message'] = 'Executing %s with configuration: %s' % (executables[idx], configurations[idx2])
                    doc['timestamp'] = datetime.utcnow()
                    self.es.index(index='execution_matrix_ui', doc_type='execution_matrix_ui', body=doc)
                    os.system('fab -f Execution/fabfile.py run_protocol:%s,%s,%s,%s --parallel'
                              % (self.protocol_config_path, configurations[idx2],
                                 executables[idx], working_directory[idx]))

    def execute_experiment_callgrind(self):
        number_of_repetitions = self.protocol_config['numOfRepetitions']
        configurations = self.protocol_config['configurations']
        working_directory = self.protocol_config['workingDirectory']
        executables = self.protocol_config['executableName']
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    os.system('fab -f Execution/fabfile.py run_protocol_profiler:%s,%s,%s,%s --parallel'
                              % (self.protocol_config_path, configurations[idx2],
                                 executables[idx], working_directory[idx]))

    @staticmethod
    def update_libscapi():
        branch = input('Enter libscapi branch to update from:')
        os.system('fab -f Execution/fabfile.py update_libscapi:%s --parallel' % branch)

