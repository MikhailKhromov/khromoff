import json
import time
from hashlib import sha256

from django.db import models


class Transaction(models.Model):
    block = models.ForeignKey('Block', on_delete=models.CASCADE)  # the chain the block is in
    text = models.TextField()


class Block(models.Model):
    """
    Constructor for the `Block` class.
    :var index: Unique ID of the block.
    :var transactions: List of transactions.
    :var timestamp: Time of generation of the block.
    """
    index = models.CharField()
    # transactions = models.CharField()
    timestamp = models.TimeField()
    previous_hash = models.CharField()  # Adding the previous hash field

    chain = models.ForeignKey('Blockchain', on_delete=models.CASCADE, primary_key=True)  # the chain the block is in

    def compute_hash(self):
        """
         Returns the hash of the block instance by first converting it
         into JSON string.
         """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain(models.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(index=0, chain=self, timestamp=time.time(), previous_hash="0")
        genesis_block.hash = genesis_block.compute_hash()
        genesis_block.save()

    @property
    def last_block(self):
        """
        A quick pythonic way to retrieve the most recent block in the chain. Note that
        the chain will always consist of at least one block (i.e., genesis block)
        """
        return Queryu
