'''
Created on April 3, 2020
FP-Growth Algorithm
@author: ZhihaoXu
'''
class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None # connect same element, dash line in the tree
        self.parent = parentNode      #needs to be updated
        self.children = {} 
    
    def inc(self, numOccur):
        self.count += numOccur
        
    # display the tree, used for debug
    def disp(self, ind=1):
        print('  '*ind, self.name, ':', self.count)
        for child in self.children.values():
            child.disp(ind+1)

'''
create FP-tree
'''

def createTree(dataSet, minSup=1): #create FP-tree from dataset but don't mine
    headerTable = {}
    # scan the dataSet once
    # counts frequency of each item's occurance and create headerTable
    for trans in dataSet:
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]

    #delete items less than minSup
    headerTableCopy = headerTable.copy()
    for k in headerTableCopy.keys():  
        if headerTable[k] < minSup: 
            del(headerTable[k])

    freqItemSet = set(headerTable.keys()) # L1
    if len(freqItemSet) == 0:
        return None, None  

    #reformat headerTable to use Node link 
    for k in headerTable:
        headerTable[k] = [headerTable[k], None] 
    #print('headerTable: ',headerTable)
    retTree = treeNode('Null Set', 1, None) #create tree

    #scan the dataSet 2nd time
    for tranSet, count in dataSet.items():  
        localD = {}
        for item in tranSet:  #put transaction items in alphabet order
            if item in freqItemSet: # only consider frequent items
                localD[item] = headerTable[item][0]
        for k,v in sorted(localD.items(), key=lambda item: item[0]): # sorted by item value
            localD[k] = v

        if len(localD) > 0:
            orderedItems = []
            localD = sorted(localD.items(), key=lambda p: p[0])
            for v in sorted(localD, key=lambda p: p[1], reverse=True):
                orderedItems.append(v[0])
            updateTree(orderedItems, retTree, headerTable, count)#populate tree with ordered freq itemset
    return retTree, headerTable #return tree and header table

# connect the node to the target header 
def updateHeader(nodeToTest, targetNode):   
    while (nodeToTest.nodeLink != None):  
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode

def updateTree(items, inTree, headerTable, count):
    #check if items[0] in retTree.children (as a child)
    if items[0] in inTree.children:
        inTree.children[items[0]].inc(count) #add count
    else:
        #add items[0] to inTree.children (create a new branch)
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        #update header table 
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    #recursion for next items
    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)

'''
mine FP-tree
'''


# find all the pattern ends by the leafNode (ascend from leaf to root)
def ascendTree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)
    
def findPrefixPath(treeNode): #treeNode from header table
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath) # from tree node to root
        if len(prefixPath) > 1: 
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink # next basePat
    return condPats

def mineFPTree(inTree, headerTable, preFix, freqItemDict, minSup, numItems):
    bigL = []
    # sort header table
    for v in sorted(headerTable.items(), key=lambda p: p[0]):
        bigL.append(v[0])
    # print('Conditional Header: ',bigL)

    for basePat in bigL:
        # print('Base Pattern: ',basePat)
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        support = headerTable[basePat][0]
        # print('Final Frequent Item: ',newFreqSet)    #append to set
        
        freqItemDict[frozenset(newFreqSet)] = support/numItems
        condPattBases = findPrefixPath(headerTable[basePat][1])
        # print('Conditional Pattern Bases :',basePat, condPattBases)

        #construct cond FP-tree from cond. pattern base
        myCondTree, myHead = createTree(condPattBases, minSup)

         #3. mine cond. FP-tree
        if myHead != None:
            # print('step4 conditional tree for: ',newFreqSet)
            # myCondTree.disp(1)
            # recurrsively mine the conditional FP-tree
            mineFPTree(myCondTree, myHead, newFreqSet, freqItemDict, minSup, numItems)

def loadSimpDat():
    
    simpDat = [['r', 'z', 'h', 'j', 'p'],
               ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
               ['z'],
               ['r', 'x', 'n', 'o', 's'],
               ['y', 'r', 'x', 'z', 'q', 't', 'p'],
               ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]
    return simpDat

# formulate it to element:count
def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        retDict[frozenset(trans)] = 1
    return retDict


if __name__ == "__main__":
    simpDat = loadSimpDat()
    # print('step1 dataSet: ',simpDat)
    initSet = createInitSet(simpDat)
    # print('step2 sorted dataset: ',initSet)
    myFPtree, myHeaderTab = createTree(initSet, minSup=3)
    # print('step3 FP-Tree: ')
    # myFPtree.disp()

    # print('step3 headerTable: ',myHeaderTab)
    freqItemsDict = {}
    mineFPTree(myFPtree, myHeaderTab, set([]), freqItemsDict, minSup=3, numItems=float(len(simpDat)))
    print('step4 myFreqList: ',freqItemsDict)
    # print('step4 myFPtree.children: ',{myFPtree.children.values()})