"""
Script for systematically evaluating yeast clustering results for functional
enrichment, using the FuncAssociate API

TODO: maybe allow p-value input?

example URL (get request):
http://llama.mshri.on.ca/cgi/funcassociate/serv?id=0&method=functionate&query=YBR293W+YCL069W+YMR088C&species=Saccharomyces%20cerevisiae&namespace=sgd_systematic
'''

"""
import sys
import time
import argparse
import requests

API_BASE_URL = 'http://llama.mshri.on.ca/cgi/funcassociate/serv'
MIN_CL_SIZE = 3
SLEEP_TIME = 2

def read_clusters(cluster_file):
    try:
        fp = open(cluster_file, 'r')
    except IOError:
        sys.exit('Could not open file: {}'.format(cluster_file))

    clusters = [line.rstrip().split()[2:] for line in fp.readlines()]
    fp.close()
    return clusters

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cluster_file", help="Cluster results file")
    opts = parser.parse_args()
    clusters = read_clusters(opts.cluster_file)
    filtered_clusters = [cl for cl in clusters if len(cl) >= MIN_CL_SIZE]
    enriched_clusters, total_clusters = 0, len(filtered_clusters)
    num_enrichments, top_log_odds = 0, 0

    count = 0
    for cluster in filtered_clusters:
        print count
        count += 1

        data = {
            "id": 0,
            "method":"functionate",
            "species":"Saccharomyces cerevisiae",
            "namespace":"sgd_systematic",
            "query": ' '.join(cluster),
            "jsonrpc":2.0
        }
        response = requests.get(API_BASE_URL, params=data)
        if response.status_code != 200:
            # this might happen if the cluster is too large, if so it won't
            # count anyway so just skip it
            continue
        result = response.json()['result']['over']

        if result:
            enriched_clusters += 1
            num_enrichments += len(result)
            try:
                top_log_odds += result[0][3]
            except IndexError:
                print result


        time.sleep(SLEEP_TIME) # be nice to the API, wait a bit before next request

    print "Enriched clusters (for p=0.05): {}".format(enriched_clusters)
    print "Total clusters: {}".format(total_clusters)
    print "Enrichment ratio: {}".format(enriched_clusters / float(total_clusters))
    print "Average number of enrichments: {}".format(num_enrichments / float(total_clusters))
    print "Average top log odds score: {}".format(top_log_odds / float(total_clusters))

if __name__ == '__main__':
    main()
