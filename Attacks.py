from unittest import TestCase, main
from Types import Type

types = ["Grass", "Fire", "Water", "Bug", "Poison", "Normal", "Flying", "Electric", "Ground",
         "Fighting", "Psychic", "Rock", "Ice", "Ghost", "Dragon", "Steel", "Dark", "Fairy"]
gen_types = {1: 15, 2: 17, 6: 18}

class Attack:
    def __init__(self, name, typing, gen=6, power=90, pp=10):
        self.name = name
        self.type = typing
        self.power = power
        self.pp = pp
        self.gen = gen        
        self.get_matchups()

    def get_matchups(self):
        matchups = Type(self.type, self.gen)
        self.advantages = matchups.advantages
        self.disadvantages = matchups.disadvantages
        self.unsusceptibles = matchups.unsusceptibles
        self.off_neutral = matchups.off_neutral

        self.off_table = matchups.off_table
        self.off_score = matchups.off_score

    def __str__(self):
        return f"{self.name}: type = {self.type}, power = {self.power}, pp = {self.pp}"

    def __repr__(self):
        return self.name

    def __hash__(self):
        return self.name

class AttackTest(TestCase):
    def test_str1(self):
        actual = str(Earthquake)
        expected = "Earthquake: type = Ground, power = 100, pp = 10"
        self.assertEqual(expected, actual)

    def test_str2(self):
        actual = str(Flamethrower)
        expected = "Flamethrower: type = Fire, power = 90, pp = 15"
        self.assertEqual(expected, actual)

    def test_repr(self):
        actual = str([Flamethrower, Earthquake])
        expected = "[Flamethrower, Earthquake]"
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    Flamethrower = Attack("Flamethrower", "Fire", 6, 90, 15)
    Earthquake = Attack("Earthquake", "Ground", 6, 100, 10)

    # print(Flamethrower.off_table)
    main()