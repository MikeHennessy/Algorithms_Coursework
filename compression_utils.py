import copy
from queue import *
from dataclasses import *
from typing import *
from byte_utils import *

# [!] Important: This is the character code of the End Transmission Block (ETB)
# Character -- use this constant to signal the end of a message
ETB_CHAR = "\x17"

class HuffmanNode:
    '''
    HuffmanNode class to be used in construction of the Huffman Trie
    employed by the ReusableHuffman encoder/decoder below.
    '''
    
    # Educational Note: traditional constructor rather than dataclass because of need
    # to set default values for children parameters
    def __init__(self, char: str, freq: int, 
                 zero_child: Optional["HuffmanNode"] = None, 
                 one_child: Optional["HuffmanNode"] = None):
        '''
        HuffNodes represent nodes in the HuffmanTrie used to create a lossless
        encoding map used for compression. Their properties are given in this
        constructor's arguments:
        
        Parameters:
            char (str):
                Really, a single character, storing the character represented
                by a leaf node in the trie
            freq (int):
                The frequency with which the character / characters in a subtree
                appear in the corpus
            zero_child, one_child (Optional[HuffmanNode]):
                The children of any non-leaf, or None if a leaf; the zero_child
                will always pertain to the 0 bit part of the prefix, and vice
                versa for the one_child (which will add a 1 bit to the prefix)
        '''
        self.char = char
        self.freq = freq
        self.zero_child = zero_child
        self.one_child = one_child


    def __lt__(self, other: "HuffmanNode") -> bool:
        '''
        Less Than method that sets the priorities for the priority queue.
        
        Parameters:
            other ("HuffmanNode"):
                The node that is to be checked for its priority.
        Returns:
            bool:
                Whether the self node is a higher priority than the other node.
        '''

        priority: bool
        if self.freq != other.freq:
            priority = (self.freq < other.freq)
        else:
            priority = (ord(self.char.lower()) < ord(other.char.lower()))
        return priority


    def is_leaf(self) -> bool:
        '''
        Returns:
            bool:
                Whether or not the current node is a leaf
        '''
        return self.zero_child is None and self.one_child is None


class ReusableHuffman:
    '''
    ReusableHuffman encoder / decoder that is trained on some original
    corpus of text and can then be used to compress / decompress other
    text messages that have similar distributions of characters.
    '''


    def _generate_encoding_map(self, node: "HuffmanNode", code: str) -> None:
        '''
        Helper method that recursively creates an encoding map using a previously generated trie.
        
        Parameters:
            node ("HuffmanNode"):
                A current node in the trie that is being added to the encoding map.
            code (str):
                The current bitstring for the current node in the encoding map.
        Returns
            None
        '''
        if node.is_leaf():
            self._encoding_map[node.char] = code
        if node.zero_child is not None:
            self._generate_encoding_map(node.zero_child, code + "0")
        if node.one_child is not None:
            self._generate_encoding_map(node.one_child, code + "1")


    def __init__(self, corpus: str):
        '''
        Constructor for a new ReusableHuffman encoder / decoder that is fit to
        the given text corpus and can then be used to compress and decompress
        messages with a similar distribution of characters.
        
        Parameters:
            corpus (str):
                The text corpus on which to fit the ReusableHuffman instance,
                which will be used to construct the encoding map
        '''
        self._encoding_map: dict[str, str] = dict()

        nodes: PriorityQueue[HuffmanNode] = PriorityQueue()
        frequencies: dict[str, int] = dict()

        if corpus == "":
            self._encoding_map[ETB_CHAR] = "0"
        else:
            corpus += ETB_CHAR
            for char in corpus:
                if char not in frequencies:
                    frequencies[char] = 1
                else:
                    frequencies[char] += 1

            for char, frequency in frequencies.items():
                huffman_node: HuffmanNode = HuffmanNode(char, frequency, None, None)
                nodes.put(huffman_node)

            while nodes.qsize() >= 2:
                zero_child: HuffmanNode = nodes.get()
                one_child: HuffmanNode = nodes.get()
                earliest_char: str
                if ord(zero_child.char.lower()) < ord(one_child.char.lower()):
                    earliest_char = zero_child.char
                else:
                    earliest_char = one_child.char
                parent: HuffmanNode = HuffmanNode(earliest_char, zero_child.freq + one_child.freq, zero_child, one_child)
                nodes.put(parent)
            self._trie_root: HuffmanNode = nodes.get()

            self._generate_encoding_map(self._trie_root, "")


    def get_encoding_map(self) -> dict[str, str]:
        '''
        Simple getter for the encoding map that, after the constructor is run,
        will be a dictionary of character keys mapping to their compressed
        bitstrings in this ReusableHuffman instance's encoding
        
        Example:
            {ETB_CHAR: 10, "A": 11, "B": 0}
            (see unit tests for more examples)
        
        Returns:
            dict[str, str]:
                A copy of this ReusableHuffman instance's encoding map
        '''
        return copy.deepcopy(self._encoding_map)
    
    # Compression
    # ---------------------------------------------------------------------------
    
    def compress_message(self, message: str) -> bytes:
        '''
        Compresses the given String message / text corpus into its Huffman-coded
        bitstring, and then converted into a Python bytes type.
        
        [!] Uses the _encoding_map attribute generated during construction.
        
        Parameters:
            message (str):
                String representing the corpus to compress
        
        Returns:
            bytes:
                Bytes storing the compressed corpus with the Huffman coded
                bytecode. Formatted as (1) the compressed message bytes themselves,
                (2) terminated by the ETB_CHAR, and (3) [Optional] padding of 0
                bits to ensure the final byte is 8 bits total.
        
        Example:
            huff_coder = ReusableHuffman("ABBBCC")
            compressed_message = huff_coder.compress_message("ABBBCC")
            # [!] Only first 5 bits of byte 1 are meaningful (rest are padding)
            # byte 0: 1010 0011 (100 = ETB, 101 = 'A', 0 = 'B', 11 = 'C')
            # byte 1: 1110 0000
            solution = bitstrings_to_bytes(['10100011', '11100000'])
            self.assertEqual(solution, compressed_message)
        '''
        bitstring: str = ""

        for char in message:
            bitstring += self._encoding_map[char]

        bitstring += self._encoding_map[ETB_CHAR]
        bitstring += "0" * (8 - (len(bitstring) % 8))
        
        bitstring_list: List[str] = [bitstring[i:i+8] for i in range(0, len(bitstring), 8)]
        
        return bitstrings_to_bytes(bitstring_list)

    # Decompression
    # ---------------------------------------------------------------------------
    
    def decompress (self, compressed_msg: bytes) -> str:
        '''
        Decompresses the given bytes representing a compressed corpus into their
        original character format.
        
        [!] Should use the Huffman Trie generated during construction.
        
        Parameters:
            compressed_msg (bytes):
                Formatted as (1) the compressed message bytes themselves,
                (2) terminated by the ETB_CHAR, and (3) [Optional] padding of 0
                bits to ensure the final byte is 8 bits total.
        
        Returns:
            str:
                The decompressed message as a string.
        
        Example:
            huff_coder = ReusableHuffman("ABBBCC")
            # byte 0: 1010 0011 (100 = ETB, 101 = 'A', 0 = 'B', 11 = 'C')
            # byte 1: 1110 0000
            # [!] Only first 5 bits of byte 1 are meaningful (rest are padding)
            compressed_msg: bytes = bitstrings_to_bytes(['10100011', '11100000'])
            self.assertEqual("ABBBCC", huff_coder.decompress(compressed_msg))
        '''
        bitstring: str = ""
        for byte in compressed_msg:
            bitstring += byte_to_bitstring(byte)

        solution: str = ""
        current_node: HuffmanNode = self._trie_root

        for bit in bitstring:
            if bit == "0" and current_node.zero_child:
                current_node = current_node.zero_child
            elif bit == "1" and current_node.one_child:
                current_node = current_node.one_child
            
            if current_node.is_leaf():
                if current_node.char == ETB_CHAR:
                    break
                else:
                    solution += current_node.char
                    current_node = self._trie_root

        return solution

