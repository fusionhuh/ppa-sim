from py_module.adder import Adder

def _get_minimum_scale_factors(adders: list) -> list:
    max_area = max([adder.get_min_area() for adder in adders])
    scale_factors = [max_area/adder.get_min_area() for adder in adders]
    return scale_factors

def _get_adder_label(a: Adder, area=1) -> str:
    return a.get_verbose_name() + f", area = {int(area*a.get_min_area()+1)}"
