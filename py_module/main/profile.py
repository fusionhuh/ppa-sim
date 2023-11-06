import statistics as stats


class Profile:
    def __init__(self, mode, cases, operands, context, adders, descriptions, areas):
        self.data = dict()
        self.mode = mode
        self.cases = cases
        self.operands = operands
        self.adders = adders
        self.descriptions = descriptions
        self.areas = areas
        self.context = context

        for adder in self.descriptions:
            self.data[adder] = dict()


    def _verify_data(self, adder: str, area: int):
        assert adder in self.descriptions
        if not area in self.data[adder].keys():
            self.data[adder][area] = dict()


    def add_delay_list(self, delay_list, adder: str, area: int):
        self._verify_data(adder, area)
        self.data[adder][area]["delays"] = delay_list
        self.data[adder][area]["mean"] = stats.mean(delay_list)
        self.data[adder][area]["stdev"] = stats.stdev(delay_list)
        self.data[adder][area]["worst"] = max(delay_list)
        self.data[adder][area]["best"] = min(delay_list)
        self.data[adder][area]["total"] = sum(delay_list)

    def add_worst_case_delay(self, delay, adder: str, area: int):
        self._verify_data(adder, area)
        self.data[adder][area]["sta_worst"] = delay

    def get_delays(self, adder: str, area):
        return self.data[adder][area]["delays"]
    
    def get_operands(self):
        return self.operands
    
    def get_adder_list(self):
        return self.adders
    
    def get_adder_str_list(self):
        return self.descriptions

    def get_area_list(self):
        return self.areas
    
    def get_context_at_index(self, index):
        return self.context[index]

