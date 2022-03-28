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
                                default_http_header=_def_headers, status_forcelist=(500, 502, 503, 524),
                                backoff_factor=0.3)

        self._getTemplates()

    def _getTemplates(self):

        _url = os.path.join(self.base_url, 'templates')
        _is_complete = False
        limit = 50
        offset = 0
        all_templates = []

        while _is_complete is False:

            _params = {
                'limit': limit,
                'offset': offset
            }

            _rsp = self.get_raw(_url, params=_params)
            _template_sc = _rsp.status_code

            try:
                _template_js = _rsp.json()

            except ValueError:
                _template_js = {'templates': []}

            if _template_sc == 401:
                logging.error("API request received %s: %s. Process exiting!" % (_template_sc, _template_js['message']))
                logging.error("Please check the credentials.")

                sys.exit(1)

            elif _template_sc == 200:

                all_templates += [str(t['id']) for t in _template_js['templates']]

                if limit > len(_template_js['templates']):
                    _is_complete = True
                else:
                    offset += limit

            else:
                logging.error(f"Unhandled exception. Received: {_template_sc} - {_template_js}.")
                sys.exit(1)

        self.varTemplates = all_templates

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
            'Content-Type': 'application/json',
            'Accept': 'application/json'
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
                try:
                    logging.error("Received %s - %s." % (_mail_sc, _mail_js['message']))
                except KeyError:
                    logging.error(f"Could not parse error message : {_mail_js}")
                sys.exit(2)
