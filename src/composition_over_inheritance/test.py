from abc import ABC, abstractmethod
from typing import Callable


class Animal(ABC):
    @abstractmethod
    def make_sound(self):
        ...


class Dog(Animal):
    def make_sound(self):
        print("Woof")


class Cat(Animal):
    def make_sound(self):
        print("Meow")


dog: Animal = Dog()
dog.make_sound()
cat: Animal = Cat()
cat.make_sound()


class Animal2:
    def make_sound(self, sound: str):
        print(sound)


class Dog2:
    def __init__(self, animal: Animal2):
        self.animal = animal

    def bark(self):
        self.animal.make_sound("Woof")


class Cat2:
    def __init__(self, animal: Animal2):
        self.animal = animal

    def bark(self):
        self.animal.make_sound("Meow")


dog2: Dog2 = Dog2(Animal2())
dog2.bark()
cat2: Cat2 = Cat2(Animal2())
cat2.bark()


def abcd(animal: Dog2 | Cat2):
    pass

def abcd(animal: Animal):
    pass

class Animal3:
    def __init__(self, make_sound: Callable[[], None], run: Callable[[], None]):
        self.run = run
        self.make_sound = make_sound

    def make_sound(self):
        self.make_sound()

dog3: Animal3 = Animal3(lambda: print("Woof"))
cat3: Animal3 = Animal3(lambda: print("Meow"))
alien3: Animal3 = Animal3(lambda: print("WOOOOOO"))


dog3.make_sound()
cat3.make_sound()

def abcd3(animal: Animal3):
    pass

abcd3(dog3)
abcd3(cat3)

