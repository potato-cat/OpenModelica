#!/usr/bin/env python3

import xmlrpc.client
from subprocess import call
import natsort
import re

server = xmlrpc.client.ServerProxy("https://trac.openmodelica.org/OpenModelica/rpc")

releases = [i for i in server.wiki.getAllPages() if i.startswith("ReleaseNotes/")]
releases = natsort.natsorted(releases)
releases.reverse()
result = ""
for rel in releases:
  content = server.wiki.getPage(rel)
  content = re.sub(r'\[milestone:([0-9.]*)\]', r'\1', content)
  # '   * XXX' -> '*** XXX', wiki multi-level bullet
  n = 1
  while n>0:
    (content,n) = re.subn(r'^([*]*) ( *[*])', r'*\1\2', content, flags=re.M)
  content = re.sub(r'^([*]*) [*]', r'\1*', content)
  content = re.sub(r'== Detailed Changes ==\s*\[\[TicketQuery[^]]*\]\]', '', content, re.MULTILINE)
  open("tmp.wiki", "w").write(content)
  call(["pandoc", "--base-header-level=2", "-o", "tmp.rst", "tmp.wiki"])
  contentrst = open("tmp.rst", "r").read()
  # Removes {{{#!div lines; easier on the rst since it's a 1-line pattern
  contentrst = re.sub(r'`PageOutline\(2-3\) <PageOutline\(2-3\)>`__\n', '', contentrst)
  result += contentrst
open("tracreleases.inc", "w").write(result)
