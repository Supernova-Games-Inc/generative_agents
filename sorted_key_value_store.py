from sortedcontainers import SortedDict

class SortedKeyValueStore:
    def __init__(self):
        self.store = {}  # Main dictionary to store key-value pairs
        self.sorted_keys = SortedDict()  # Sorted dictionary to maintain sorted keys
        self.value_to_key = {}  # Reverse dictionary for fast value-to-key lookups

    def insert(self, key, value):
        if value in self.value_to_key:
            raise ValueError("Value already exists in the store.")
        if key in self.store:
            old_value = self.store[key]
            del self.value_to_key[old_value]
        self.store[key] = value
        self.sorted_keys[key] = value
        self.value_to_key[value] = key

    def remove(self, key):
        if key in self.store:
            value = self.store[key]
            del self.store[key]
            del self.sorted_keys[key]
            del self.value_to_key[value]

    def get_value(self, key):
        return self.store.get(key)

    def get_key(self, value):
        return self.value_to_key.get(value)

    def get_sorted_keys(self):
        return list(self.sorted_keys.keys())

    def get_sorted_values(self):
        return [self.store[key] for key in self.sorted_keys]
