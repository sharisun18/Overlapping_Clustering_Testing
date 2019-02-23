"""
Script for systematically evaluating DREAM clustering results for functional
enrichment, using the FuncAssociate API

example URL (get request):
http://llama.mshri.on.ca/cgi/funcassociate/serv?id=0&method=functionate&query=SLC22A4+SLC22A5&species=Homo%20sapiens&namespace=hgnc_symbol

"""
import sys
import time
import logging
import traceback
import argparse
import requests

API_BASE_URL = 'http://llama.mshri.on.ca/cgi/funcassociate/serv'
MIN_CL_SIZE = 3
SLEEP_TIME = 5

def read_clusters(cluster_file):
    try:
        fp = open(cluster_file, 'r')
    except IOError:
        sys.exit('Could not open file: {}'.format(cluster_file))

    clusters = [line.rstrip().split()[2:] for line in fp.readlines()]
    fp.close()
    return clusters

def read_significant(module_file):
    try:
        fp = open(module_file, 'r')
    except IOError:
        sys.exit('Could not open file: {}'.format(module_file))

    # files are 0 indexed, input is 1 indexed so add 1
    significant_map = {}
    for idx, line in enumerate(fp.readlines()):
        if idx < 3:
            continue
        l = line.rstrip().split('\t')
        map_index = int(l[0])+1
        if map_index in significant_map:
            significant_map[map_index].append(l[1])
        else:
            significant_map[map_index] = [l[1]]
    fp.close()
    return significant_map

def read_bipartite(module_file):
    try:
        fp = open(module_file, 'r')
    except IOError:
        sys.exit('Could not open file: {}'.format(module_file))

    # files are 0 indexed, input is 1 indexed so add 1
    indices = [int(line.rstrip())+1 for line in fp.readlines()]
    fp.close()
    return indices

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cluster_file", help="Cluster results file")
    parser.add_argument("-b", "--bipartite_modules", default=None,
                        help="File with indices of bipartite modules")
    parser.add_argument("-s", "--significant_modules", default=None,
                        help="File with indices of significant modules")
    opts = parser.parse_args()
    clusters = read_clusters(opts.cluster_file)
    significant_map = (read_significant(opts.significant_modules) if
                         opts.significant_modules is not None else [])
    bipartite_modules = (read_bipartite(opts.bipartite_modules) if
                         opts.bipartite_modules is not None else [])
    filtered_clusters = [cl for cl in clusters if len(cl) >= MIN_CL_SIZE]
    enriched_clusters, total_clusters = 0, len(filtered_clusters)
    num_enrichments, top_log_odds = 0, 0

    for cl_ix, cluster in enumerate(filtered_clusters, 1):
        data = {
            "id": 0,
            "method":"functionate",
            "species":"Homo sapiens",
            "namespace":"hgnc_symbol",
            "query": ' '.join(cluster),
            "jsonrpc":2.0
        }
        response = requests.get(API_BASE_URL, params=data)
        if response.status_code != 200:
            # this might happen if the cluster is too large, if so it won't
            # count anyway so just skip it
            continue
        try:
            result = response.json()['result']['over']
            for r in result:
                print r
                print
            return
        except KeyError:
            logging.info('Key error:\n{}\n'.format(response.json()['result']))
            continue
        print '{}\t{}\n'.format(cl_ix, '\t'.join(cluster))
        if len(bipartite_modules) > 0:
            print 'Bipartite:\t{}'.format('Yes' if cl_ix in bipartite_modules
                                          else 'No')
        print 'Significant:\t{}\n'.format('Yes' if cl_ix in significant_map
                                        else 'No')
        if cl_ix in significant_map:
            print "Significant for GWAS:\n{}\n".format('\n'.join(significant_map[cl_ix]))
        if result:
            try:
                print 'Functional enrichment:'
                for annotation in result[:10]:
                    print '{}\t{}'.format(annotation[3], annotation[7])
                print ''
                enriched_clusters += 1
                num_enrichments += len(result)
                top_log_odds += result[0][3]
            except IndexError:
                print result
        else:
            print 'No significantly enriched annotations found\n'
        time.sleep(SLEEP_TIME) # be nice to the API, wait a bit before next request

    print "-----------------------------------------------------------"
    print "Summary"
    print "-----------------------------------------------------------"
    print "Enriched clusters (for p=0.05): {}".format(enriched_clusters)
    print "Total clusters: {}".format(total_clusters)
    print "Enrichment ratio: {}".format(enriched_clusters / float(total_clusters))
    print "Average number of enrichments: {}".format(num_enrichments / float(total_clusters))
    print "Average top log odds score: {}".format(top_log_odds / float(total_clusters))

if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=20,
                        format="%(asctime)s\n%(message)s")
    try:
        main()
    except Exception:
        logging.error('{}\n{}'.format(' '.join(sys.argv), traceback.format_exc()))
        sys.exit(traceback.format_exc())

    logging.info('{}\n{}\n'.format(' '.join(sys.argv), 'Completed successfully'))

