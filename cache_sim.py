def lg(n):
    sign = 1
    log = 0
    if n < 1:
        sign = -1
        n = 1/n
    while n > 1:
        n = n / 2
        log += sign
    return log


class CacheBlock:
    def __init__(self, tag, index, block_size):
        self.valid = 0
        self.tag = tag
        self.index = index
        self.block_size = block_size
        self.words = ['-'] * block_size

    def __str__(self):
        words = ''.join([padding(x, 16) for x in self.words])
        return f"{padding(self.index, 5)} :\t{self.valid}\t{self.tag}\t\t{words}"


def hex_to_bin(x):
    return bin(int(x, 16))[2:]


def padding(x, length, pad=' '):
    if len(x) >= length:
        return x
    return x + pad * (length - len(x))


class Cache:
    def __init__(self, block_size, cache_size, memory_address_size):
        self.block_size = block_size
        self.memory_address_size = memory_address_size

        self.index_size = lg(cache_size // (4 * block_size))
        self.offset = lg(block_size) + 2
        self.tag_size = memory_address_size - self.offset - self.index_size

        self.cache_block_array = [CacheBlock("0" * self.tag_size, addr, self.block_size) for addr in map(lambda x: bin(x)[2:].zfill(self.index_size), range(2 ** self.index_size))]
        print(self.tag_size, self.index_size, self.offset)

    def load_hex(self, hex_address):
        return self.load(hex_to_bin(hex_address).zfill(self.memory_address_size))

    def load(self, addr):
        hex_address = hex(int(addr, 2))
        print(addr)
        # index for access array
        c_index = int(addr[self.tag_size:][:self.index_size], 2)
        # index for word in block
        w_index = addr[self.tag_size + self.index_size:][:-2]
        w_index = 0 if len(w_index) == 0 else int(w_index, 2)

        tag = addr[:self.tag_size]
        block = self.cache_block_array[c_index]
        print("Address: ", addr)
        print("Tag: ", tag)
        print("Index: ", bin(c_index)[2:])
        if block.valid == 1 and block.tag == tag:
            print(f"{hex_address} result:\tHIT\n")
            return block.words[w_index]
        elif block.valid == 0:
            print(f"{hex_address} result:\tMISS by Valid\n")
            block.valid = 1
        elif block.tag != tag:
            print(f"{hex_address} result:\tMISS by Tag\n")
        block.tag = tag
        for i in range(self.block_size):
            block.words[i] = f"MEM[0x{hex((int(hex_address, 16) // (2 ** self.offset)) * (2 ** self.offset) + i * 4)[2:].upper().zfill(self.memory_address_size // 4)}]"
        return block.words[w_index]

    def __str__(self):
        words = ''.join([padding(f"WORD_{x}", 16) for x in range(self.block_size)])
        ret = f"{padding('INDEX', self.index_size)} :\tV\tTAG \t\t{words}\n"
        ret += '\n'.join(map(str, self.cache_block_array))
        return ret


cache = Cache(4, 4096, 16)
while True:
    q = input()
    print("Loaded", cache.load_hex(q))
    print(cache)