from examples.report.cat_example_classes import Cat, Head
from wirinj import Injector, Definitions, Instance

inj = Injector(Definitions({
    Cat: Instance(),
    Head: Instance(),
}))
cat2 = inj.get(Cat)
