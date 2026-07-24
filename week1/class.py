# example.py
class Dog:
    family = "Canine"               # Class attribute

    def __init__(self, name, age):
        self.name = name            # Instance attribute
        self.age = age

    def __str__(self):              # toString method
        return f"{self.name} is {self.age} years old."
    
    def sound(self, sound):         # Instance method
        self.sound = sound
        print(f"{self.name} says {self.sound}")

#tommy = Dog()
sheru = Dog("Sheru", 9)
sheru.sound("Woof!")                        # Sheru says Woof!
print(sheru)                                # Sheru is 9 years old.
print(f"Sheru family:: {sheru.family}")     # Canine

tomy = Dog("Tomy", 5)
print(tomy)
print(f"sheru==tomy :: {sheru==tomy}")      # False

sheru.family = "Doggy"                      # Changing class attribute for ONLY sheru instance
print(f"Sheru family:: {sheru.family}")     # Doggy
print(f"Tomy family:: {tomy.family}")       # Canine

Dog.family = "Doggy"                        # Changing class attribute for all Dogs
print(f"Sheru family:: {sheru.family}")     # Doggy
print(f"Tomy family:: {tomy.family}")       # Canine
