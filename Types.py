from unittest import TestCase, main

import Matcher

types = ["Grass", "Fire", "Water", "Bug", "Poison", "Normal", "Flying", "Electric", "Ground",
         "Fighting", "Psychic", "Rock", "Ice", "Ghost", "Dragon", "Steel", "Dark", "Fairy"]
gen_types = {1: 15, 2: 17, 6: 18}


class Type:
    def __init__(self, name, generation=6):
        self.gen = generation
        if self.gen%1!=0 or self.gen < 1:
            raise NotImplementedError(f"Generation '{generation}' not recognized.")
        while self.gen not in [1, 2, 6] and self.gen > 0:
            self.gen = self.gen - 1

        self.type = name
        if self.type not in types:
            raise NotImplementedError(f"Type '{self.type}' not recognized")

        self.weaknesses = []
        self.resistances = []
        self.immunities = []
        self.def_neutral = types[:gen_types[self.gen]]
        self.def_table = {}
        self.def_score = 0

        self.advantages = []
        self.disadvantages = []
        self.unsusceptibles = []
        self.off_neutral = types[:gen_types[self.gen]]
        self.off_table = {}
        self.off_score = 0

        """Making some exceptions for Steel, Dark and Fairy"""
        if self.type not in types[:gen_types[self.gen]]:
            self.def_neutral = types[:gen_types[self.gen]]
            self.def_table = {element: 1 for element in types[:gen_types[self.gen]]}
            self.unsusceptibles = types[:gen_types[self.gen]]
            self.off_neutral = []
            self.off_table = {element: 0 for element in types[:gen_types[self.gen]]}
            return


        """Defensive properties."""
        self.resistances, self.weaknesses, self.immunities = Matcher.def_matchups[self.gen].loc[self.type]

        self.def_neutral = list(set(self.def_neutral) - set(self.weaknesses)
                            - set(self.resistances) - set(self.immunities))

        self.def_table = {weak: 2 for weak in self.weaknesses}
        self.def_table.update({resist: 0.5 for resist in self.resistances})
        self.def_table.update({immu: 0 for immu in self.immunities})
        self.def_table.update({neutral: 1 for neutral in self.def_neutral})

        self.def_score = sum([self.def_table[k] for k in types[:gen_types[self.gen]]])
        if self.def_score%1 == 0:
            self.def_score = int(self.def_score)


        """Offensive properties."""
        self.advantages, self.disadvantages, self.unsusceptibles = Matcher.off_matchups[self.gen].loc[self.type]

        self.off_neutral = list(set(self.off_neutral) - set(self.advantages) 
                                - set(self.disadvantages) - set(self.unsusceptibles))

        self.off_table = {adv: 2 for adv in self.advantages}
        self.off_table.update({dis: 0.5 for dis in self.disadvantages})
        self.off_table.update({unsus: 0  for unsus in self.unsusceptibles})
        self.off_table.update({neutral: 1 for neutral in self.off_neutral})

        self.off_score = sum([self.off_table[k] for k in types[:gen_types[self.gen]]])
        if self.off_score%1 == 0:
            self.off_score = int(self.off_score)

    def __str__(self):
        res =  f"Type: {self.type}\nWeaknesses: " + ", ".join(self.weaknesses)
        if self.resistances == []: 
            "\nNo Resistances"
        else:
            res += "\nResistances: " + ", ".join(self.resistances)
        if self.immunities != []:
            res += "\nImmunities: " + ", ".join(self.immunities)
        return res

    def __repr__(self):
        return str(self.type)

    def __eq__(self, other):
        if isinstance(other, Type):
            return  str(self) == str(other)
        return False

    def __hash__(self):
        return len(self.immunities)+len(self.weaknesses)*10+len(self.resistances)*100

    def direct(self, other):
        if self.def_table[other.type] < other.def_table[self.type]:
            return self.type, f"{self.type} won against {other.type}."
        if self.def_table[other.type] > other.def_table[self.type]:
            return other.type, f"{self.type} lost against {other.type}."
        if self.def_table[other.type] == other.def_table[self.type]:
            return self.indirect(other)

    def indirect(self, other):
        if self.def_score < other.def_score:
            return self.type, f"{self.type} won against {other.type} with {self.def_score} to {other.def_score}."
        if self.def_score > other.def_score:
            return other.type, f"{self.type} lost against {other.type} with {self.def_score} to {other.def_score}."
        if self.def_score == other.def_score:
            return None, f"Tie between {self.type} and {other.type} with {self.def_score} each."


class TypeTest(TestCase):
    """1.  Implementation Test Cases"""
    def test_Gen0_NotImplemented(self):
        with self.assertRaises(NotImplementedError):
            Type("Fairy", 0)

    def test_Gen4_5_NotImplemented(self):
        with self.assertRaises(NotImplementedError):
            Type("Rock", 4.5)

    def test_Gen4_is_Gen2(self):
        expected = 2
        actual = Type("Dark", 4).gen
        self.assertEqual(actual, expected)

    def test_Gen8_is_Gen6(self):
        expected = 6
        actual = Type("Fairy", 8).gen
        self.assertEqual(actual, expected)

    def test_NotImplemented(self):
        with self.assertRaises(NotImplementedError):
            Type("Sound")

    def test_Poison_eq_str(self):
        expected = False
        actual = Type("Poison") == "Poison"
        self.assertEqual(actual, expected)

    def test_Dragon_eq_Dragon(self):
        expected = True
        actual = Type("Dragon") == Type("Dragon")
        self.assertEqual(actual, expected)

    def test_Grass_eq_Bug(self):
        expected = False
        actual = Type("Grass") == Type("Bug")
        self.assertEqual(actual, expected)

    def test_Steel_def_neutral_gen1(self):
        expected = types[:gen_types[1]]
        actual = Type("Steel", 1).def_neutral
        self.assertEqual(actual, expected)

    def test_Fairy_def_neutral_gen2(self):
        expected = types[:gen_types[2]]
        actual = Type("Fairy", 2).def_neutral
        self.assertEqual(actual, expected)


    """2.  Generation Insensitive Test Cases"""
    def test_Normal_super_effective(self):
        expected = []
        actual = Type("Normal").advantages
        self.assertEqual(actual, expected)

    def test_Normal_weaknesses(self):
        expected = ["Fighting"]
        actual = Type("Normal").weaknesses
        self.assertEqual(actual, expected)

    def test_Ground_direct_Electric(self):
        expected = "Ground won against Electric."
        actual = Type("Ground").direct(Type("Electric"))[1]
        self.assertEqual(actual, expected)

    def test_Ghost_resistances(self):
        expected = ["Bug", "Poison"]
        actual = Type("Ghost").resistances
        self.assertEqual(actual, expected)

    def test_Flying_def_score(self):
        expected = 18.5
        actual = Type("Flying").def_score
        self.assertEqual(actual, expected)


    """3   Intra Generational Type Interaction Test Cases"""
    """3.1 Generation 1 Test Cases"""
    def test_Dragen_offensive_neutralities_gen1(self):
        """Dragon Rage was the only dragon type attack and it dealt always 40HP."""
        expected = sorted(types[:gen_types[1]])
        actual = sorted(Type("Dragon", 1).off_neutral)
        self.assertEqual(actual, expected)

    def test_Psychic_immunities_gen1(self):
        expected = ["Ghost"]
        actual = Type("Psychic", 1).immunities
        self.assertEqual(actual, expected)

    def test_Poison_advantages_gne1(self):
        expected = ["Bug", "Grass"]
        actual = Type("Poison", 1).advantages
        self.assertEqual(actual, expected)

    def test_Bug_advantages_gen1(self):
        expected = ["Grass", "Poison", "Psychic"]
        actual = Type("Bug", 1).advantages
        self.assertEqual(actual, expected)

    def test_Fire_resistances_gne1(self):
        expected = ["Bug", "Fire", "Grass"]
        actual = Type("Fire", 1).resistances
        self.assertEqual(actual, expected)

    def test_Water_resistances_gne1(self):
        expected = ["Fire", "Ice", "Water"]
        actual = Type("Water", 1).resistances
        self.assertEqual(actual, expected)

    def test_Fighting_advantages_gen1(self):
        expected = ["Ice", "Normal", "Rock"]
        actual = Type("Fighting", 1).advantages
        self.assertEqual(actual, expected)

    """3.2 Generation 2 Test Cases"""
    def test_Psychic_imunities_gen2(self):
        expected = []
        actual = Type("Psychic", 2).immunities
        self.assertEqual(actual, expected)

    def test_Steel_advantages_gen2(self):
        expected = ["Ice", "Rock"]
        actual = Type("Steel", 2).advantages
        self.assertEqual(actual, expected)

    def test_Fire_resistances_gen2(self):
        expected = ["Bug", "Fire", "Grass", "Ice", "Steel"]
        actual = Type("Fire", 2).resistances
        self.assertEqual(actual, expected)

    """3.3 Generation 6 Test Cases"""
    def test_Fire_resistances_gen6(self):
        expected = ["Bug", "Fire", "Fairy", "Grass", "Ice", "Steel"]
        actual = Type("Fire").resistances
        self.assertEqual(actual, expected)

    def test_Fairy_immunities_gen6(self):
        expected = ["Dragon"]
        actual = Type("Fairy").immunities
        self.assertEqual(actual, expected)

    def test_Steel_indirect_Grass_gen6(self):
        expected = "Steel won against Grass with 15 to 21."
        actual = Type("Steel").indirect(Type("Grass"))[1]
        self.assertEqual(actual, expected)

    def test_Dark_off_score_gen6(self):
        expected = 18.5
        actual = Type("Dark").off_score
        self.assertEqual(actual, expected)

    def test_Poison_resistances_gen6(self):
        expected = ["Bug", "Fairy", "Fighting", "Grass", "Poison"]
        actual = Type("Poison").resistances
        self.assertEqual(actual, expected)

    def test_Ground_direct_Fighting_gen6(self):
        expected = Type("Ground").indirect(Type("Fighting"))
        actual = Type("Ground").direct(Type("Fighting"))
        self.assertEqual(actual, expected)


    """4   Inter Generational Type Interaction Test Cases"""
    def test_Electric_eq_gen1_gen2(self):
        expected = False
        actual = Type("Electric", 1) == Type("Electric", 2)
        self.assertEqual(actual, expected)

    def test_Normal_eq_gen1_gen6(self):
        expected = True
        actual = Type("Normal", 1) == Type("Normal", 6)
        self.assertEqual(actual, expected)

    def test_Steel_eq_gen2_gen6(self):
        expected = False
        actual = Type("Steel", 2) == Type("Steel", 6)
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    main()