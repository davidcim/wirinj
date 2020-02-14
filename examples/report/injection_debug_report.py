import logging

from examples.report.cat_example_classes import Cat
from wirinj import Injector, Autowiring, Definitions, Instance

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
inj = Injector(Autowiring(use_singletons=False))
cat = inj.get(Cat)
