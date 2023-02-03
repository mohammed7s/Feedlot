# -*- coding: utf-8 -*- #
"""This provides the DuneAnalytics class implementation"""

from requests import Session
import logging
import pytest
import pandas as pd



#################################################################
#########     Duneanalytics class implementation   ##############
#################################################################


# --------- Constants --------- #

BASE_URL = "https://dune.com"
GRAPH_URL = 'https://core-hsr.dune.com/v1/graphql'

# --------- Constants --------- #
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s : %(levelname)s : %(funcName)-9s : %(message)s'
)
logger = logging.getLogger("dune")


class DuneAnalytics:
    """
    DuneAnalytics class to act as python client for duneanalytics.com.
    All requests to be made through this class.
    """

    def __init__(self, username, password):
        """
        Initialize the object
        :param username: username for duneanalytics.com
        :param password: password for duneanalytics.com
        """
        self.csrf = None
        self.auth_refresh = None
        self.token = None
        self.username = username
        self.password = password
        self.session = Session()
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                      'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'dnt': '1',
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'origin': BASE_URL,
            'upgrade-insecure-requests': '1'
        }
        self.session.headers.update(headers)

    def login(self):
        """
        Try to login to duneanalytics.com & get the token
        :return:
        """
        login_url = BASE_URL + '/auth/login'
        csrf_url = BASE_URL + '/api/auth/csrf'
        auth_url = BASE_URL + '/api/auth'

        # fetch login page
        self.session.get(login_url)

        # get csrf token
        self.session.post(csrf_url)
        self.csrf = self.session.cookies.get('csrf')

        # try to login
        form_data = {
            'action': 'login',
            'username': self.username,
            'password': self.password,
            'csrf': self.csrf,
            'next': BASE_URL
        }

        self.session.post(auth_url, data=form_data)
        self.auth_refresh = self.session.cookies.get('auth-refresh')
        if self.auth_refresh is None:
            logger.warning("Login Failed!")

    def fetch_auth_token(self):
        """
        Fetch authorization token for the user
        :return:
        """
        session_url = BASE_URL + '/api/auth/session'

        response = self.session.post(session_url)
        if response.status_code == 200:
            self.token = response.json().get('token')
            if self.token is None:
                logger.warning("Fetching Token Failed!")
        else:
            logger.error(response.text)

    def query_result_id(self, query_id):
        """
        Fetch the query result id for a query

        :param query_id: provide the query_id
        :return:
        """
        query_data = {"operationName": "GetResult", "variables": {"query_id": query_id},
                      "query": "query GetResult($query_id: Int!, $parameters: [Parameter!]) "
                               "{\n  get_result_v2(query_id: $query_id, parameters: $parameters) "
                               "{\n    job_id\n    result_id\n    error_id\n    __typename\n  }\n}\n"
                      }

        self.session.headers.update({'authorization': f'Bearer {self.token}'})

        response = self.session.post(GRAPH_URL, json=query_data)
        if response.status_code == 200:
            data = response.json()
            logger.debug(data)
            if 'errors' in data:
                logger.error(data.get('errors'))
                return None
            result_id = data.get('data').get('get_result_v2').get('result_id')
            return result_id
        else:
            logger.error(response.text)
            return None

    def query_result(self, result_id):
        """
        Fetch the result for a query
        :param result_id: result id of the query
        :return:
        """
        query_data = {"operationName": "FindResultDataByResult",
                      "variables": {"result_id": result_id, "error_id": "00000000-0000-0000-0000-000000000000"},
                      "query": "query FindResultDataByResult($result_id: uuid!, $error_id: uuid!) "
                               "{\n  query_results(where: {id: {_eq: $result_id}}) "
                               "{\n    id\n    job_id\n    runtime\n    generated_at\n    columns\n    __typename\n  }"
                               "\n  query_errors(where: {id: {_eq: $error_id}}) {\n    id\n    job_id\n    runtime\n"
                               "    message\n    metadata\n    type\n    generated_at\n    __typename\n  }\n"
                               "\n  get_result_by_result_id(args: {want_result_id: $result_id}) {\n    data\n    __typename\n  }\n}\n"
                      }

        self.session.headers.update({'authorization': f'Bearer {self.token}'})

        response = self.session.post(GRAPH_URL, json=query_data)
        if response.status_code == 200:
            data = response.json()
            logger.debug(data)
            return data
        else:
            logger.error(response.text)
            return {}



@pytest.mark.usefixtures('dune')
class TestDuneAnalytics:
    """
    Class to test DuneAnalytics
    """
    def test_login(self, dune):
        # try to login
        dune.login()
        assert dune.auth_refresh is not None
        assert dune.username is not None
        assert dune.password is not None
        assert dune.token is None

    def test_fetch_auth_token(self, dune):
        # fetch authentication token
        # dune.login()
        dune.fetch_auth_token()
        assert dune.auth_refresh is not None
        assert dune.username is not None
        assert dune.password is not None
        assert dune.token is not None

    # @pytest.mark.skip(reason='To be implemented')
    def test_query_result_id(self, dune):
        result_id = dune.query_result_id(query_id=3751)
        assert result_id is not None

    # @pytest.mark.skip(reason='To be implemented')
    def test_query_result(self, dune):
        result_id = dune.query_result_id(query_id=3705)
        assert result_id is not None
        data = dune.query_result(result_id)
        assert data is not None




#################################################################
#########     Download table of dune query data    ##############
#################################################################

# params
output_file_raw = "cow-3month-download.csv"
your_query_id = 37241 # this is the cow protocol ID
username = 
password = 

# fetch query results to json
dune = DuneAnalytics(username, password)
dune.login()
dune.fetch_auth_token()
result_id = dune.query_result_id(query_id=your_query_id)
data = dune.query_result(result_id)

print('got data')

# conversion of this dict into standard csv for import in gSheets
x = pd.DataFrame.from_dict(data)
keys = pd.DataFrame(x["data"]["get_result_by_result_id"])["data"][0].keys()
y = dict()
for i in pd.DataFrame(x["data"]["get_result_by_result_id"])["data"]:
    for k in keys:
         y.setdefault(k,[]).append(i[k])

print('sorted data')

pd.DataFrame(y).to_csv(output_file_raw, index=False)

print('done')



