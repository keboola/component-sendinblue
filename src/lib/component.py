import csv
import json
import logging
import sys
from lib.client import sendInBlueClient
from lib.result import resultWriter
from kbc.env_handler import KBCEnvHandler


API_KEY = '#apiKey'
# SENDER_EMAIL_KEY = 'sender.email'
# SENDER_NAME_KEY = 'sender.name'
# REPLYTO_EMAIL_KEY = 'replyTo.email'
# REPLYTO_NAME_KEY = 'replyTo.name'
BATCH_USAGE_KEY = 'batch.usage'
BATCH_SIZE_KEY = 'batch.size'

MANDATORY_PARAMS = [API_KEY]
REQUIRED_COLUMNS = ['email', 'name', 'templateId']


class Component(KBCEnvHandler):

    def __init__(self):

        KBCEnvHandler.__init__(self, MANDATORY_PARAMS)
        self.validate_config(MANDATORY_PARAMS)

        self.paramApiKey = self.cfg_params[API_KEY]
        self.paramBatchUsage = False if self.cfg_params.get(BATCH_USAGE_KEY) is None \
            else self.cfg_params[BATCH_USAGE_KEY]
        self.paramBatchSize = self.cfg_params.get(BATCH_SIZE_KEY)

        assert isinstance(self.paramBatchUsage, bool), "Parameter \"batch.usage\" must be a boolean"
        assert isinstance(self.paramBatchSize, int), "Parameter \"batch.size\" must be a boolean"

        self.varInputTables = self.configuration.get_input_tables()
        self._checkInputTables()

        self.client = sendInBlueClient(apiKey=self.paramApiKey,
                                       # senderEmail=self.paramSenderEmail,
                                       # senderName=self.paramSenderName,
                                       # replyToEmail=self.paramReplyToEmail,
                                       # replyToName=self.paramReplyToName
                                       )

        self.writer = resultWriter(self.data_path)

        '''
        self.varSenderObject = {'email': self.paramSenderEmail}
        if self.paramSenderName is not None or self.paramSenderName != '':
            self.varSenderObject['name'] = self.paramSenderName

        self.varReplyToObject = {'email': self.paramReplyToEmail}
        if self.paramReplyToName is not None or self.paramReplyToName != '':
            self.varReplyToObject['name'] = self.paramReplyToName

        logging.debug("Sender object:")
        logging.debug(self.varSenderObject)

        logging.debug("ReplyTo object:")
        logging.debug(self.varReplyToObject)
        '''

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

    def splitRecipients(self):

        templateIds = []
        recipients = {}

        for _table in self.varInputTables:

            _tablePath = _table['full_path']
            with open(_tablePath) as tableFile:

                _reader = csv.DictReader(tableFile)

                for row in _reader:

                    _tId = row['templateId']

                    if _tId.isdigit() is True:

                        _tIdConverted = int(_tId)

                    else:

                        _tIdConverted = _tId

                    toRecipient = {'email': row['email'],
                                   'name': row['name']}

                    if _tIdConverted not in templateIds:

                        templateIds += [_tIdConverted]
                        recipients[_tIdConverted] = [toRecipient]

                    elif _tIdConverted in templateIds:

                        recipients[_tIdConverted] += [toRecipient]

        logging.debug("Recipients object:")
        logging.debug(recipients)

        self.varRecipients = recipients

    @staticmethod
    def _divideList(listToDivide, resultSize):

        for i in range(0, len(listToDivide), resultSize):

            yield listToDivide[i:i + resultSize]

    def run(self):

        self.splitRecipients()
        batchesSent = 0

        for templateId in self.varRecipients:

            toObject = self.varRecipients[templateId]

            if templateId not in self.client.varTemplates:

                logging.warn(
                    "Unknown template %s. Skipping configuration." % templateId)

                _errDict = {
                    'recipients': json.dumps(toObject),
                    'error': 'templateError',
                    'errorMessage': "Template does not exist.",
                    'templateId': templateId
                }

                self.writer.writerErrors.writerow(_errDict)
                continue

            if self.paramBatchUsage is True:

                toObjectSplit = self._divideList(toObject, self.paramBatchSize)

            else:

                toObjectSplit = self._divideList(toObject, 1)

            for toObj in toObjectSplit:

                logging.debug("Recipients:")
                logging.debug(toObj)

                _sc, _msg = self.client.sendTransactionalEmail(
                    toObject=toObj, templateId=templateId)

                if _sc == 201:

                    batchesSent += 1
                    _msgDict = {
                        'messageId': _msg,
                        'recipients': json.dumps(toObj)
                    }

                    self.writer.writerMessages.writerow(_msgDict)

                else:

                    _errDict = {
                        'recipients': json.dumps(toObj),
                        'error': 'sendError',
                        'errorMessage': ' - '.join([_sc, _msg]),
                        'templateId': templateId
                    }

                    self.writer.writerErrors.writerow(_errDict)

        logging.info("Sent %s emails." % batchesSent)
