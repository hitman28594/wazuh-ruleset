#!/usr/bin/env python
# Copyright (C) 2015-2019, Wazuh Inc.
#
# This program is a free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation

import ConfigParser
import subprocess
import os
import sys
import os.path
import re


class OssecTester(object):
    def __init__(self):
        self._error = False
        self._debug = False
        self._quiet = False
        self._ossec_conf = "/var/ossec/etc/ossec.conf"
        self._base_dir = "/var/ossec/"
        self._ossec_path = "/var/ossec/bin/"
        self._test_path = "./tests"

    def buildCmd(self, rule, alert, decoder):
        cmd = ['%s/ossec-logtest' % (self._ossec_path), ]
        cmd += ['-q']
        if self._ossec_conf:
            cmd += ["-c", self._ossec_conf]
        if self._base_dir:
            cmd += ["-D", self._base_dir]
        cmd += ['-U', "%s:%s:%s" % (rule, alert, decoder)]
        return cmd


    def runTest(self, log, rule, alert, decoder, section, name, negate=False):
        #print self.buildCmd(rule, alert, decoder)
        p = subprocess.Popen(
                self.buildCmd(rule, alert, decoder),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                shell=False)
        std_out = p.communicate(log)[0]

        if("Level: '{0}'".format(alert) not in std_out):
            print ("\t LOG: " + log)
            print ("Level failed: " + alert)
            print("")
        if("Rule id: '2945'".format(rule) not in std_out):
            print ("\t LOG: " + log)
            print ("Rule failed: " + rule)
            print("")
        if ("Description: '{0}'".format(section) not in std_out):
            print ("\t LOG: " + log)
            print ("Description failed: " + section)
            print("")
        if ("decoder: '{0}'".format(decoder) not in std_out):
            print ("\t LOG: " + log)
            print ("Decoder failed: " + decoder)
            print("")

    def run(self, selective_test=False):
        for aFile in os.listdir(self._test_path):
            aFile = os.path.join(self._test_path, aFile)
            if aFile.endswith(".ini"):
                if selective_test and not aFile.endswith(selective_test):
                    continue
                print "- [ File = %s ] ---------" % (aFile)
                tGroup = ConfigParser.ConfigParser()
                tGroup.read([aFile])
                tSections = tGroup.sections()
                for t in tSections:
                    rule = tGroup.get(t, "rule")
                    alert = tGroup.get(t, "alert")
                    decoder = tGroup.get(t, "decoder")
                    for (name, value) in tGroup.items(t):
                        if name.startswith("log "):
                            if self._debug:
                                print "-" * 60
                            if name.endswith("pass"):
                                neg = False
                            elif name.endswith("fail"):
                                neg = True
                            else:
                                neg = False
                            if (value != ""):
                                self.runTest(value, rule, alert, decoder, t, name, negate=neg)
                print ""
        if self._error:
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        selective_test = sys.argv[1]
        if not selective_test.endswith('.ini'):
            selective_test += '.ini'
    else:
        selective_test = False
    OT = OssecTester()
    OT.run(selective_test)
