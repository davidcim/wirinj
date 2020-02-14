from wirinj import Injector, Autowiring


class Cat:
    pass


inj = Injector(Autowiring())

cat = inj.get(Cat)
print(cat)
