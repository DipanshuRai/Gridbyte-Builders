
class TrieNode:
    """A node in the Trie structure."""
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.count = 0

class Trie:
    """Trie structure for efficient prefix-based searching."""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, count=1):
        """Inserts a word into the trie and sets its frequency count."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.count = count