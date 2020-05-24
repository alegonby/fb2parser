import glob


class TestProcessor:
    def __init__(self, config, connector, logger):
        self.config = config
        self.connector = connector
        self.logger = logger

    def process(self):
        test_data_files = self.check_test_folder()

        for f in test_data_files:
           self.do_testing(f)

    def check_test_folder(self):
        test_data_folder = self.config.get_test_data_folder()
        return [f for f in glob.glob(test_data_folder + '/*.json', recursive=True)]

    def do_testing(self, file_name):
        self.logger.start_test(file_name)

        with open(file_name, encoding = 'utf-8') as f:
            test_data = eval(f.read())
        var_dict = {}
        for test in test_data['tests']:
            self.logger.start_case(test['name'])

            if test['parametrized'] == 1:
                parameter = test['parameter']
                query = test['query'] + "'" + var_dict.get(parameter, "") + "'"
            else:
                query = test['query']

            expected_result = test['expected']
            actual_result = self.connector.execute(query)
            var_name = test['var_name']
            var_dict[var_name] = actual_result
            print(var_dict)

            if actual_result == expected_result:
                self.logger.add_pass(query, actual_result)
            else:
                self.logger.add_fail(query, actual_result, expected_result)