import logging
import json
import os
import sys
from kbc.client_base import HttpClientBase

BASE_URL = 'https://api.sendinblue.com/v3/smtp'


class sendInBlueClient(HttpClientBase):

    def __init__(self, apiKey):

        self.paramApiKey = apiKey

        _def_headers = {"Accept": "application/json",
                        "api-key": apiKey}

        HttpClientBase.__init__(self, base_url=BASE_URL, max_retries=10,
                                default_http_header=_def_headers, status_forcelist=(500, 502),
                                backoff_factor=0.3)

        self._getTemplates()

    def _getTemplates(self):

        _url = os.path.join(self.base_url, 'templates')
        _rsp = self.get_raw(_url)
        _template_sc = _rsp.status_code

        try:
            _template_js = _rsp.json()

        except ValueError:
            _template_js = {}

        if _template_sc == 401:

            logging.error("API request received %s: %s. Process exiting!" % (_template_sc, _template_js['message']))
            logging.error("Please check the credentials.")

            sys.exit(1)

        elif _template_sc == 200:

            logging.info("Templates obtained.")
            self.varTemplates = [str(t['id']) for t in _template_js['templates']]

            logging.debug("Template ids downloaded:")
            logging.debug(self.varTemplates)

    def sendTransactionalEmail(self, toObject, templateId, params=None, cc=None, bcc=None):

        _url = os.path.join(self.base_url, 'email')
        _body = {
            'to': json.loads(toObject),
            'templateId': int(templateId)
        }

        if params is not None:
            _body['params'] = json.loads(params)

        if cc is not None:
            _body['cc'] = json.loads(cc)

        if bcc is not None:
            _body['bcc'] = json.loads(bcc)

        _header = {
            'Content-Type': 'application/json'
        }

        logging.debug(_body)

        _rsp = self.post_raw(_url, data=json.dumps(_body), headers=_header)
        _mail_sc = _rsp.status_code

        try:
            _mail_js = _rsp.json()

        except ValueError:
            _mail_js = {}

        if _mail_sc == 201:

            return _mail_sc, _mail_js['messageId']

        else:

            logging.warning("Received status code %s: %s." % (_mail_sc, _mail_js))

            if _mail_sc == 400:

                return _mail_js, _mail_js['message']

            else:

                logging.error("Unhandled exception. Exiting!")
                logging.error("Received %s - %s." % (_mail_sc, _mail_js['message']))
                sys.exit(2)
