#!/usr/bin/env python
from openid.consumer.discover import discover, DiscoveryFailure
from openid.fetchers import HTTPFetchingError

names = [["server_url",  "Server URL  "],
         ["local_id",    "Local ID    "],
         ["canonicalID", "Canonical ID"],
        ]

def show_services(user_input, normalized, services):
    print " Claimed identifier:", normalized
    if services:
        print " Discovered OpenID services:"
        for n, service in enumerate(services):
            print " %s." % (n,)
            for attr, name in names:
                val = getattr(service, attr, None)
                if val is not None:
                    print "  %s: %s" % (name, val)

            print "  Type URIs:"
            for type_uri in service.type_uris:
                print "   *", type_uri

            print

    else:
        print " No OpenID services found"
        print

if __name__ == "__main__":
    import sys

    for user_input in sys.argv[1:]:
        print "=" * 50
        print "Running discovery on", user_input
        try:
            normalized, services = discover(user_input)
        except DiscoveryFailure, why:
            print "Discovery failed:", why
            print
        except HTTPFetchingError, why:
            print "HTTP request failed:", why
            print
        else:
            show_services(user_input, normalized, services)
