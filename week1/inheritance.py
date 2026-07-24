class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def speak(self, sound):
        print(f"{self.name} says {sound}")

class BullDog(Dog):
    def speak(self, sound = "BARK"):
        super().speak(sound)

tommy = Dog("Tommy", 6)
tommy.speak("Woof")

sheru = BullDog("Sheru", 8)
sheru.speak()