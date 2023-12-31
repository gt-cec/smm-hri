# make_smm.py: processes logs to construct a mental model

import smm.smm
import ast
import networkx as nx
import matplotlib.pyplot as plt

G = None  # networkx graph
node_colors = None  # networkx node colors

def run_smm(user_id):
    # pull the lines from the log file
    with open("env/server/logs/" + user_id + ".txt", "r") as f:
        lines = f.readlines()

    # init model
    model = smm.smm.SMM("predicates")

    # init plot
    plt.show(block=False)
    
    # process each line
    for line in lines:
        # convert to a state dict
        state = ast.literal_eval(line)

        # ignore non-state logs
        if "stage" in state:
            continue

        # make sure the model is initialized
        if not model.initialized:
            model.init_belief_state_from_file(state["layout"] + ".layout")

        # update the smm
        model.update(state)
        visualize(model.belief_state)

    # keep the plot visible
    plt.show()

# gets the node color of an object, for the networkx plot
def get_color(name):
    if name == "tomato":
        return "red"
    if name == "onion":
        return "orange"
    if name == "soup":  # dishes are considered soups too, just empty soups
        return "skyblue"
    if name == "station":
        return "purple"
    if name == "pot":
        return "grey"
    if name == "A0":
        return "blue"
    if name == "A1":
        return "green"
    print("NAME", name)
    return "orange"

# shows the networkx plot
def visualize(state):
    global G

    if G is None:
        # create a graph
        G = nx.Graph()
        # add the nodes
        G.add_nodes_from(state["objects"].keys())
        G.add_nodes_from(state["agents"].keys())

    # update the nodes
    for obj in state["objects"]:
        # set the node properties
        node_properties = {
            "x" : state["objects"][obj]["at"][0],
            "y" : 4 - state["objects"][obj]["at"][1],  # the game board is 4 high and 0,0 is at the top left
            "class" : state["objects"][obj]["propertyOf"]["name"],
            "cookTime" : state["objects"][obj]["propertyOf"]["cookTime"],
            "isCooking" : state["objects"][obj]["propertyOf"]["isCooking"],
            "isReady" : state["objects"][obj]["propertyOf"]["isReady"],
            "isIdle" : state["objects"][obj]["propertyOf"]["isIdle"],
        }
        # add a new node if it doesnt exist
        if obj not in G.nodes:
            G.add_node(obj)
        G.nodes[obj].update(node_properties)

    # remove objects that no longer exist or are not marked as visible
    removed = [x for x in G.nodes if (x not in state["objects"] or not state["objects"][x]["visible"]) and x not in state["agents"]]
    [G.remove_node(x) for x in removed]

    # set the edges ("can use with")
    G.clear_edges()
    for object_from in G.nodes:
        if object_from[0] == "A":  # agents do not have edges, only objects
            continue
        # set the node edges
        for object_to_and_weight in state["objects"][object_from]["canUseWith"]:
            if object_to_and_weight[1] > 0 and object_to_and_weight[0] in G.nodes:
                G.add_edge(object_from, object_to_and_weight[0], weight=object_to_and_weight[1])

    # set the node colors by class
    node_colors = [get_color((state["objects"][obj]["propertyOf"]["name"] if obj[0] == "O" else obj)) for obj in G.nodes]
    
    # update the agents
    for agent in state["agents"]:
        # set the node properties
        node_properties = {
            "x" : state["agents"][agent]["at"][0],
            "y" : 4 - state["agents"][agent]["at"][1],  # the game board is 4 high and 0,0 is at the top left
            "facing x" : state["agents"][agent]["facing"][0],
            "facing y" : state["agents"][agent]["facing"][1],
            "holding" : state["agents"][agent]["holding"],
            "goal" : state["agents"][agent]["goal"],
        }
        G.nodes[agent].update(node_properties)

    # plot the graph
    plt.clf()
    pos = nx.rescale_layout_dict({obj : [float(G.nodes[obj]["x"]), float(G.nodes[obj]["y"])] for obj in G.nodes})
    node_labels = {obj : obj for obj in G.nodes}
    nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=700, node_color=node_colors, font_size=10, font_color="black", font_weight="bold", edge_color="gray", linewidths=1, alpha=0.7)

    # display the plot
    plt.pause(0.1)


if __name__ == "__main__":
    run_smm("jack")