from wirinj import Injector, Definitions, Instance, Singleton, Factory


class Cat:
    pass


class Dog:
    pass

# Wiring definitions
defs = {
    'sound': 'Meow',
    Cat: Instance(),
    Dog: Singleton(),
    'cat_factory': Factory(Cat),
}

inj = Injector(Definitions(defs))

print(inj.get('sound'))

cat1 = inj.get(Cat)
print('cat1:', cat1)

cat2 = inj.get(Cat)
print('cat2:', cat2)

print('cat1 is cat2:', cat1 is cat2)

dog = inj.get(Dog)
print('dog:', dog)

dog2 = inj.get(Dog)
print('dog2:', dog2)

print('dog is dog2:', dog is dog2)

cat_factory = inj.get('cat_factory')
cat3 = cat_factory()
print('cat3:', cat3)
