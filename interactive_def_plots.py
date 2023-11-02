import pandas as pd
import numpy as np
import statistics as st
from bokeh.models import ColumnDataSource, Div, RadioButtonGroup, Slope, Select, Button
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row

from Pokemon import Pokemon

types = ["Grass", "Fire", "Water", "Bug", "Poison", "Normal", "Flying", "Electric", "Ground",
         "Fighting", "Psychic", "Rock", "Ice", "Ghost", "Dragon", "Steel", "Dark", "Fairy"]
gen_types = {1: 15, 2: 17, 6: 18}

def_labels = ["Defensive Score", "Double Weaknesses", "Weaknesses", 
              "Defensive Neutralities", "Resistances", "Double Resistances", "Immunities"]

sort_dict = {"Defensive Score": [6, 3], "Defensive Attribute": [6, 3], "Double Weaknesses": [2, 0],
             "Weaknesses": [1, 0], "Defensive Neutralities": [0, 6], "Resistances": [5, 0],
             "Double Resistances": [4, 0], "Immunities": [0, 3]}

ascend_dict = {"Defensive Score": [False, True, True], "Defensive Attribute": [False, True, True],
               "Double Weaknesses": [False, False, False], "Weaknesses": [False, False, False],
               "Defensive Neutralities": [True, False, False], "Resistances": [True, True, False],
               "Double Resistances": [True, True, False], "Immunities": [True, False, True]}

colours= ["purple", "crimson", "red", "blue", "green", "lime", "black"]


def defensive_dataframe(dual, generation=6):
    """Returns a dataframe with the needed information for the plots."""
    scores = []
    attrs = []
    d_weak = []
    weaknesses = []
    neutralities = []
    resistances = []
    d_rest = []
    immunities = []
    for element in types[:gen_types[generation]]:
        Element = Pokemon(None, [element, dual], generation)
        scores.append(Element.def_score)
        attrs.append(Element.def_attr)
        d_weak.append(len(Element.d_weak))
        weaknesses.append(len(Element.weaknesses))
        neutralities.append(len(Element.def_neutral))
        resistances.append(len(Element.resistances))
        d_rest.append(len(Element.d_rest))
        immunities.append(len(Element.immunities))

    df = pd.DataFrame(list(zip(types[:gen_types[generation]], scores, attrs, d_weak, 
                               weaknesses, neutralities, resistances, d_rest, immunities)),
                      columns=["Types", "Defensive Score", "Defensive Attribute", "Double Weaknesses", "Weaknesses",
                               "Defensive Neutralities", "Resistances", "Double Resistances", "Immunities"])
    return df

def defensive_analysis(dataframe):
    """Returns a dataframe with lists of various statistical properties of the different dataframe columns."""
    """The dataframe includes, in this order: minimum, maximum, (arithmetic) mean, median, mode, standard deviation."""
    analysis = []
    for k in def_labels:
        stats = [np.amin(df[k]), np.amax(df[k]), np.mean(df[k]), st.median(df[k]), st.stdev(df[k]), st.multimode(df[k])]
        for i in range(5):
            stats[i] = round(stats[i], 2)
        for k in range(len(stats[5])):
            stats[5][k] = round(stats[5][k], 2)
        analysis.append(stats)
    analysis = pd.DataFrame([analysis[i] for i in range(len(analysis))], index=def_labels)
    analysis = analysis.transpose()
    return analysis

def make_divs(n):
    """Creates a DIV displaying the various statistical properties of the dataframe."""
    data = analysis[def_labels[n]]
    
    stat_div = Div(text=f"range = [{data[0]}, {data[1]}]" + '</br>' +
                        f"mean = {data[2]}" + '</br>' + f"median = {data[3]}" + '</br>' +
                        f"mode = {data[5][0] if len(data[5])==1 else sorted(data[5])}" + '</br>' +
                        f"standard deviation = {data[4]}")
    emptyDIV = Div(width=50)
    DIV_dict[def_labels[n]] = stat_div
    return row(emptyDIV, stat_div)
    
def update_div(labeling=None):
    """Updates either a single DIV or all the DIVs with the new values from the dataframe."""
    analysis = defensive_analysis(df)
    if labeling:
        to_update = [labeling]
    else:
        to_update = def_labels
    for label in to_update:
        data = analysis[label]
        DIV_dict[label].text = (f"range = [{data[0]}, {data[1]}]" + '</br>' +
                                f"mean = {data[2]}" + '</br>' + f"median = {data[3]}" + '</br>' +
                                f"mode = {data[5][0] if len(data[5])==1 else sorted(data[5])}" + '</br>' +
                                f"standard deviation = {data[4]}")
    
def regression_line(n):
    """Adds the regression line to the plot."""
    Plot = plot_list[n]
    slope, intercept = np.polyfit(df[def_labels[n]], np.arange(start=1, stop=gen_types[gen]+1, step=1), 1)
    regression_line = Slope(gradient=slope, y_intercept=intercept, line_color=colours[n])
    Plot.add_layout(regression_line)
    regression["line"] = regression_line

def callback(new):
    """Defining the callback function for the RadioButtonGroup."""
    """It sorts the df, plots the data with updated y_axis and shows the regression line."""
    global df
    regression["clicked"] = new
    if regression["line"] != None:
        regression["line"].visible = False
    for i,d in enumerate(def_labels):
        if i == new:
            sort_by = [def_labels[i]] + [def_labels[k] for k in sort_dict[d]]
            df = df.sort_values(by=sort_by, ascending=ascend_dict[d], ignore_index=True)
            source.data = dict(Types=df["Types"], Defensive_Score=df["Defensive Score"],
                               Defensive_Attribute=df["Defensive Attribute"], Double_Weaknesses=df["Double Weaknesses"],
                               Weaknesses=df["Weaknesses"], Defensive_Neutralities=df["Defensive Neutralities"], 
                               Resistances=df["Resistances"], Double_Resistances=df["Double Resistances"],
                               Immunities=df["Immunities"])

    """Updating the plots with the newly sorted dataframe."""
    for i, label in enumerate(def_labels):
        Plot = plot_list[i]
        Plot.y_range.factors = df["Types"].to_list()
        circles = Plot.circle(x=label.replace(" ", "_"), y="Types", size=10, source=source, color=colours[i])
        # circles_dict[label] = circles
        # Plot.add_layout(circles)
    if analysis[def_labels[new]][0] < analysis[def_labels[new]][1]:  
        regression_line(new)
        if not regression["visible"]:
            regression["line"].visible = False
        if DIV_visibility:
            update_div()
            
def update(attr, old, new):
    """Defining the update function for the dual_select."""
    global df, source
    if regression["line"] != None:
        regression["line"].visible = False
        regression["line"] = None
    dual = dual_select.value
    df = defensive_dataframe(dual, gen)

    callback(regression["clicked"])

def change(attr, old, new): 
    """Currently unused."""
    """Defining the callback function for "metric"."""
    Plot = Defensive_Score_plot
    if new == "Defensive Attribute":
        Plot.x_range.update(start=-6.5, end=7.5)
    if new == "Defensive Score":
        Plot.x_range.update(start=-5, end=8.5)

    def_labels[0] = new
    Plot.title.text = new
    callback(regression["clicked"])
    if DIV_visibility:
        update_div(new)
    buttons.labels[0] = def_labels[0]

def get_def_attr(attr, old, new):
    pass

def time_travel(attr, old, new):
    """Defining the callback function for "generation"."""
    global gen
    if regression["line"] != None:
        regression["line"].visible = False
        regression["line"] = None
    if new == "1":
        gen = 1
    if new == "2 - 5":
        gen = 2
    if new == "6 - 9":
        gen = 6
                            
    if dual_select.value == "None":
        update(attr="value", old="None", new="None")
    else:
        dual_select.value = "None"
        
    dual_select.options = ["None"] + types[:gen_types[gen]]

def toggle_stats():
    """Defining the callback function for stats_button."""
    if DIV_dict[def_labels[0]].visible == True:
        DIV_visibility = False
        for label in def_labels:
            DIV_dict[label].visible = False
        stats_button.label = "Show statistical analysis"
    else:
        DIV_visibility = True
        update_div()
        for label in def_labels:
            DIV_dict[label].visible = True
        stats_button.label = "Hide statistical analysis"

def toggle_line():
    """Defining the callback function for line_button."""
    if regression["visible"] == True:
        if regression["line"]:
            regression["line"].visible = False
        regression["visible"] = False
        line_button.label = "Show regression line"
    else:
        regression["line"].visible = True
        regression["visible"] = True
        line_button.label = "Hide regression line"


"""Fetching the needed dataframe."""
gen = 6
df = defensive_dataframe(None, gen)
df = df.sort_values(by="Defensive Score", ascending=False, ignore_index=True)
analysis = defensive_analysis(df)
circles = None

"""Creating the ColumnDataSource."""
source = ColumnDataSource(dict(Types=df["Types"], Defensive_Score=df["Defensive Score"], 
                               Defensive_Attribute=df["Defensive Attribute"], Double_Weaknesses=df["Double Weaknesses"], 
                               Weaknesses=df["Weaknesses"], Defensive_Neutralities=df["Defensive Neutralities"], 
                               Resistances=df["Resistances"], Double_Resistances=df["Double Resistances"],
                               Immunities=df["Immunities"]))


"""Creating the plot showing score against typing."""
Defensive_Score_plot = figure(title="Defensive Score", plot_height=600, plot_width=250,
                         x_range=[-5.75, 9.5], y_range=df["Types"], toolbar_location=None, tools="")

"""Creating the plot showing amount of immunities against typing."""
Immunities_plot = figure(title="Immunities", plot_height=600, plot_width=250,
                         x_range=[-0.25, 3.25], y_range=df["Types"], toolbar_location=None, tools="")

"""Creating the plot showing amount of double resistances against typing."""
Double_Resistances_plot = figure(title="Double Resistances", plot_height=600, plot_width=250,
                         x_range=[-0.5, 5.5], y_range=df["Types"], toolbar_location=None, tools="")

"""Creating the plot showing amount of resistances against typing."""
Resistances_plot = figure(title="Resistances", plot_height=600, plot_width=250,
                         x_range=[-0.5, 11.5], y_range=df["Types"], toolbar_location=None, tools="")

"""Creating the plot showing amount of neutralities against typing."""
Defensive_Neutralities_plot = figure(title="Defensive Neutralities", plot_height=600, plot_width=250,
                         x_range=[-0.5, 17], y_range=df["Types"], toolbar_location=None, tools="")

"""Creating the plot showing amount of weaknesses against typing."""
Weaknesses_plot = figure(title="Weaknesses", plot_height=600, plot_width=250,
                         x_range=[-0.5, 7.5], y_range=df["Types"], toolbar_location=None, tools="")

"""Creating the plot showing amount of double weaknesses against typing."""
Double_Weaknesses_plot = figure(title="Double Weaknesses", plot_height=600, plot_width=250,
                         x_range=[-0.25, 3.25], y_range=df["Types"], toolbar_location=None, tools="")


"""Creating a list of all the plots, adding the glyphs and DIVs."""
plot_list = [Defensive_Score_plot, Double_Weaknesses_plot, Weaknesses_plot, Defensive_Neutralities_plot,
             Resistances_plot, Double_Resistances_plot, Immunities_plot]
DIV_dict = {def_label: Div(text="") for def_label in def_labels}
DIV_visibility = True
regression = {"line": None, "visible": True, "clicked": None}
# circles_dict = {plot: None for plot in def_labels}
for i, plot in enumerate(plot_list):
    plot.circle(x=def_labels[i].replace(" ", "_"), y="Types", size=10, source=source, color=colours[i])
layout_list = [column(plot_list[i], make_divs(i)) for i in range(len(plot_list))]


"""Creating the RadioButtonGroup, one button for each plot."""
buttons = RadioButtonGroup(labels=def_labels)
buttons.on_click(callback)


"""Adding a Select to make it possible to investigate dual typings."""
dual_select = Select(title="Choose the dual type", value="None", options=["None"]+types[:gen_types[gen]])
dual_select.on_change("value", update)

"""Adding a Select to interchange the "Defensive Score" and "Defensive Attribute" plot."""
metric_select = Select(title="Select a defensive metric.", value="Defensive Score",
                       options=["Defensive Score"])    #"Defensive Attribute"
metric_select.on_change("value", change)

"""Adding a Select to change the generation."""
gen_select = Select(title="Select a generation", value="6 - 9", options=["1", "2 - 5", "6 - 9"])
gen_select.on_change("value", time_travel)

"""Adding a Button to toggle the statistical analysis."""
stats_button = Button(label="Hide statistical analysis")
stats_button.on_click(toggle_stats)

"""Adding a Button to hide the RegressionLine."""
line_button = Button(label="Hide regression line")
line_button.on_click(toggle_line)
spacingDIV1 = Div(text="", height=8)


"""Adding everything to the layout and to curdoc."""
layout = column(row(layout_list), 
                buttons,
                row(dual_select, metric_select, gen_select, 
                column(spacingDIV1, 
                       row(stats_button, line_button))))
curdoc().add_root(layout)
curdoc().title = "Call of Arceus"