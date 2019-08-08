import csv
import json
import os
from kbc.result import KBCResult, KBCTableDef

FIELDS_MESSAGES = ['messageId', 'recipients']
PK_MESSAGES = ['messageId']

FIELDS_ERRORS = ['recipients', 'error', 'errorMessage', 'templateId']
PK_ERRORS = []


class resultWriter:

    def __init__(self, dataPath):

        self.paramDataPath = dataPath
        self.run()

    def createTableDefinition(self, tableName, tableColumns, tablePK):

        _fileName = tableName + '.csv'
        _fullPath = os.path.join(self.paramDataPath, 'out', 'tables', _fileName)

        _tableDef = KBCTableDef(
            name=tableName, columns=tableColumns, pk=tablePK)
        _resultDef = KBCResult(file_name=_fileName,
                               full_path=_fullPath, table_def=_tableDef)

        return _resultDef

    @staticmethod
    def createWriter(tableDefinition):

        _writer = csv.DictWriter(open(tableDefinition.full_path, 'w'),
                                 fieldnames=tableDefinition.table_def.columns,
                                 restval='', extrasaction='ignore',
                                 quotechar='"', quoting=csv.QUOTE_ALL)

        _writer.writeheader()

        return _writer

    @staticmethod
    def createManifest(destination, pk=[], incremental=False):

        _manifest = {'primary_key': pk, 'incremental': incremental}

        with open(destination, 'w') as _manFile:

            json.dump(_manifest, _manFile)

    def run(self):

        _msgTableDef = self.createTableDefinition(
            'messages', FIELDS_MESSAGES, PK_MESSAGES)
        self.writerMessages = self.createWriter(_msgTableDef)
        self.createManifest(destination=_msgTableDef.full_path + '.manifest',
                            pk=_msgTableDef.table_def.pk,
                            incremental=True)

        _errTableDef = self.createTableDefinition(
            'errors', FIELDS_ERRORS, PK_ERRORS)
        self.writerErrors = self.createWriter(_errTableDef)
        self.createManifest(destination=_errTableDef.full_path + '.manifest',
                            pk=_errTableDef.table_def.pk)
