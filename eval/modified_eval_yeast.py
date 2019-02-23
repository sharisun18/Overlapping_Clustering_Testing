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
SLEEP_TIME = 2 # original 5

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
    valid_clusters = 0
    bins_all = {}
    bins_enriched = {}
    unused_nodes = sum([len(cl) for cl in clusters if len(cl) < MIN_CL_SIZE])
    over_100s = [len(cl) for cl in clusters if len(cl) > 100]
    enriched_vertices = {}
    print len(filtered_clusters)
    for cluster in filtered_clusters:
        # print("CLUSTER", cluster)
        cluster_size = len(cluster)
        if cluster_size < MIN_CL_SIZE:
            continue
        power_of_2 = 2**(cluster_size-1).bit_length()
        if power_of_2 in bins_all:
            bins_all[power_of_2] += 1
        else: 
            bins_all[power_of_2] = 1
            bins_enriched[power_of_2] = 0
        #clustered_nodes = clustered_nodes + cluster_size

        data = {
            "id": 0,
            "method":"functionate",
            "species":"Saccharomyces cerevisiae",
            "namespace":"sgd_systematic",
            "query": ' '.join(cluster),
            "jsonrpc":2.0
        }
        print "requesting {}".format(filtered_clusters.index(cluster))
        response = requests.get(API_BASE_URL, params=data)
        if response.status_code != 200:
            # this might happen if the cluster is too large, if so it won't
            # count anyway so just skip it
            continue

        #print(response.json())
        if 'over' in response.json()['result']:
            result = response.json()['result']['over']
            if result:
                enriched_clusters += 1
                num_enrichments += len(result)
                bins_enriched[power_of_2] += 1

# OVERLAP SECTION
                
                for v in cluster:
                    if v in enriched_vertices:
                        enriched_vertices[v] -= 0.2 # ** decreasing factor penalizing overlap — should probably change **
                    else:
                        enriched_vertices[v] = 1
                print enriched_vertices # remove as soon as it starts working

# END OVERLAP SECTION

                try:
                    top_log_odds += result[0][3]
                except IndexError:
                    print result
            valid_clusters = valid_clusters + 1
        time.sleep(SLEEP_TIME) # be nice to the API, wait a bit before next request

    ratios = {}

    sorted_be = sorted(bins_enriched.items())
    sorted_ba = sorted(bins_all.items())
    for i in bins_all.keys():
        ratios[i] = bins_enriched[i]/float(bins_all[i])

    print "Number of unused nodes: {}".format(unused_nodes)
    print "Enriched clusters (for p=0.05): {}".format(enriched_clusters)
    print "Total clusters: {}".format(total_clusters)
    print "Valid clusters: {}".format(valid_clusters)
    print "Enrichment ratio: {}".format(enriched_clusters / float(total_clusters))
    print "Average number of enrichments: {}".format(num_enrichments / float(total_clusters))
    print "Average top log odds score: {}".format(top_log_odds / float(total_clusters))
    print "Enrichment ratio for each cluster size:"
    for i in ratios.keys():
        print "Size: {}".format(i) + " Ratio: {}".format(ratios[i])
    print "total bins: "
    print sorted_ba
    print "enriched clusters: "
    print sorted_be
    print "clusters over 100 nodes: "
    print over_100s
    print "enrichment score (accounting for overlap - but incomplete, see note): {}".format(sum(enriched_vertices))
# should report sum DIVIDED by total number of vertices; haven't programmed the counting-vertices part yet, though

if __name__ == '__main__':
    main()
