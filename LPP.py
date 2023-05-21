from lpproj import LocalityPreservingProjection

def getLLP(means):
    lpp4 = LocalityPreservingProjection(n_components=4)
    lpp8 = LocalityPreservingProjection(n_components=8)

    dim4 = lpp4.fit_transform(means)
    dim8 = lpp8.fit_transform(means)

    return (dim4, dim8)


