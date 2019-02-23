# Detangling PPI Network for Overlapping Clusters

We compare computational methods for decomposing a PPI network into overlapping clusters. Three popular community detection algorithms are tested before and after the network is pre-processed by removing and reweighting based on the diffusion state distance (DSD) between pairs of nodes in the network. We call this “detangling” the network. We also test these three algorithms on small networks pre-processed by DSD. A method has a better performance if it assigns a large proportion of nodes into functionally meaningful modules, as measured by functional enrichment over terms from the Gene Ontology. In most cases, we find that detangling the network based on the DSD distance reweighting provides more meaningful clusters.

Experiments Summary:

https://docs.google.com/document/d/1CazB84vBfcMogjPghMdwK7zT_1iybhVDdoPMsqebTBw/edit?usp=sharing


Three Algorithms:

COPRA: https://arxiv.org/pdf/0910.5516.pdf

OSLOM: http://www.oslom.org/software.html

link-community: https://ucilnica.fri.uni-lj.si/pluginfile.php/1212/course/section/1202/Ahn%20et%20al%20-%20Link%20communities%20reveal%20multi-scale%20complexity%20in%20networks%2C%202010.pdf


test_net: Self-designed small testing networks

eval: Evaluation codes for clustering results
