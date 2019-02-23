# Detangling PPI Network for Overlapping Clusters

We compare computational methods for decomposing a PPI network into overlapping clusters. Three popular community detection algorithms are tested before and after the network is pre-processed by removing and reweighting based on the diffusion state distance (DSD) between pairs of nodes in the network. We call this “detangling” the network. We also test these three algorithms on small networks pre-processed by DSD. A method has a better performance if it assigns a large proportion of nodes into functionally meaningful modules, as measured by functional enrichment over terms from the Gene Ontology. In most cases, we find that detangling the network based on the DSD distance reweighting provides more meaningful clusters.

