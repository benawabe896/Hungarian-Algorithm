"""
Very interesting problem.  
Was able to see a nice solve here: https://bitbucket.org/cynah/maxsuitabilityscore/src/796b142d6632 
and an interesting map reduce version here: https://github.com/jyotisj/Discount-Offers

Neither of them were able to work as they are incomplete, but it was nice to build on.  I am familiar
with the assignment problem, but I wasn't familiar with this Hungarian algorithm.  
Great article about it here: http://community.topcoder.com/tc?module=Static&d1=tutorials&d2=hungarianAlgorithm

"""

import itertools
import sys
import math
import string
import re

class Hungarian(object):
    def __init__(self, G):
        self.G = G
        self.lU = dict()
        self.lV = dict()
        for u in G.U:
            self.lU[u] = G.getMaxWeightOfVertex(u)
        for v in G.V:
            self.lV[v] = 0

    def getPerfectMatching(self):
        M = list()
        while not self._isPerfectMatching(M):
            S = list()
            T = list()
            u = self._getFreeVertex(M)
            S.append(u)
            while True:
                neigbors = self._getNeighborOfSet(S)
                if self._hasEqualElements(neigbors, T):
                    alpha = self._getAlphaValue(S, T)
                    self._setNewLabeling(S, T, alpha)
                    continue
                v = self._getVertexFromSubtractionOfSets(neigbors, T)
                w = map(lambda (x, y): x, filter(lambda (x, y): y == v, M))
                if w:
                    for z in w:
                        if z not in S:
                            S.append(z)
                    if v not in T:
                        T.append(v)
                else:
                    T.append(v)
                    A = self._getAugmentPath(u, S, M, T, v)
                    AandMc = filter(lambda x: x not in M, A)
                    M = filter(lambda x: x not in A, M)
                    M.extend(AandMc)
                    break
        return M

    def _getFreeU(self, M):
        matchedU = map(lambda (x, y): x, M)
        freeU = filter(lambda x: x not in matchedU, self.lU.keys())
        return freeU

    def _getFreeV(self, M):
        matchedV = map(lambda (x, y): y, M)
        freeV = filter(lambda x: x not in matchedV, self.lV.keys())
        return freeV

    def _isPerfectMatching(self, M):
        perfectU = len(self._getFreeU(M)) == 0
        perfectV = len(self._getFreeV(M)) == 0
        return any([perfectU, perfectV])

    def _getFreeVertex(self, M):
        freeU = self._getFreeU(M)
        assert(len(freeU) >= 1)
        return freeU.pop(0)

    def _getNeighborOfSet(self, S):
        result = list()
        for u in S:
            for v in self.lV.keys():
                if self._isNeighbor(u, v) and v not in result:
                    result.append(v)
        return result

    def _isNeighbor(self, u, v):
        u_val = self.lU.get(u)
        v_val = self.lV.get(v)
        assert(u_val is not None and v_val is not None)
        return self.G.getWeightOfEdge(u, v) == u_val + v_val

    def _hasEqualElements(self, S, T):
        if len(S) <> len(T):
            return False
        S.sort()
        T.sort()
        return S == T

    def _getVertexFromSubtractionOfSets(self, S, T):
        result = filter(lambda x: x not in T, S)
        assert(len(result) >= 1)
        return result.pop(0)

    def _getAlphaValue(self, S, T):
        result = list()
        _T = filter(lambda x: x not in T, self.lV.keys())
        for u in S:
            for v in _T:
                u_val = self.lU.get(u)
                v_val = self.lV.get(v)
                assert(u_val is not None and v_val is not None)
                result.append(u_val + v_val - self.G.getWeightOfEdge(u, v))
        return min(result)

    def _setNewLabeling(self, S, T, alpha):
        for u in S:
            curr_val = self.lU.get(u)
            self.lU[u] = curr_val - alpha
        for v in T:
            curr_val = self.lV.get(v)
            self.lV[v] = curr_val + alpha

    def _getAugmentPath(self, u, S, M, T, v):
        graph = dict()
        for s in S:
            neighbor = self._getNeighborOfSet([s])
            graph[s] = filter(lambda x: x in T, neighbor)
        for t in T:
            matched = map(lambda (x, y): x, filter(lambda (x, y): y == t, M))
            if matched:
                graph[t] = matched
            else:
                neighbor = list()
                for s in S:
                    if self._isNeighbor(s, t):
                        neighbor.append(s)
                graph[t] = neighbor
        aug_path = list()
        tmp_path = [u]
        q = list()
        q.append(tmp_path)
        while len(q) > 0:
            _path = q.pop(0)
            last_node = _path[len(_path)-1]
            if last_node == v:
                aug_path = _path
                break
            for link_node in graph[last_node]:
                if link_node not in _path:
                    new_path = []
                    new_path = _path + [link_node]
                    q.append(new_path)
        result = list()
        for i in range(0, len(aug_path), 2):
            s = aug_path[i]
            t = aug_path[i+1]
            result.append((s, t))
            matched = filter(lambda (x, y): x == s or y == t, M)
            result.extend(matched)
        return result

class WeightedBipartiteGraph(object):
    def __init__(self, U, V, E):
        self.U = U
        self.V = V
        self.E = E

    def getWeightOfEdge(self, u, v):
        return self.E.get((u, v), 0)

    def getMaxWeightOfVertex(self, u):
        result = list()
        for v in self.V:
            result.append(self.getWeightOfEdge(u, v))
        return max(result)

class Entity(object):

    @staticmethod
    def getFactors(namelength):
        factors = list()
        _sqrt = int(math.sqrt(namelength))
        for i in range(1, _sqrt + 1):
            if not namelength % i:
                _i = namelength / i
                if i <> 1:
                    factors.append(i)
                if _i <> 1:
                    factors.append(_i)
        factors = {}.fromkeys(factors).keys()
        factors.sort()
        return factors

    def __init__(self, name):
        self.name = name
        self.namelength = len("".join([ch for ch in name if ch in (string.ascii_letters)]))
        self.factors = Entity.getFactors(self.namelength)

class Product(Entity):

    def __repr__(self):
        return '<Product name: %s (%s) factors: [ %s ]>' % (self.name,
                self.namelength, ', '.join([str(x) for x in self.factors]))

    def nameLengthIsEven(self):
        return self.namelength % 2 == 0

class Customer(Entity):

    vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'A', 'E', 'I', 'O', 'U', 'Y']

    @staticmethod
    def getAlphabetCount(name):
        return len(filter(lambda x: x in string.ascii_letters, name))

    @staticmethod
    def getVowelCount(name):
        return len(filter(lambda x: x in Customer.vowels, name))

    def __init__(self, name):
        super(Customer, self).__init__(name)
        alphabet_count = Customer.getAlphabetCount(name)
        self.vowel_count = Customer.getVowelCount(name)
        self.consonant_count = alphabet_count - self.vowel_count

    def __repr__(self):
        return '<Customer name: %s (%s) factors: [ %s ] vow: %s con: %s>' %\
                (self.name, self.namelength,
                ', '.join([str(x) for x in self.factors]),
                self.vowel_count, self.consonant_count)

def nameHasCommonDivisor(product, customer):
    return len(filter(lambda x: x in product.factors, customer.factors)) > 0

def getSuitabilityScore(product, customer):
    result = 0
    if product.nameLengthIsEven():
        result = customer.vowel_count * 1.5
    else:
        result = customer.consonant_count * 1.0
    
    return result * 1.5 if nameHasCommonDivisor(product, customer) else result

        
if __name__ == '__main__':
    if len(sys.argv) <> 3:
        sys.exit(' '.join(['usage:', 'python', sys.argv[0],
                '<products>', '<customers>']))
    product_by_pid = dict()
    customer_by_cid = dict()
    U = list()
    V = list()
    E = dict()
    with open(sys.argv[1], 'r') as fp:
        for pid, line in itertools.izip(itertools.count(), fp):
            product_by_pid[pid] = Product(line.strip())
            U.append(pid)
    with open(sys.argv[2], 'r') as fp:
        for cid, line in itertools.izip(itertools.count(len(U)), fp):
            customer_by_cid[cid] = Customer(line.strip())
            V.append(cid)
    for pid, product in product_by_pid.iteritems():
        for cid, customer in customer_by_cid.iteritems():
            E[(pid, cid)] = getSuitabilityScore(product, customer)
    wbgraph = WeightedBipartiteGraph(U, V, E)
    hungarian = Hungarian(wbgraph)
    result = hungarian.getPerfectMatching()
    for pid, cid in result:
        product = product_by_pid.get(pid)
        customer = customer_by_cid.get(cid)
    print 'Total Suitability Score: %s' % (sum(map(lambda x: E.get(x), result)))

