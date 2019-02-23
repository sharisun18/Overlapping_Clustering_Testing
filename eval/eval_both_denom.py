"""
Script for systematically evaluating yeast clustering results for functional
enrichment, using the FuncAssociate API

Modified by Taylor Yeracaris for overlapping clusters

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
SLEEP_TIME = 2 # originally 5

# TO-DO: control penalty function with command-line argument
def overlap_penalty(num_clusters):
# each vertex counts for (1 - overlap_penalty) in each enriched cluster
    # return 0.1*(num_clusters - 1)
    return 1 - (num_clusters ** (-0.5))

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
    unused_nodes = sum([len(cl) for cl in clusters if len(cl) < MIN_CL_SIZE])
    vertices = {}
    enriched_cluster_list = []
    print 'clusters to check: {}'.format(len(filtered_clusters))

    # initiate the vertex list (each vertex's value is the number of
    # clusters it's part of)
    for cluster in filtered_clusters:
        for v in cluster:
            vertices[v] = 0

    progress = 0
        
    for cluster in filtered_clusters:
        # print("CLUSTER", cluster)
        cluster_size = len(cluster)
        if cluster_size < MIN_CL_SIZE:
            continue

        # increase number of clusters for each vertex
        for v in cluster:
            vertices[v] += 1

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

        #print(response.json())
        if 'over' in response.json()['result']:
            result = response.json()['result']['over']
            if result:
                enriched_clusters += 1
                num_enrichments += len(result)
                enriched_cluster_list.append(cluster)
                
            valid_clusters = valid_clusters + 1
        time.sleep(SLEEP_TIME) # be nice to the API, wait a bit before next request
        progress += 1
        if progress % 10 == 0:
            print(progress)

    # overlap penalization
    for v in vertices:
        vertices[v] = 1 - overlap_penalty(vertices[v])
        if vertices[v] < 0:
            vertices[v] = 0
            
    score = 0 # total number of enriched vertices, minus penalty for overlap
    for cluster in enriched_cluster_list:
        for v in cluster:
            score += vertices[v]
            
    cluster_size_sum = 0 # sum of number of vertices in ceach cluster
    # divide score by this to get potentially more informative metric
    for cluster in filtered_clusters:
        cluster_size_sum += len(cluster)

    # is the score, as reported, particularly informative? Different denominator?
    print "Enrichment score penalizing overlap (denom. = sum of cluster sizes): {}".format(score/cluster_size_sum)
    print "Enrichment score penalizing overlap (denom. = total # of vertices): {}".format(score/len(vertices))
    print "Raw score: {}".format(score)
    print "Sum of cluster sizes: {}".format(cluster_size_sum)
    print "Total # of vertices: {}".format(len(vertices))
    print "Number of unused nodes: {}".format(unused_nodes)
    print "Enriched clusters (for p=0.05): {}".format(enriched_clusters)
    print "Total clusters: {}".format(total_clusters)
    print "Valid clusters: {}".format(valid_clusters)
    print "Enrichment ratio: {}".format(enriched_clusters / float(total_clusters))
    print "Average number of enrichments: {}".format(num_enrichments / float(total_clusters))
if __name__ == '__main__':
    main()
