from bigO import BigO
from bigO import algorithm

lib = BigO()

# lib.runtime(algorithm.insertSort, "reversed", 32)
# lib.compare(algorithm.insertSort, algorithm.bubbleSort, "all", 5000)


totalsize=[]
def mergeFiles(fileSizes):
    print(fileSizes)
    # Write your code here
    while(len(fileSizes)>2):
        fileSizes.sort()
        first = fileSizes[0]
        second = fileSizes[1]
        fileSizes.pop(0)
        fileSizes.pop(0)
        # for i in fileSizes:
        first = first+second
        totalsize.append(first)
        fileSizes.append(first)
        # mergeFiles(fileSizes)
    # else:
    
    if(len(fileSizes)==2):
        Sum=sum(totalsize)
        return fileSizes[0]+fileSizes[1]+Sum
    elif(len(totalsize)==0):
        return (fileSizes[0])
    else:
        Sum=sum(totalsize)
        return (fileSizes[0]+Sum)


mergeFiles([20,4,8,2])


complexity = lib.test(mergeFiles, "random")
