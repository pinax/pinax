# $Id: benchmark.py 1757 2004-03-28 17:21:25Z fredrik $
# simple elementtree benchmark program

from elementtree import XMLTreeBuilder, SimpleXMLTreeBuilder
from elementtree import SgmlopXMLTreeBuilder
from xml.dom import minidom

import sys, time

try:
    file = sys.argv[1]
except IndexError:
    file = "hamlet.xml"

def benchmark(file, builder_module):
    source = open(file, "rb")
    t0 = time.time()
    parser = builder_module.TreeBuilder()
    while 1:
        data = source.read(32768)
        if not data:
            break
        parser.feed(data)
    tree = parser.close()
    t1 = time.time()
    print "%s: %d nodes read in %.3f seconds" % (
        builder_module.__name__, len(tree.getiterator()), t1-t0
        )
    raw_input("press return to continue...")
    del tree

def benchmark_minidom(file):
    t0 = time.time()
    dom = minidom.parse(file)
    t1 = time.time()
    print "minidom tree read in %.3f seconds" % (t1-t0)
    raw_input("press return to continue...")
    del dom

benchmark(file, XMLTreeBuilder)
benchmark(file, SimpleXMLTreeBuilder) # use xmllib
try:
    benchmark(file, SgmlopXMLTreeBuilder) # use sgmlop
except RuntimeError, v:
    print "=== SgmlopXMLTreeBuilder not available (%s)" % v
benchmark_minidom(file)
