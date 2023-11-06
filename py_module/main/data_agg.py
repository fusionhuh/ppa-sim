class DataAggregator:
    def __init__(self):
        self.private_fields = []

    def is_field_private(self, name: str) -> bool:
        return name in self.private_fields

    def add_field(self, name: str, val: any, private=False):
        if self.field_exists(name):
            raise Exception(f"Adding field '{name}' to aggregator when it already exists.")
        setattr(self, name, val)
        if private:
            self.private_fields.append(name)

    def field_exists(self, name: str) -> bool:
        return hasattr(self, name)
    
    def set_field(self, name: str, val: any):
        if not self.field_exists(name):
            raise Exception(f"Trying to modify field '{name}' when it doesn't exist.")
        if self.is_field_private(name):
            raise Exception(f"Trying to modify reserved field '{name}'")
        setattr(self, name, val)

    def get_field(self, name: str) -> any:
        if not self.field_exists(name):
            raise Exception(f"Trying to get field '{name}', which doesn't exist")
        return getattr(self, name)
    
    