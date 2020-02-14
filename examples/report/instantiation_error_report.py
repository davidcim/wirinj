from examples.report.cat_example_classes import Nail, Cat
from wirinj import Injector, Definitions, Autowiring, Instance


class BrokenNail(Nail):

    def __init__(self):
        raise AttributeError('Broken leg')


inj = Injector(
    Definitions({
        Nail: Instance(BrokenNail)
    }),
    Autowiring(use_singletons=False),
)

inj.get(Cat)
