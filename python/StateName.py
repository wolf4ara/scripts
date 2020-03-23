from saltlint.linter import SaltLintRule
import os
import re

class StateName(SaltLintRule):
    id = '100'
    shortdesc = 'The name of state does not correspont to concept'
    description = 'The name of state will be "formula name"_"file name"_other'
    severity = 'HIGH'
    tags = ['naming']
    version_added = 'v0.0.1'

    def match(self, file, line):
        file_salt = re.sub('.sls', '', os.path.basename(file['path']))
        dirname = os.path.dirname(file['path'])
        dir_salt = dirname.split('/')[-1]
        pattern = dir_salt + "_" + file_salt + "_"
        if len(line) > 0:
            if line[0] != ' ' and line[0] != '{' and line[0] != '-' and line != 'include:' and line[len(line)-1] != '}':
                if line.find(pattern) != 0:
                    return 'The state\'s name is "<formula-name>_<file-name>_<other-desc>"'
