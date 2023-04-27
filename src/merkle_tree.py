 # Python code for implemementing Merkle Tree
from typing import List
import hashlib
import math
class Node:
	def __init__(self, left, right, value: str, content, is_copied=False) -> None:
		#Initialize a new node of the Merkle Tree.
 	
		#- left (Node): The left child node.
		#- right (Node): The right child node.
		#- value (str): The hash value of the node.
		#- content (str): The content of the node.
		#- is_copied (bool): A flag indicating whether the node is a copy (True) or not (False).

		self.left: Node = left
		self.right: Node = right
		self.value = value
		self.content = content
		self.is_copied = is_copied
		self.is_left = None
		self.parent: Node = None
	
	@staticmethod
	def hash(val: str) -> str:
		# val (str): The input string to hash.
		# The SHA-256 hash of the input string.

		return hashlib.sha256(val.encode('utf-8')).hexdigest()

	def __str__(self):
		return (str(self.value))  #Converts and returns string implementation of node

	def copy(self):
		#creates and returns the copy of a node. 
		return Node(self.left, self.right, self.value, self.content, True)

	# def set_parent(self, parent):
	# 	self.parent = parent
	

class MerkleTree:  # Defining the MerkleTree class

	def __init__(self, addresses: List[str]) -> None:
		#Initialize a new Merkle Tree.
		self.addresses = addresses
		self.leaves=[]
		self.leaves_dictionary = {}
		self.root = self.__buildTree(addresses)

	

	def __buildTree(self, addresses: List[str]) -> None:

		#Build the Merkle Tree recursively.
		# Create leaf nodes for each value in the input list
		#leaves: List[Node] = [Node(None, None, Node.hash(e), e) for e in values]
		contents = []
		for filename in addresses:
			with open(filename, 'r') as f:
				file_data = f.read()
			f.close()
			contents.append(file_data)
	
		leaves: List[Node] = []
		for content in contents:
			node = Node(None, None, Node.hash(content), content)
			self.leaves_dictionary[node.value] = node
			leaves.append(node)

		# If the number of leaves is odd, duplicate the last leaf
		if len(leaves) % 2 == 1:
			leaves.append(leaves[-1].copy()) # duplicate last elem if odd number of elements

		self.leaves = leaves

		# Build the tree recursively
		
		return self.__buildTreeRec(leaves)
	
	def __buildTreeforVerify(self, addresses: List[str]) -> None:

		#Build the Merkle Tree recursively.
		# Create leaf nodes for each value in the input list
		#leaves: List[Node] = [Node(None, None, Node.hash(e), e) for e in values]
		contents = []
		for filename in addresses:
			with open(filename, 'r') as f:
				file_data = f.read()
			f.close()
			contents.append(file_data)
	
		leaves: List[Node] = []
		for content in contents:
			node = Node(None, None, Node.hash(content), content)
			# self.leaves_dictionary[node.value] = node
			leaves.append(node)

		# If the number of leaves is odd, duplicate the last leaf
		if len(leaves) % 2 == 1:
			leaves.append(leaves[-1].copy()) # duplicate last elem if odd number of elements
			leaves[-1].is_copied = True
		# self.leaves = leaves

		# Build the tree recursively
		
		return self.__buildTreeRec(leaves)

	def __buildTreeRec(self, nodes: List[Node]) -> Node: #Contains The list of nodes to be included in the Merkle Tree.
		if len(nodes) % 2 == 1:  # If the number of nodes is odd, duplicate the last node
			nodes.append(nodes[-1].copy()) # duplicate last elem if odd number of elements
			nodes[-1].is_copied = True

		# Calculate the index of the middle node
		half: int = len(nodes) // 2  

		# If there are only two nodes, create a parent node for them
		if len(nodes) == 2:
			Hash_Value = Node.hash(nodes[0].value + nodes[1].value)
			Combined_Content = nodes[0].content+"+"+nodes[1].content
			parent = Node(nodes[0], nodes[1], Hash_Value, Combined_Content)

			nodes[0].is_left = 1
			nodes[0].parent = parent

			nodes[1].is_left = 0
			nodes[1].parent = parent

			return parent
		
		# Recursively build the left and right subtrees
		left: Node = self.__buildTreeRec(nodes[:half])
		right: Node = self.__buildTreeRec(nodes[half:])
		left.is_left = 1
		right.is_left = 0

		value: str = Node.hash(left.value + right.value)  #Calculates Hash
		content: str = f'{left.content}+{right.content}'
		
		parent = Node(left, right, value, content) 
		left.parent = parent
		right.parent = parent #Storing Content for testing purposes
		return parent #Returns The root node of the Merkle Tree.

	def verify_tree(self):
		hashed_value = self.__buildTreeforVerify(self.addresses).value
		print(hashed_value, self.root.value)
		if(hashed_value == self.root.value):
			return True
		else:
			return False

	def printTree(self) -> None:
		self.__printTreeRec(self.root) #Calling Helper function
		
	def __printTreeRec(self, node: Node) -> None:
		# Check if the node is not None
		if node != None:
			# If the node is not a leaf node, print the left and right child nodes
			if node.left != None:
				print("Left: "+str(node.left))
				print("Right: "+str(node.right))
			else:
				# If the node is a leaf node, print that it is an input
				print("Input")

			# If the node is a copy, print that it is padding
			if node.is_copied:
				print('(Padding)')
			# Print the value and content of the node
			print("Value: "+str(node.value))
			print("Content: "+str(node.content))
			print("")
			# Recursively call the method on the left and right child nodes
			self.__printTreeRec(node.left)
			self.__printTreeRec(node.right)

	def merkle_proof(self, node:Node):
		path = []
		hashed_value = Node.hash(node.content)

		while(node.parent != None):
			path.append(node.content)
			if(node.is_left):
				hashed_value = Node.hash(hashed_value + node.parent.right.value)
			else:
				hashed_value = Node.hash(node.parent.left.value + hashed_value)

			node = node.parent
		path.append(node.content)

		if(self.root.value != hashed_value):
			return False
		return path
	
	def verify_inclusion(self, address):   #this function currently takes in self.content but that's probably a bad idea when working with files
		try:							#changed it to address
			with open(address, 'r') as f:
				file_data = f.read()
			f.close()
		except:
			return False
			
		content = file_data

		hashed_value = Node.hash(content)
		
		if(hashed_value in self.leaves_dictionary.keys()):
			node = self.leaves_dictionary[hashed_value]
			return self.merkle_proof(node)
		return False


	def addnode(self, element : str): 
		node_list = []
		node, check = self.checkLeafsIsCopied()
		if check == False:
			#no copy nodes exist, a subtree of the same height as the Merkle Tree needs to be created 
			node_list.append(Node(None, None, Node.hash(element), element, False))
			for i in range(len(self.leaves)-1):
				node_list.append(Node(None, None, Node.hash(element), element, True))
			root = self.__buildTreeRec(node_list)
			self.root = self.__buildTreeRec([self.root, root])
		else:
			#copy leaf nodes exist and can be replaced
			#change the copied leafs value
			node.content = element
			node.value = Node.hash(element)
			while node.parent != None: #Loop until you reach the root 
				#here we are changing the parents value
				node = node.parent
				node.value: str = Node.hash(node.left.value + node.right.value)  #Calculates Hash
				node.content: str = f'{node.left.content}+{node.right.content}'
			#here we finally change the root values
			node.value: str = Node.hash(node.left.value + node.right.value)  #Calculates Hash
			node.content: str = f'{node.left.content}+{node.right.content}'	
			self.root = node

	def checkLeafsIsCopied(self):
		for thisLeaf in self.leaves:
			if thisLeaf.is_copied == True:
				return thisLeaf, True
		return thisLeaf, False

	def getRootHash(self) -> str:
	    return self.root.value  #Returns The SHA-256 hash of the root node of the Merkle Tree.

	
	
def mixmerkletree() -> None:
	""" The mixmerkletree() function takes a list of transactions and generates a Merkle tree by 
	recursively combining pairs of hashes until only one root hash remains. It then adds a 
	"mixing" hash to the root hash to make it unique and returns the final root hash. This 
	process helps to ensure the privacy of the transactions by making it difficult to trace the 
	original transaction from the final output. """

	# Define a list of input values
	elems = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
	#As there are odd number of inputs, the last input is repeated
	print("Inputs: ")
	print(*elems, sep=" | ") # Print the input values separated by "|"
	print("")
	mtree = MerkleTree(elems) # Create a Merkle Tree from the input values
	print("Root Hash: "+mtree.getRootHash()+"\n") # Print the root hash of the Merkle Tree
	#print(mtree.root.content)
	#mtree.printTree() # Print the entire Merkle 
	#print(mtree.leaves[9].c)
	mtree.leaves[9].content = 'j'
	print(mtree.merkle_proof(mtree.leaves[9]))
	print(mtree.verify_inclusion('g'))
	
#mixmerkletree()

