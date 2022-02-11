import json
import numpy as np
import matplotlib.pyplot as plt

ipcc_coef = {
    "Nuclear": 12,
    "Geothermal": 12,
    "Biomass": 12,
    "Waste": 12,
    "Fossil Brown coal/Lignite": 820,
    "Fossil Peat": 820,
    "Fossil Oil shale": 820,
    "Fossil Hard coal": 820,
    "Fossil Gas": 490,
    "Fossil Oil": 650,
    "Fossil Coal-derived gas": 490,
    "Hydro Run-of-river and poundage": 24,
    "Hydro Water Reservoir": 24,
    "Hydro Pumped Storage": 24,
    "Solar": 45,
    "Wind Onshore": 24,
    "Wind Offshore": 12,
    "Other renewable": 12,
    "Other": 12,
    "Marine": 12
}


def add_ghg_emissions(path="data.json"):
    """
    Ne fonctionne pas !
    :param path: le
    :return: Un dictionnaire avec les émissions de ges par heure
    """
    with open(path, "r") as json_file:
        data = json.load(json_file)

    countries = list(data.keys())
    dates = list(data[countries[0]].keys())

    for country in list(data.keys()):
        for date in dates:
            sources = list(data[country][date])
            data[country][date].update({"GHG emissions": {}})
            for k in range(len(data[country][date][sources[0]])):
                data[country][date]["GHG emissions"].update({str(k + 1): str(np.sum([ipcc_coef[source] * int(data[country][date][source][str(k + 1)])*1e3 for source in sources if str(k + 1) in data[country][date][source].keys()]) / np.sum([int(data[country][date][source][str(k + 1)])*1e3 for source in sources if str(k + 1) in data[country][date][source].keys()]))}) #g de co2 par KWh sur la journée.
    return data


def visualise(data, country="France", date="201801010000"):
    linestyles = [":", "-", "--", "-."]
    sources = list(data[country][date].keys())
    n_points = list(data[country][date][sources[0]])
    prods = {source: [data[country][date][source][str(k + 1)] for k in range(len(n_points)) if
                      str(k + 1) in data[country][date][source].keys()] for source in sources if source != "GHG emissions"}

    print({source: [data[country][date][source][str(k + 1)] for k in range(len(n_points)) if
                      str(k + 1) in data[country][date][source].keys()] for source in sources if source == "GHG emissions"})

    plt.figure()
    plt.title("Energy generation, per hour in {country} the {date}".format(country=country, date=date.replace("0000", "")))
    for i, source in enumerate(prods.keys()):
        plt.plot([float(value) for value in prods[source]], label=source, linestyle=linestyles[i % len(linestyles)])
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()
