import json
import certifi
from datetime import datetime
from elasticsearch import Elasticsearch
from Execution.new_fabfile import FabricTasks


class E2E:
    def __init__(self, protocol_config, protocol_config_path):
        self.protocol_config = protocol_config
        self.protocol_config_path = protocol_config_path
        self.es = Elasticsearch('3.81.191.221:9200', ca_certs=certifi.where())
        self.protocol_name = self.protocol_config['protocol']

        self.fabric = FabricTasks()

    def pre_process(self):
        pre_process_task = self.protocol_config['preProcessTask']
        self.fabric.pre_process(pre_process_task)

    def install_experiment(self):
        # read git credentials configuration

        with open('GlobalConfigurations/tokens.json', 'r') as tokens_file:
            data = json.load(tokens_file)
            username = data['GitHub']['user']
            password = data['GitHub']['password']

        protocol_name = self.protocol_config['protocol']
        working_directory = self.protocol_config['workingDirectory']
        external_protocol = json.loads(self.protocol_config['isExternal'])
        cp = list(self.protocol_config['CloudProviders'].keys())
        git_address = self.protocol_config['CloudProviders'][cp[0]]['git']['gitAddress']
        git_branch = self.protocol_config['CloudProviders'][cp[0]]['git']['gitBranch']

        for idx in range(len(working_directory)):
            doc = {}
            doc['protocolName'] = protocol_name
            doc['message'] = 'Installing %s at %s' % (protocol_name, working_directory)
            doc['timestamp'] = datetime.utcnow()
            self.es.index(index='execution_matrix_ui', doc_type='execution_matrix_ui', body=doc)
            self.fabric.install_git_project(username, password, git_branch[idx], working_directory[idx],
                                            git_address[idx], external_protocol)

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
                    party_id = 0
                    for conn in self.fabric.connections:
                        self.fabric.test_task(conn, party_id)
                        self.fabric.run_protocol(conn, '/home/liork/MATRIX/HyperMPC.json', configurations[idx2],
                                                 executables[idx], working_directory[idx], party_id)
                        party_id += 1

    def execute_experiment_callgrind(self):
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
                    doc['message'] = 'Executing profiler for %s with configuration: %s' \
                                     % (executables[idx], configurations[idx2])
                    doc['timestamp'] = datetime.utcnow()
                    self.es.index(index='execution_matrix_ui', doc_type='execution_matrix_ui', body=doc)
                    self.fabric.run_protocol_profiler()

    def execute_experiment_with_latency(self):
        number_of_repetitions = self.protocol_config['numOfRepetitions']
        configurations = self.protocol_config['configurations']
        working_directory = self.protocol_config['workingDirectory']
        executables = self.protocol_config['executableName']
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    self.fabric.run_protocol_latency()

    def update_libscapi(self):
        protocol_name = self.protocol_config['protocol']

        doc = {}
        doc['protocolName'] = protocol_name
        doc['message'] = 'Update libscapi for %s protocol' % protocol_name
        doc['timestamp'] = datetime.utcnow()
        self.es.index(index='execution_matrix_ui', doc_type='execution_matrix_ui', body=doc)

        self.fabric.update_libscapi()

    def get_logs(self):
        protocol_name = self.protocol_config['protocol']

        doc = {}
        doc['protocolName'] = protocol_name
        doc['message'] = 'Get logs for protocol %s' % protocol_name
        doc['timestamp'] = datetime.utcnow()
        self.es.index(index='execution_matrix_ui', doc_type='execution_matrix_ui', body=doc)
        self.get_logs()

