import numpy as np
from bokeh.models import ColumnDataSource, Div, Select, Button, CheckboxGroup
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row

from Pokemon import Pokemon
from Types import Type

types = ["Grass", "Fire", "Water", "Bug", "Poison", "Normal", "Flying", "Electric", "Ground",
         "Fighting", "Psychic", "Rock", "Ice", "Ghost", "Dragon", "Steel", "Dark", "Fairy"]
rev_types = types[::-1]
gen_types = {1: 15, 2: 17, 6: 18}


"""defensive_plot shows how good/bad the chosen typing takes attacks"""
defensive_plot = figure(title="Defensive Line-Up", plot_height=375, plot_width=350,
                         x_range=[-0.25, 4.25], y_range=rev_types, toolbar_location=None, tools="")


"""matchups_plot gives an indication of how good/bad a given matchup is"""
matchups = ["Hard", "Unfavoured", "Even", "Favoured", "Easy"]
matchups_plot = figure(title="Matchups Table", plot_height=412, plot_width=250,
                       x_range=matchups, y_range=rev_types, toolbar_location=None, tools="")
matchups_plot.xaxis.major_label_orientation = np.pi/4

"""offensive_plot shows how good/bad the chosen coverage deals damage"""
offensive_plot = figure(title="Offensive Line-Up", plot_height=375, plot_width=250,
                         x_range=[-0.25, 3.25], y_range=rev_types, toolbar_location=None, tools="")


def transform():
    """Updates the ColumnDataSource and the plots according to the values of the various selects."""
    for circle in utility["circles"]:
        circle.visible = False

    defensive_line_up, offensive_line_up, dot_size = get_line_up()

    matchups_line_up, colour = get_matchup_table(defensive_line_up, offensive_line_up)

    source = ColumnDataSource(dict(Types = types, 
                               Defensive = defensive_line_up,
                               Matchup   = matchups_line_up,
                               Offensive = offensive_line_up,
                               colours   = colour))

    def_circles = defensive_plot.circle(x="Defensive", y="Types", size=dot_size, source=source, color="purple")
    off_circles = offensive_plot.circle(x="Offensive", y="Types", size=10, source=source, color="purple")
    mat_circles = matchups_plot.circle(x="Matchup", y="Types", size=10, source=source, color="colours")
    utility["circles"] = [def_circles, mat_circles, off_circles]

    update_ticker(defensive_line_up, offensive_line_up)

    def_score_DIV.text = f"defensive score: {monster.def_score}"
    off_score_DIV.text = f"offensive score: {monster.off_score}"

def get_line_up():
    """Gets the defensive and offensive line_up and prepares it for the ColumnDataSource."""
    utility["monster"].get_def_matchups(utility["gen"])
    utility["monster"].set_moves_by_type(utility["attacks"], utility["STAB"], utility["gen"])

    defensive = [utility["monster"].def_table[element] for element in types[:gen_types[utility["gen"]]]] 
    defensive += [-1 for element in types[gen_types[utility["gen"]]:]]
    offensive = [utility["monster"].off_table[element] for element in types[:gen_types[utility["gen"]]]]
    offensive += [-1 for element in types[gen_types[utility["gen"]]:]]

    maximum = max(defensive)
    if maximum > 4:
        defensive_plot.x_range.end = maximum + 0.25
        dot_size = 32/maximum + 3
    if maximum <= 4:
        defensive_plot.x_range.end = 4.25
        dot_size = 10
    return defensive, offensive, dot_size

def get_matchup_table(defense, offense):
    """Returns everything that is needed for "matchups_plot"."""
    matchups = []
    colour   = []

    if utility["STAB"] == True:
        utility["monster"].set_moves_by_type(utility["attacks"], False, utility["gen"])
        offense = [utility["monster"].off_table[element] for element in types[:gen_types[utility["gen"]]]]
        offense += [-1 for element in types[gen_types[utility["gen"]]:]]

    for k in range(gen_types[utility["gen"]]):
        diff = offense[k] - defense[k]
        if diff <= -1:
            matchups.append("Hard")
            colour.append("crimson")
        elif diff < 0:
            matchups.append("Unfavoured")
            colour.append("red")
        elif diff == 0:
            matchups.append("Even")
            colour.append("blue")
        elif diff <= 1:
            matchups.append("Favoured")
            colour.append("green")
        else:
            matchups.append("Easy")
            colour.append("lime")

    for k in range(gen_types[utility["gen"]], 18):
        matchups.append("No Data")
        colour.append("black")
    return matchups, colour

def update_ticker(defense, offense):
    maximum = max(defense)
    if maximum <= 8:
        defensive_plot.xaxis.ticker = list(set([val for val in defense if (val-0.5)%1==0 or val%1==0]))
    else:
        defensive_plot.xaxis.ticker = list(set([val for val in defense if val%1==0]))
    offensive_plot.xaxis.ticker = list(set([val for val in offense if (val-0.5)%1==0 or val%1==0]))
    
def time_travel(attr, old, new):
    """Changes the generation to match the value of gen_select"""
    utility["monster"] = None
    if new == "1":
        utility["gen"] = 1
    if new == "2 - 5":
        utility["gen"] = 2
    if new == "6 - 9":
        utility["gen"] = 6

    utility["monster"] = Pokemon(None, utility["typing"], utility["gen"])
    transform()

def reflect_type(clicked):
    """Updates the typing according to the selected boxes from "typing_select"."""
    utility["typing"] = [types[index] for index in clicked]
    utility["monster"].typing = [Type(element, utility["gen"]) for element in utility["typing"]]
    utility["monster"].typing_str = utility["typing"]
    transform()

def multitype(clicked):
    """Updates the attacks according to the selected boxes from "attack_select"."""
    utility["monster"].reset_moves()
    utility["attacks"] = [types[index] for index in clicked]
    transform()

def stabify():
    """Updates utility["STAB"] according to the state of stab_button"""
    if utility["STAB"] == False:
        utility["STAB"] = True
        stab_button.label = "deactivate STAB"

    else:
        utility["STAB"] = False
        stab_button.label = "activate STAB"
    transform()



"""Adding a Select to change the generation"""
gen_select = Select(title="Select a generation", value="6 - 9", options=["1", "2 - 5", "6 - 9"], width=150)
gen_select.on_change("value", time_travel)

"""Adding a CheckboxGroup to select the typing"""
typing_select = CheckboxGroup(labels=types, active=[], width=150, height=312)
typing_select.on_click(reflect_type)

"""Adding a CheckboxGroup to select the types of the attacks"""
attack_select = CheckboxGroup(labels=types, active=[], width=150, height=312)
attack_select.on_click(multitype)

"""Adding a Toggle to activate/deactivate STAB"""
stab_button = Button(label="activate STAB")
stab_button.on_click(stabify)



"""Adding some divs to display information"""
def_score_DIV = Div(text="defensive score: 0")
off_score_DIV = Div(text="offensive score: 0")

"""Adding some empty divs to move some others or to hide information"""
height_DIV = Div(text="", height=8)

"""Adding everything to the layout and to curdoc"""
layout = column(row(gen_select, column(height_DIV, stab_button)),
                row(column(height_DIV, typing_select),
                    column(defensive_plot),
                    column(matchups_plot),
                    column(offensive_plot),
                    column(height_DIV, attack_select)))


"""Setting the default values."""
monster = Pokemon(None, [], 6)
utility = {"monster": monster, "attacks": [], "typing": [], "gen": 6, "circles": [], "STAB": False}

transform()


curdoc().add_root(layout)
curdoc().title = "Mew's playground"