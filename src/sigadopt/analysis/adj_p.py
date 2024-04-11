from scipy.stats import false_discovery_control


p_vals = [
    # Policies
    # deemph
    # 1.0528800972503641e-05,
    # 0.011827168660876694,
    # 0.0026035239065010825,
    # update
    # 0.9707827344233013,
    # 0.5995228018080654,
    # 4.299451618877173e-13,
    #   Events
    # docker hack
    0.9992863507506341,
    0.8700614088080117,
    0.007501344529292149,
    # solar winds
    0.6149525171398281,
    0.0054432188885332605,
    0.01054375099817995,
    # Tooling
]

adj_p_vals = false_discovery_control(p_vals)

for adj in adj_p_vals:
    print(adj)
