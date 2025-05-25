class TrieNode():
    def __init__(self):
        self.children = {}
        self.last = False

class Trie():
    def __init__(self):
        self.root = TrieNode()

    def formTrie(self, keys):
        for key in keys:
            self.insert(key)
    
    def insert(self,key):
        cur = self.root
        for char in key:
            if not cur.children.get(char):
                cur.children[char] = TrieNode()
            cur = cur.children[char]
        cur.last = True
    
    def suggestionsRec(self, node, word, words):

        # Method to recursively traverse the trie
        # and return a whole word.
        
        if node.last:
            if not None:
                words.append(word)

        for a, n in node.children.items():
            self.suggestionsRec(n, word + a,words)
        
        

    def autocomplete(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]

        results = []
        self.suggestionsRec(node, prefix, results)
        return results
    

    

