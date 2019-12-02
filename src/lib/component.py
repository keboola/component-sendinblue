import csv
import json
import logging
import sys
from lib.client import sendInBlueClient
from lib.result import resultWriter
from kbc.env_handler import KBCEnvHandler


API_KEY = '#apiKey'

MANDATORY_PARAMS = [API_KEY]
REQUIRED_COLUMNS = ['emailObject', 'templateId']


class Component(KBCEnvHandler):

    def __init__(self):

        KBCEnvHandler.__init__(self, MANDATORY_PARAMS)
        self.validate_config(MANDATORY_PARAMS)

        self.paramApiKey = self.cfg_params[API_KEY]
        self.varInputTables = self.configuration.get_input_tables()
        self._checkInputTables()

        self.client = sendInBlueClient(apiKey=self.paramApiKey)
        self.writer = resultWriter(self.data_path)

    def _checkInputTables(self):

        if len(self.varInputTables) == 0:

            logging.error("No input table provided.")
            sys.exit(1)

        for _table in self.varInputTables:

            _tablePath = _table['full_path']
            _manPath = _tablePath + '.manifest'

            with open(_manPath) as _manFile:

                _manifest = json.load(_manFile)

            _columnDiff = set(REQUIRED_COLUMNS) - set(_manifest['columns'])

            if len(_columnDiff) != 0:

                logging.error("Missing columns %s in table %s. Please check the input mapping." %
                              (list(_columnDiff), _table['source']))
                sys.exit(1)

    def _check_json(self, dictToCheck, dictType):
        # type = ['to', 'bcc', 'params']

        if dictToCheck is None and dictType in ('cc', 'bcc', 'params'):

            return True

        try:

            dictJS = json.loads(dictToCheck)

            if dictType in ('to', 'cc', 'bcc') and isinstance(dictJS, list):

                return True

            elif dictType in ('to', 'cc', 'bcc') and not isinstance(dictJS, list):

                return False

            elif dictType == 'params' and isinstance(dictJS, dict):

                return True

            elif dictType == 'params' and not isinstance(dictJS, dict):

                return False

            else:

                logging.error("Unhandled dictType.")
                sys.exit(2)

        except ValueError:

            return False

    def run(self):

        for table in self.varInputTables:

            with open(table['full_path'], 'r') as _inFile:

                _rdr = csv.DictReader(_inFile)

                for row in _rdr:

                    toObject = row['emailObject']
                    templateId = row['templateId']
                    paramsObject = row.get('params')
                    ccObject = row.get('ccObject')
                    bccObject = row.get('bccObject')

                    if templateId not in self.client.varTemplates:

                        logging.warn("Unknown template %s. Skipping row!" % templateId)

                        _errDict = {
                                    'error': 'templateError',
                                    'errorMessage': "Template does not exist.",
                                    'additionalInfo': templateId,
                                    'emailObject': toObject
                                    }

                        self.writer.writerErrors.writerow(_errDict)
                        continue

                    if paramsObject == '' or paramsObject == '{}':
                        paramsObject = None

                    if ccObject == '' or ccObject == '{}':
                        ccObject = None

                    if bccObject == '' or bccObject == '{}':
                        bccObject = None

                    toObjectCheck = self._check_json(toObject, 'to')
                    paramsObjectCheck = self._check_json(paramsObject, 'params')
                    ccObjectCheck = self._check_json(ccObject, 'cc')
                    bccObjectCheck = self._check_json(bccObject, 'bcc')

                    if not all([toObjectCheck, paramsObjectCheck, ccObjectCheck, bccObjectCheck]):

                        logging.warn("Invalid object detected.")

                        _errDict = {
                                    'error': 'JSONError',
                                    'errorMessage': "Invalid input format for one of " +
                                                    "emailObject, paramObject, ccObject, bccObject.",
                                    'additionalInfo': [toObjectCheck, paramsObjectCheck, ccObjectCheck, bccObjectCheck],
                                    'emailObject': toObject
                                    }

                        self.writer.writerErrors.writerow(_errDict)

                        continue

                    logging.info(f"Sending email to {toObject}")

                    _sc, _msg = self.client.sendTransactionalEmail(
                        toObject=toObject, templateId=templateId, params=paramsObject,
                        cc=ccObject, bcc=bccObject)

                    if _sc == 201:

                        _msgDict = {
                            'messageId': _msg,
                            'emailObject': json.dumps(toObject)
                        }

                        self.writer.writerMessages.writerow(_msgDict)

                    else:

                        _errDict = {
                            'error': 'sendError',
                            'errorMessage': _sc,
                            'additionalInfo': _msg,
                            'emailObject': json.dumps(toObject)
                        }

                        self.writer.writerErrors.writerow(_errDict)
