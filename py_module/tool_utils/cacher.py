from hlsynthesizer._file import *
import json



class Cacher(object):

    def __init__(self):
        self.path_to_func: dict = dict()
        self.path_to_type: dict = dict()
        self.path_to_args: dict = dict()

    def _data_exists(path: str) -> bool:
        if not file_exists(path): return False

        if read_text(path) == "" or read_text(path) == "\n": return False

        return True

    def register_data(self, path: str, miss_func, type: str = "text", args: list = []) -> any:
        assert type == "text" or type == "json"
        self.path_to_func[path] = miss_func
        self.path_to_type[path] = type
        self.path_to_args[path] = args

    def load_data(self, path: str):
        if path not in self.path_to_type:
            raise Exception("Trying to load resource that hasn't been registered yet")
        if not self._data_exists(path):
            # call miss func
            if not self._data_exists(path):
                raise Exception("Resource still doesn't exist after calling miss function")
            
        data = read_text(path)
        type = self.path_to_type[path]

        return data if type == "text" else json.loads(data)





