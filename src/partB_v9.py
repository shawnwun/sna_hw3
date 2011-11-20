import sys;
import os;
import networkx as nx;
import random;
import operator;
from copy import copy;

#use average similarity, add not assigned nodes by some metrics, modify both assigned code

def main(argv=None):
    graphFile = sys.argv[1];
    typeFile = sys.argv[2];
    outputFile = sys.argv[3];

    inputFh = open(graphFile, 'r');

    graph = nx.Graph();

    #read graph
    for line in inputFh:
        line = line.replace("\n", "");
        splitLine = line.partition("\t");

        if (len(splitLine) == 3):
            node1 = int(splitLine[0]);
            node2 = int(splitLine[2]);
            graph.add_node(node1);
            graph.add_node(node2);            
            graph.add_edge(node1, node2);
    
    inputFh.close();

    #read part a partitions
    inputFh = open(typeFile, 'r');

    line = inputFh.readline();

    line = line.strip();
    #line = line.replace(" \n", "");
    splitLine = line.split(" ");

    timeNodes = [];

    for token in splitLine:
        if token == " ":
            continue;

        timeNodes.append(int(token));


    placeNodes = [];
    
    line = inputFh.readline();
    
    #line = line.replace(" \n", "");
    line = line.strip();
    splitLine = line.split(" ");

    for token in splitLine:
        if token == " ":
            continue;
        placeNodes.append(int(token));

    movieNodes = [];
    
    line = inputFh.readline();
    
    #line = line.replace(" \n", "");
    line = line.strip();
    splitLine = line.split(" ");

    for token in splitLine:
        if token == " ":
            continue;
        movieNodes.append(int(token));


    personNodes = [];
    
    line = inputFh.readline();
    
    #line = line.replace(" \n", "");
    line = line.strip();
    splitLine = line.split(" ");

    for token in splitLine:
        if token == " ":
            continue;
        personNodes.append(int(token));


    inputFh.close();

    candidate= [];
    allNodes = graph.nodes();

    while len(candidate) < 100:
        rand = random.randint(0, len(timeNodes)-1);

        if timeNodes[rand] in candidate:
            continue;

        candidate.append(timeNodes[rand]);

        
    #print len(candidate);
    #print sorted(candidate);

    isValid = False;

    index = 0;
    visitedAll = {};
    while not isValid:
        print "Run %d" % index;
        isValid = randomWalk(graph, visitedAll, outputFile, candidate, timeNodes, movieNodes, personNodes, placeNodes);
        index+=1;

def randomWalk(graph, visitedAll, outputFile, candidate, timeNodes, movieNodes, personNodes, placeNodes):
    
    #random walk
    print "Random Walk";
    for run in range (0, 10000):
        for time in candidate:
            if time in visitedAll:
                visited = visitedAll[time];
            else:
                visited = {};
                
            currNode = time;
            oldNodes = [];
            for steps in range(0, 3):
                neighbor = graph.neighbors(currNode);
                nodeTried = [];
                while (True):
                    if len(nodeTried) == len(neighbor):
                        currNode = -1;
                        break;
                    else:
                        val = random.randint(0, len(neighbor)-1);
                        currNode = neighbor[val];

                        #nodeTried.append(currNode);
                        if not (currNode in oldNodes):
                            #oldNodes.append(currNode);
                            break;
                if currNode == -1:
                    break;

                if currNode in visited:
                    visited[currNode] = visited[currNode] + 1;
                else:
                    visited[currNode] = 1;
                    
            visitedAll[time] = visited;

    clusters = {};

    for time in candidate:
        visitedCount = visitedAll[time];


        hist = buildHist(visitedCount);
        nodeList = [];

        for count in hist:
            if count < 3:
                continue;

            nodes = hist[count];

            for n in nodes:
                nodeList.append(n);

        clusters[time] = nodeList;
        #print len(nodeList);
        #print visitedCount;
        #print "--------";

    clustersList = [];
    for time in clusters:
        clustersList.append(clusters[time]);

    index = 0;

    intersectDict = {};    

    for i in range(0, len(clustersList)):
        interForI = {};
        index = 0;
        for j in range(0, len(clustersList)):            
            
            if not (i == j):            
                list1 = clustersList[i];
                list2 = clustersList[j];

                intersect = list(set(list1).intersection( set(list2)));

                
                interForI[index] = int(1000*float(len(intersect))/float(  (len(list1)+len(list2))  /2));
                
            else:
                interForI[index] = 0;
            index+=1;

        intersectDict[i] = interForI;
        #print interForI;
    
    perNodeRanking = {};
    allRanking = {};
    for i in intersectDict:
        interForI = intersectDict[i];

        for j in interForI:
            allRanking[(i,j)] = interForI[j];
        
        ranking = [];
        for node in interForI:
            ranking.append(interForI[node]);

        perNodeRanking[i] = ranking;

    #print "Node i to j intersect count";
    #print perNodeRanking;
    #print "";

    #generate intersect count to (node1, node2) dictionary
    sortedRank = sorted(allRanking.iteritems(), key=operator.itemgetter(1), reverse=True);
    rankings = {};
    #print sortedRank;
    for nodeTuple, count in sortedRank:
        if count == 0:
            continue;
        reverTuple = (nodeTuple[1], nodeTuple[0]);        
        if count in rankings:
            tupleList = rankings[count];
            if reverTuple in tupleList:
                continue;
            tupleList.append(nodeTuple);
        else:
            tupleList = [];
            tupleList.append(nodeTuple);

        rankings[count] = tupleList;

    '''for count in rankings:
        tupleList = rankings[count];
        sys.stdout.write("%d: " % count);
        print tupleList;
    '''
    #print statement. KEEP!!!
    '''
    for i in intersectDict:
        sys.stdout.write("%d: " % i);
        print intersectDict[i];
        print perNodeRanking[i];
    '''

    #print"";
    clusters = [];
    assigned = {};
    for rank in sorted(rankings.iterkeys(), reverse=True):
        tupleList = rankings[rank];

        for nodeTuple in tupleList:
            node1 = nodeTuple[0];
            node2 = nodeTuple[1];

        
            #print "%d,%d" % (node1, node2); 

            #both assigned, continue
            if node1 in assigned and node2 in assigned:
                if assigned[node1] == assigned[node2]:
                    continue;
                else:
                    nodeList1 = clusters[assigned[node1]];                    
                    clSum1 = 0;
                    for node in nodeList1:
                        clSum1 += perNodeRanking[node][node2];
                    clSum1 = float(clSum1) / float(len(nodeList1));

                    nodeList2 = clusters[assigned[node2]];
                    clSum2 = 0;

                    for node in nodeList2:
                        clSum2 += perNodeRanking[node][node1];
                    clSum2 = float(clSum2) / float(len(nodeList2));

                    if clSum2 > clSum1:
                        nodeList2.append(node1);
                        nodeList1.remove(node1);
                        clusters[assigned[node2]] = nodeList2;
                        clusters[assigned[node1]] = nodeList1;                        
                        assigned[node1] = assigned[node2];
                    else:
                        nodeList1.append(node2);
                        nodeList2.remove(node2);
                        clusters[assigned[node1]] = nodeList1;
                        clusters[assigned[node2]] = nodeList2;
                        assigned[node2] = assigned[node1];
                        
            elif node1 in assigned:
                node1C = assigned[node1];
                nodeList = clusters[node1C];
                nodeList.append(node2);
                assigned[node2] = node1C;
                clusters[node1C] = nodeList;
                #print "Node 1 assigned";
                #print clusters;
                #print "";
            elif node2 in assigned:
                node2C = assigned[node2];
                nodeList = clusters[node2C];
                nodeList.append(node1);
                assigned[node1] = node2C;
                clusters[node2C] = nodeList;
                #print "Node 2 assigned";
                #print clusters;
                #print "";
            else:
                #find a cluster that fits the 2 nodes best
                maxSum = 0;
                maxIndex = 0;
                index = 0;
                for nodeList in clusters:
                    if len(nodeList) == 0:
                        continue;
                    clSum = 0;
                    for node in nodeList:
                        clSum += perNodeRanking[node][node1];
                        clSum += perNodeRanking[node][node2];
                    clSum = clSum / (2*len(nodeList));
                    #print "%d, %.2f" % (index, clSum);
                    if clSum > maxSum:
                        maxSum = clSum;
                        maxIndex = index;

                    index+=1;
                #neither assigned
                if len(clusters) < 10 and perNodeRanking[node1][node2] > maxSum:
                        #print "Node %d and %d sim: %d, maxSim: %d" % (node1, node2, perNodeRanking[node1][node2], maxSum);
                        nodeList = [];
                        nodeList.append(node1);
                        nodeList.append(node2);

                        assigned[node1] = len(clusters);
                        assigned[node2] = len(clusters);
                    
                        clusters.append(nodeList);
                    
                        #print "Assign new group"
                        #print clusters;
                        #print "";
                else:
                    nodeList = clusters[maxIndex];
                    nodeList.append(node1);
                    nodeList.append(node2);
                    assigned[node1] = maxIndex;
                    assigned[node2] = maxIndex;
                    
                    #print "Assign existing group %d" % maxIndex;
                    #print clusters;
                    #print "";

        #re-order step
        #   first get all the min nodes from clusters > 10
        haveTried = {};
        reorderNodes = [];
        while (True):
            reorderNodes = [];
            for nodeList in clusters:
                while len(nodeList) > 10:
                    minSum = sys.maxint;
                    minNode = -1;
                    for node in nodeList:
                        nodeSum = 0;
                        for nei in nodeList:
                            if nei == node:
                                continue;
                            nodeSum += perNodeRanking[node][nei];                        
    
                        if nodeSum < minSum:
                            minSum = nodeSum;
                            minNode = node;
                    nodeList.remove(minNode);
                    reorderNodes.append(minNode);

                    if not (minNode in haveTried):
                        haveTried[minNode] = [];

            if len(reorderNodes) == 0:
                break;
            
            for node in reorderNodes:
                maxSum = 0;
                maxIndex = -1;
                index = 0;
                triedList = haveTried[node];
                
                for nodeList in clusters:
                    if index in triedList:
                        index+=1;
                        continue;
                    if len(nodeList) == 0:
                        triedList.append(index);
                        continue;
                    
                    clSum = 0;
                    for n in nodeList:
                        clSum += perNodeRanking[node][n];                        
                    clSum /= len(nodeList);
                    #print "%d, %.2f" % (index, clSum);
                    if clSum > maxSum and not (index == assigned[node]):
                        maxSum = clSum;
                        maxIndex = index;
    
                    index+=1;

                if maxIndex == -1:
                    nodeList = [];
                    nodeList.append(node);
                    clusters.append(nodeList);
                    assigned[node] = len(clusters) -1;
                else:
                    nodeList = clusters[maxIndex];
                    nodeList.append(node);
                    clusters[maxIndex] = nodeList;
                    assigned[node] = maxIndex;
                    triedList.append(maxIndex);
                    haveTried[node] = triedList;
                    
                #print "Reassign node: %d to cluster: %d" % (node, maxIndex);
                #print clusters;
                #print "";

    tClusters = [];
    for tNodeList in clusters:
        clusters = [];
        for node in tNodeList:
            clusters.append(candidate[node]);
        tClusters.append(sorted(clusters));

    '''for cl in tClusters:
        print cl;
    '''

    finalClusters = [];
    for tNodeList in tClusters:
        nodeList = [];

        for tNode in tNodeList:            
            
            neighbors = graph.neighbors(tNode);
            nodeList.append(tNode);

            for nei in neighbors:
                nodeList.append(nei);

                neiNeighbors = graph.neighbors(nei);

                for n in neiNeighbors:
                    nodeList.append(n);
                       
            

        finalClusters.append(list(set(nodeList)));

    #print "";
    #print "clusters:";


    index = 0;
    for clusters in finalClusters:        
        tCount = 0;
        mCount = 0;
        plCount = 0;
        perCount = 0;
        
        for node in clusters:
            if node in timeNodes:
                tCount+=1;
            elif node in movieNodes:
                mCount+=1;
            elif node in placeNodes:
                plCount+=1;
            elif node in personNodes:
                perCount+=1;
            
        index+=1;
        #print "Size: %d, T: %d, M:%d, Per:%d, PL:%d" % (tCount+mCount+perCount+plCount, tCount, mCount, perCount, plCount);
    
    notAssigned = [];
    allNodes = graph.nodes();
    tCount = 0;
    mCount = 0;
    perCount = 0;
    plCount = 0;
    for node in allNodes:
        assigned = False;

        for cluster in finalClusters:
            if node in cluster:
                assigned = True;
                break;

        if not assigned:
            notAssigned.append(node);
            if node in timeNodes:
                tCount+=1;
            elif node in movieNodes:
                mCount+=1;
            elif node in personNodes:
                perCount+=1;
            elif node in placeNodes:
                plCount+=1;

    #print "Not assigned:";
    #print sorted(notAssigned);
    #print "Size: %d, T: %d, M:%d, Per:%d, PL:%d" % (len(notAssigned), tCount, mCount, perCount, plCount);
    
    
    for node in notAssigned:
        twoLevNeighbors = [];
        neighbors = graph.neighbors(node);

        for nei in neighbors:
            twoLevNeighbors.append(nei);
            neiOfNeighbors = graph.neighbors(nei);

            for nei2 in neiOfNeighbors:
                twoLevNeighbors.append(nei2);
        
        index = 0;
        maxInter = 0;
        maxIndex = -1;
        for nodeList in finalClusters:
            intersection = set(nodeList).intersection(set(twoLevNeighbors));

            if len(intersection) > maxInter:
                maxIndex = index;
                maxInter = len(intersection);

            index+=1;
            
        nodeList = finalClusters[maxIndex];
        nodeList.append(node);
        finalClusters[maxIndex] = list(set(nodeList));
   
    isValid = True;

    for clusters in finalClusters:
        if len(clusters) > 7100:
            isValid = False;
            break;

    if isValid:
        f = file(outputFile, 'w');

        for clusters in finalClusters:
            count = 0;        
            for node in clusters:
                f.write("%s" % node);
                if count == len(clusters)-1:
                    f.write("\n");
                else:
                    f.write(" ");
                count+=1;            
        f.close();

    print "Final Clusters";
    for clusters in finalClusters:        
        tCount = 0;
        mCount = 0;
        plCount = 0;
        perCount = 0;
        
        for node in clusters:
            if node in timeNodes:
                tCount+=1;
            elif node in movieNodes:
                mCount+=1;
            elif node in placeNodes:
                plCount+=1;
            elif node in personNodes:
                perCount+=1;
        
        print "Size: %d, T: %d, M:%d, Per:%d, PL:%d" % (len(clusters), tCount, mCount, perCount, plCount);

    return isValid;

def buildHist(visited):
    hist = {};
    maxSteps = 0;
    for node in visited:
        visitCount = visited[node];

        if visitCount in hist:
            nodeList = hist[visitCount];
            nodeList.append(node);
        else:
            if visitCount > maxSteps:
                maxSteps = visitCount;
            nodeList = [];
            nodeList.append(node);

        hist[visitCount] = nodeList;

    '''for i in range(0, maxSteps+1):
        if i in hist:
            sys.stdout.write("%d," % len(hist[i]));
        else:
            sys.stdout.write("0,");
        
    print "";'''
    return hist;

if __name__ == "__main__":
    sys.exit(main());
