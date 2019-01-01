from collections import namedtuple, Counter
from math import log
import os
import gzip
import numpy as np

RT = "/Users/yangzhong/Desktop/NLPparser/mturk_specificity/cleaned_data/MetaOptimize/BrownWC/"

BROWNCLUSFILE_100 = RT + "brown-rcv1.clean.tokenized-CoNLL03.txt-c100-freq1.txt"
BROWNCLUSFILE = RT + "bronwn-rcv1-1000-freq1.txt"

STOPWORDFILE = RT + "data/nltkstopwords.txt"


def readPdtbConns():
    conns = set()
    with open(CONNFILE) as f:
        for line in f:
            conns.add(line.strip())
        f.close()
    return conns


def readMpqa():
    MPQAEntry = namedtuple("MPQAEntry", "isstem,subj,polarity")
    ret = {}
    with open(MPQAFILE) as f:
        for line in f:
            if len(line.strip()) == 0: continue
            fields = [x.split("=")[1] for x in line.strip().split()]
            isstem = True if fields[4] == "y" else False
            entry = MPQAEntry(isstem, fields[0], fields[-1])
            ret[fields[2]] = entry
    return ret


def readGenInq():
    inq_dict = {}
    for line in open(GENINQFILE, 'r'):
        info = line.strip().split()
        if not info: continue
        word = info[0]
        stmt = Counter(info[1:])
        ## pos,neg,strong,weak
        inq_dict[word] = (
            max(stmt['Pos'], stmt['Pstv']), max(stmt['Neg'], stmt['Ngtv']),
            stmt['Strng'], stmt['Weak'])
    return inq_dict


def readMetaOptimizeBrownCluster_100():
    print ("loading brown clusters...")
    word_cluster_d = {}
    cluster_2_index = {}
    with open(BROWNCLUSFILE_100, "r", encoding='utf-8') as f:
        for line in f:
            bitstr, word, numocc = line.strip().split("\t")
            word_cluster_d[word] = bitstr
            if bitstr not in cluster_2_index:
                cluster_2_index[bitstr] = len(cluster_2_index)

    print ("done; # words: ,", len(word_cluster_d))
    return word_cluster_d, cluster_2_index


def readMetaOptimizeBrownCluster():
    print ("loading brown clusters...")
    word_cluster_d = {}
    cluster_2_index = {}
    with open(BROWNCLUSFILE, "r", encoding='utf-8') as f:
        for line in f:
            bitstr, word, numocc = line.strip().split("\t")
            word_cluster_d[word] = bitstr
            if bitstr not in cluster_2_index:
                cluster_2_index[bitstr] = len(cluster_2_index)

    print ("done; # words: ,", len(word_cluster_d))
    return word_cluster_d, cluster_2_index


def readMetaOptimizeEmbeddings():
    print ("loading word embeddings...")
    f = gzip.open(NEURALVECFILE, 'rb')
    embdict = {}
    counter = 0
    for line in f:
        fields = line.strip().split(" ")
        embdict[fields[0]] = np.array([float(x) for x in fields[1:]])
        counter += 1
    f.close()
    print ("done; # words: ", counter)
    return embdict


def readMrc():
    ## export original mrc as only the following fields (starting from 0):
    ## familiarity (25-27), concretness (28-30), imagery (31-33),
    ## mean colorado meaningfullness (34-36), mean pavlo meaningfulness (37-39)
    ## word is located at first position of "|"
    MRCEntry = namedtuple("MRCEntry", "fami,conc,img,mcolo,mpavlo")
    mrcdict = {}
    with open(MRCFILE) as f:
        for line in f:
            fields = line.strip().split()
            fami = int(fields[0][25:28])
            conc = int(fields[0][28:31])
            img = int(fields[0][31:34])
            mcolo = int(fields[0][34:37])
            mpavlo = int(fields[0][37:40])
            word = fields[-1].split("|", 1)[0].lower()
            mrcdict[word] = MRCEntry(fami, conc, img, mcolo, mpavlo)
    return mrcdict


def readIdfFile(filename):
    d = {};
    doccount = 0
    with open(filename) as f:
        i = 0
        for line in f:
            if i == 0:
                doccount = int(line.strip().split(": ")[1])
                i += 1
            elif i == 1:
                i += 1
            else:
                word, df, idf = line.strip().split()
                if not word.isalpha(): continue
                d[word] = float(idf)
        f.close()
    return d, doccount


def readIdf():
    idfd, dct = readIdfFile(IDF_FILE)
    idflowerd, dct = readIdfFile(IDF_FILE2)
    default_oov = log(dct + 0.0)
    return idfd, idflowerd, default_oov


def readStopwords():
    ret = set()
    with open(STOPWORDFILE) as f:
        for line in f:
            l = line.strip()
            if len(l) > 0:
                ret.add(l)
        f.close()
    return ret
