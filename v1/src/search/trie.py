class TrieNode:
    def __init__(self):
        self.children = {}
        self.last = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
        print("Trie initialized with empty root")  # Debug print

    def formTrie(self, keys):
        """Initialize the trie with a list of keys."""
        print(f"Forming trie with {len(keys)} keys")  # Debug print
        for key in keys:
            self.insert(key)
        print("Trie formation complete")  # Debug print
    
    def insert(self, key):
        """Insert a key into the trie."""
        cur = self.root
        for char in key:
            if not cur.children.get(char):
                cur.children[char] = TrieNode()
            cur = cur.children[char]
        cur.last = True
    
    def suggestionsRec(self, node, word, words):
        """Recursively traverse the trie and collect words."""
        if node.last:
            words.append(word)

        for a, n in node.children.items():
            self.suggestionsRec(n, word + a, words)

    def autocomplete(self, prefix):
        """
        Return a list of words that start with the given prefix.
        
        Args:
            prefix (str): The prefix to search for
            
        Returns:
            List[str]: List of matching words
        """
        print(f"Searching for prefix: {prefix}")  # Debug print
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                print(f"Character '{ch}' not found in children")  # Debug print
                return []
            node = node.children[ch]

        results = []
        self.suggestionsRec(node, prefix, results)
        print(f"Found {len(results)} matches")  # Debug print
        return results



    

