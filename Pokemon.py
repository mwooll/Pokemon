from unittest import TestCase, main

from Types import Type
from Attacks import Attack

types = ["Grass", "Fire", "Water", "Bug", "Poison", "Normal", "Flying", "Electric", "Ground",
         "Fighting", "Psychic", "Rock", "Ice", "Ghost", "Dragon", "Steel", "Dark", "Fairy"]
gen_types = {1: 15, 2: 17, 6: 18}

class Pokemon:
    def __init__(self, species, typing, generation=6):
        self.gen = generation
        if self.gen%1!=0 or self.gen < 1:
            raise NotImplementedError(f"Generation {generation} not recognized.")
        while self.gen not in [1, 2, 6] and self.gen > 0:
            self.gen = self.gen - 1

        typing = list(set(typing))
        if None in typing:
            typing.remove(None)
        if "None" in typing:
            typing.remove("None")
        self.typing = [Type(typing[k], self.gen) for k in range(len(typing))]
        self.typing_str = typing

        self.species = species
        self.moves = []

        self.get_def_matchups()
        self.get_off_matchups()

    def get_def_matchups(self, generation=None):
        if generation == None:
            generation = self.gen
        self.weaknesses = []
        self.resistances = []
        self.immunities = []
        self.def_neutral = types[:gen_types[generation]]
        self.def_table = {}
        self.def_score = 0
        self.d_weak = []
        self.d_rest = []

        for element in types[:gen_types[generation]]:
            self.def_table[element] = 1

        for i in range(len(self.typing)):
            self.weaknesses.extend(self.typing[i].weaknesses)
            self.resistances.extend(self.typing[i].resistances)
            self.immunities.extend(self.typing[i].immunities)

            for element in types[:gen_types[generation]]:
                self.def_table[element] *= self.typing[i].def_table[element]

        # self.def_inv_table = {4: [], 2: [], 1: [], 0.5: [], 0.25: [], 0: []}
        self.def_inv_table = {2**k: [] for k in range(5, -8, -1)}
        self.def_inv_table[0] = []
        for key in types[:gen_types[self.gen]]:
            self.def_inv_table[self.def_table[key]].append(key)

        self.d_weak = self.def_inv_table[4]
        self.weaknesses = self.def_inv_table[2]
        self.def_neutral = self.def_inv_table[1]
        self.resistances = self.def_inv_table[0.5]
        self.d_rest = self.def_inv_table[0.25]
        self.immunities = self.def_inv_table[0] 

        for key in types[:gen_types[generation]]:
            self.def_score += self.def_table[key]-1
        self.def_attr = 0

    def get_off_matchups(self, STAB=True):
        self.advantages = []
        self.disadvantages = []
        self.unsusceptibles = []
        self.off_neutral = types[:gen_types[self.gen]]
        self.off_table = {}
        self.off_score = 0

        for element in types[:gen_types[self.gen]]:
            self.off_table[element] = 0
            for attack in self.moves:
                fac = 1
                if attack.type in self.typing_str and STAB:
                    fac = 1.5
                self.off_table[element] = max(self.off_table[element], fac*attack.off_table[element])

        self.off_inv_table = {3: [], 2: [], 1.5: [], 1: [], 0.75: [], 0.5: [], 0: []}
        for key in types[:gen_types[self.gen]]:
            self.off_inv_table[self.off_table[key]].append(key)

        self.advantages = self.off_inv_table[2] + self.off_inv_table[3]
        self.off_neutral = self.off_inv_table[1] + self.off_inv_table[1.5]
        self.disadvantages = self.off_inv_table[0.5] + self.off_inv_table[0.75]
        self.unsusceptibles = self.off_inv_table[0] 

        for key in types[:gen_types[self.gen]]:
            self.off_score += self.off_table[key]
        return self.off_score

    def set_move(self, moves):
        for move in moves:
            if len(self.moves) < 4:
                self.moves.append(move)
                self.get_off_matchups()

    def set_moves_by_type(self, typings, STAB=True, generation=None):
        self.reset_moves()
        if generation == None:
            generation = self.gen

        for typing in typings:
            move = Attack(f"generic {typing} move", typing, generation)
            self.moves.append(move)
        return self.get_off_matchups(STAB)

    def reset_moves(self):
        self.moves = []

    def get_moveset(self):
        return self.moves

    def get_off_coverage(self, moves=2, given=[], STAB=True):
        """This function aims to maximize self.off_score."""
        self.coverage_dict = {1: {}, 2: {}, 3: {}, 4: {}}
        self.inv_coverage_dict = {1: {}, 2: {}, 3: {}, 4: {}}
        self.max_coverage = {}
        baseline = given
        set_moves = len(given)
        if baseline:
            self.max_coverage[0] = (baseline, self.set_moves_by_type(baseline, STAB))
            self.reset_moves()

        if moves - set_moves <= 2:
            for element in types[:gen_types[self.gen]]:
                typing = baseline + [element]
                value = self.set_moves_by_type(typing, STAB)
                self.coverage_dict[1][element] = value
                if value in self.inv_coverage_dict[1].keys():
                    self.inv_coverage_dict[1][value].append(element)
                else:
                    self.inv_coverage_dict[1][value] = [element]
                # self.reset_moves()
            max_key = max(self.inv_coverage_dict[1].keys())
            self.max_coverage[1] = (self.inv_coverage_dict[1][max_key], max_key)

        if moves - set_moves == 2:
            for element in types[:gen_types[self.gen]]:
                for power in types[:gen_types[self.gen]]:
                    if element == power:
                        continue
                    adding = sorted([element, power])
                    added = tuple(adding)
                    if added in self.coverage_dict[2].keys():
                        continue

                    typing = baseline + adding
                    value = self.set_moves_by_type(typing, STAB)
                    self.coverage_dict[2][added] = value
                    if value in self.inv_coverage_dict[2].keys():
                        self.inv_coverage_dict[2][value].append(added)
                    else:
                        self.inv_coverage_dict[2][value] = [added]
                    self.reset_moves()
            max_key = max(self.inv_coverage_dict[2].keys())
            self.max_coverage[2] = (self.inv_coverage_dict[2][max_key], max_key)

        if moves - set_moves == 3:
            for element in types[:gen_types[self.gen]]:
                for power in types[:gen_types[self.gen]]:
                    for force in types[:gen_types[self.gen]]:

                        adding = sorted(list(set([element, power, force])))
                        added = tuple(adding)
                        key = 3
                        if element == power or element == force or power == force:
                            key = 2
                        if element == power and power == force:
                            key = 1
                            adding = [force]
                            added = force
                        if added in self.coverage_dict[key].keys():
                            continue

                        typing = baseline + adding
                        value = self.set_moves_by_type(typing, STAB)
                        self.coverage_dict[key][added] = value
                        if value in self.inv_coverage_dict[key].keys():
                            self.inv_coverage_dict[key][value].append(added)
                        else:
                            self.inv_coverage_dict[key][value] = [added]
                        self.reset_moves()

            for key in [1, 2, 3]:
                max_key = max(self.inv_coverage_dict[key].keys())
                self.max_coverage[key] = (self.inv_coverage_dict[key][max_key], max_key)

        if moves - set_moves == 4:
            for element in types[:gen_types[self.gen]]:
                for power in types[:gen_types[self.gen]]:
                    for force in types[:gen_types[self.gen]]:
                        for spell in types[:gen_types[self.gen]]:

                            adding = sorted(list(set([element, power, force, spell])))
                            added = tuple(adding)
                            key = len(adding)
                            if key == 1:
                                adding = [force]
                                added = force
                            if added in self.coverage_dict[key].keys():
                                continue

                            typing = baseline + adding
                            value = self.set_moves_by_type(typing, STAB)
                            self.coverage_dict[key][added] = value
                            if value in self.inv_coverage_dict[key].keys():
                                self.inv_coverage_dict[key][value].append(added)
                            else:
                                self.inv_coverage_dict[key][value] = [added]
                            self.reset_moves()

            for key in [1, 2, 3, 4]:
                max_key = max(self.inv_coverage_dict[key].keys())
                self.max_coverage[key] = (self.inv_coverage_dict[key][max_key], max_key)

        self.set_moves_by_type(baseline, STAB)
        return self.max_coverage


    def set_def_attr(self, d_w, w, n, r, d_r, i):
        self.def_attr =  sum([d_w for d_weak in self.d_weak])
        self.def_attr += sum([w for weak in self.weaknesses])
        self.def_attr += sum([n for neu in self.def_neutral])
        self.def_attr -= sum([r for res in self.resistances])
        self.def_attr -= sum([d_r for d_rest in self.d_rest])
        self.def_attr -= sum([i for immu in self.immunities])
        return self.def_attr

    def __str__(self):
        return f"species = {self.species}, typing = {self.typing}"

    def __repr__(self):
        return str(self.species)

    def __eq__(self, other):
        if isinstance(other, Pokemon):
            return self.species == other.species
        return NotImplementedError(f"{other} is not a Pokemon.")

    def __hash__(self):
        return self.__repr__()

    def direct(self, other):
        selve = max([self.def_table[other.typing[k].type] for k in range(len(other.typing))])
        others = max([other.def_table[self.typing[k].type] for k in range(len(self.typing))])
        if selve < others:
            return self.type, f"{self.species} won against {other.species}."
        if selve > others:
            return other.type, f"{self.species} lost against {other.species}."
        if selve == others:
            return self.indirect(other)

    def indirect(self, other):
        if self.score < other.score:
            return self.species, f"{self.species} won against {other.species} with {self.score} to {other.score}."
        if self.score > other.score:
            return other.species, f"{self.species} lost against {other.species} with {self.score} to {other.score}."
        if self.score == other.score:
            return None, f"Tie between {self.species} and {other.species} with {self.score} each."

class PokéTest(TestCase):
    """Typing=[a, a] should be converted to Typing=[a], therefore should have no double weaknesses or double resistances"""
    def test_Rock_Rock_gen1_double_weaknesses(self):
        expected = []
        actual = Pokemon(None, ["Rock", "Rock"], 1).d_weak
        self.assertEqual(actual, expected)

    def test_Steel_Steel_gen2_double_weaknesses(self):
        expected = []
        actual = Pokemon(None, ["Steel", "Steel"], 5).d_weak
        self.assertEqual(actual, expected)

    def test_Fairy_Fairy_gen6_double_weaknesses(self):
        expected = []
        actual = Pokemon(None, ["Fairy", "Fairy"], 6).d_weak
        self.assertEqual(actual, expected)

    def test_Poison_Poison_gen1_double_resistances(self):
        expected = []
        actual = Pokemon(None, ["Poison", "Poison"], 1).d_rest
        self.assertEqual(actual, expected)

    def test_Dark_Dark_gen2_double_resistances(self):
        expected = []
        actual = Pokemon(None, ["Dark", "Dark"], 2).d_rest
        self.assertEqual(actual, expected)

    def test_Fire_Fire_gen6_double_resistances(self):
        expected = []
        actual = Pokemon(None, ["Fire", "Fire"], 6).d_rest
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    main()
    
    tyr = Pokemon("Tyranitar", ["Rock", "Dark"], 6)
    val = tyr.get_off_coverage(moves=4, given=["Rock"], STAB=True)
    print(val)
