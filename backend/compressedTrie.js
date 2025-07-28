// backend/compressedTrie.js

class RadixNode {
  constructor() {
    this.children = {};        // key: edge label (string), value: RadixNode
    this.isEnd = false;        // indicates if it's the end of a valid word
    this.word = null;          // stores the full word (for suggestions)
  }
}

class CompressedTrie {
  constructor() {
    this.root = new RadixNode();
  }

  insert(word) {
    this._insert(this.root, word.toLowerCase(), word);
  }

  _insert(node, remaining, fullWord) {
    for (let key in node.children) {
      const commonPrefixLen = this._commonPrefixLength(remaining, key);

      if (commonPrefixLen === 0) continue;

      const commonPrefix = key.substring(0, commonPrefixLen);
      const oldSuffix = key.substring(commonPrefixLen);
      const newSuffix = remaining.substring(commonPrefixLen);

      const child = node.children[key];
      delete node.children[key];

      // Create new intermediate node
      const intermediate = new RadixNode();
      node.children[commonPrefix] = intermediate;

      // Reattach existing child
      if (oldSuffix) {
        intermediate.children[oldSuffix] = child;
      } else {
        intermediate.isEnd = child.isEnd;
        intermediate.word = child.word;
        intermediate.children = child.children;
      }

      // Add new branch if needed
      if (newSuffix) {
        const newNode = new RadixNode();
        newNode.isEnd = true;
        newNode.word = fullWord;
        intermediate.children[newSuffix] = newNode;
      } else {
        intermediate.isEnd = true;
        intermediate.word = fullWord;
      }

      return;
    }

    // No matching prefix found; add new child
    const newNode = new RadixNode();
    newNode.isEnd = true;
    newNode.word = fullWord;
    node.children[remaining] = newNode;
  }

  getSuggestions(prefix, limit = 5) {
    const results = [];
    this._search(this.root, prefix.toLowerCase(), '', results, limit);
    return results;
  }

_search(node, prefix, path, results, limit) {
  for (let key in node.children) {
    const child = node.children[key];
    const commonPrefixLen = this._commonPrefixLength(prefix, key);

    if (commonPrefixLen === 0) continue;

    if (commonPrefixLen < key.length && commonPrefixLen < prefix.length) {
      // Partial match, not enough to descend
      continue;
    }

    if (commonPrefixLen === prefix.length) {
      // Match complete — dive for all completions
      this._dfs(child, path + key, results, limit);
      return;
    }

    // Keep searching
    this._search(child, prefix.slice(commonPrefixLen), path + key, results, limit);
  }
}


//   _search(node, prefix, path, results, limit) {
//     for (let key in node.children) {
//       const child = node.children[key];

//       if (prefix.startsWith(key)) {
//         // Prefix completely covers this key; go deeper
//         this._dfs(child, path + key, results, limit);
//       } else if (key.startsWith(prefix)) {
//         // Prefix is part of this key — e.g., prefix = 'ap', key = 'apple'
//         if (child.isEnd) results.push(child.word);
//         this._dfs(child, path + key, results, limit);
//       } else if (this._commonPrefixLength(prefix, key) > 0) {
//         // Partial match (no suggestion)
//         continue;
//       }

//       if (results.length >= limit) return;
//     }
//   }

  _dfs(node, path, results, limit) {
    if (node.isEnd) results.push(node.word);
    if (results.length >= limit) return;

    for (let key in node.children) {
      if (results.length >= limit) break;
      this._dfs(node.children[key], path + key, results, limit);
    }
  }

  _commonPrefixLength(a, b) {
    let i = 0;
    while (i < a.length && i < b.length && a[i] === b[i]) i++;
    return i;
  }
}

module.exports = CompressedTrie;
