import glob
import logging
import os
import shutil
import sys
from kbc.env_handler import KBCEnvHandler


MODE_KEY = 'mode'
PATTERN_KEY = 'pattern'
REPLACEMENT_KEY = 'replacement'
MANDATORY_PARS = [MODE_KEY, PATTERN_KEY, REPLACEMENT_KEY]


class Component(KBCEnvHandler):

    def __init__(self):

        KBCEnvHandler.__init__(self, MANDATORY_PARS)

        # Parameter fetching
        # self.paramMode = self.cfg_params[MODE_KEY]
        if self.cfg_params[PATTERN_KEY] == '{{NULL-BYTE}}':

            self.paramPattern = b'\x00'

        else:

            self.paramPattern = self.cfg_params[PATTERN_KEY].encode('utf-8')

        if self.cfg_params.get(REPLACEMENT_KEY) is None:

            self.paramReplacement = ''.encode('utf-8')

        else:

            self.paramReplacement = self.cfg_params[REPLACEMENT_KEY].encode('utf-8')

        self.files_in_path = os.path.join(self.data_path, 'in', 'files')
        self.files_out_path = os.path.join(self.data_path, 'out', 'files')

        logging.debug("Pattern to be replaced:")
        logging.debug(self.paramPattern)

        logging.debug("Replacement pattern:")
        logging.debug(self.paramReplacement)

    def changePathLocation(self, inPath):

        if '/in/files/' in inPath:

            return inPath.replace('/in/files/', '/out/files/')

        elif '/tables/' in inPath:

            return inPath.replace('/in/tables/', '/out/tables/')

        else:

            logging.error(
                "No matching criteria for path. Make sure the path is in correct form: ./in/files or ./in/tables.")
            sys.exit(1)

    def identifyAndCopyManifests(self):

        fileManifests = glob.glob(os.path.join(
            self.files_in_path, '*manifest'))
        tableManifests = glob.glob(os.path.join(
            self.tables_in_path, '*manifest'))
        allManifests = fileManifests + tableManifests

        logging.debug(allManifests)

        for _manifestPath in allManifests:

            _manifestOutPath = self.changePathLocation(_manifestPath)
            shutil.copyfile(_manifestPath, _manifestOutPath)

    def replaceCharacterStandard(self, filePath, outPath, pattern, replacement):

        with open(filePath, 'rb') as inFile, open(outPath, 'wb') as outFile:

            for row in inFile:
                logging.debug(row)
                replacedRow = row.replace(pattern, replacement)
                logging.debug(replacedRow)
                outFile.write(replacedRow)

    def run(self):

        self.identifyAndCopyManifests()

        fileCSV = glob.glob(os.path.join(self.files_in_path, '**', '*[!manifest]'), recursive=True)
        tableCSV = glob.glob(os.path.join(self.tables_in_path, '**', '*[!manifest]'), recursive=True)

        allCSV = fileCSV + tableCSV

        logging.debug("All files:")
        logging.debug(allCSV)

        logging.debug(self.data_path)
        logging.debug(self.files_in_path)

        for inPath in allCSV:

            logging.info("Processing file %s..." % inPath)

            outPath = self.changePathLocation(inPath)

            parentDir = os.path.dirname(outPath)
            if not os.path.exists(parentDir):

                os.makedirs(parentDir)

            self.replaceCharacterStandard(inPath, outPath, self.paramPattern, self.paramReplacement)

            logging.info("Processing of %s finished." % inPath)
