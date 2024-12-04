import numpy as np


# Mod. to search only in the integer space and with tuned parameters
def pso_search_among_integer(
    func,
    lb,
    ub,
    ieqcons=[],
    f_ieqcons=None,
    args=(),
    kwargs={},
    swarmsize=100,
    omega=0.5,
    phip=0.5,
    phig=0.5,
    maxiter=100,
    minstep=1e-8,
    minfunc=1e-8,
    debug=False,
):
    import numpy as np

    assert len(lb) == len(ub), "Lower- and upper-bounds must be the same length"
    assert hasattr(func, "__call__"), "Invalid function handle"
    lb = np.array(lb, dtype=int)
    ub = np.array(ub, dtype=int)
    assert np.all(
        ub > lb
    ), "All upper-bound values must be greater than lower-bound values"

    v_max = np.maximum(np.ceil((ub - lb) / 4).astype(int), 1)
    v_min = -v_max

    obj = lambda x: func(x, *args, **kwargs)
    if f_ieqcons is None:
        if not len(ieqcons):
            if debug:
                print("No constraints given.")
            cons = lambda x: np.array([0])
        else:
            if debug:
                print("Converting ieqcons to a single constraint function")
            cons = lambda x: np.array([y(x, *args, **kwargs) for y in ieqcons])
    else:
        if debug:
            print("Single constraint function given in f_ieqcons")
        cons = lambda x: np.array(f_ieqcons(x, *args, **kwargs))

    def is_feasible(x):
        check = np.all(cons(x) >= 0)
        return check

    S = swarmsize
    D = len(lb)
    x = np.random.randint(lb, ub + 1, size=(S, D))
    v = np.zeros_like(x, dtype=int)
    p = x.copy()
    fp = np.array([obj(xi) for xi in x])
    g = x[np.argmin(fp), :]
    fg = np.min(fp)

    if debug:
        print(f"Initial global best: {g}, Objective: {fg}")

    it = 1
    while it <= maxiter:
        rp = np.random.uniform(size=(S, D))
        rg = np.random.uniform(size=(S, D))
        for i in range(S):
            inertia = omega * v[i, :]
            cognitive = phip * rp[i, :] * (p[i, :] - x[i, :])
            social = phig * rg[i, :] * (g - x[i, :])
            new_velocity = np.round(inertia + cognitive + social).astype(int)
            v[i, :] = np.clip(new_velocity, v_min, v_max)

            new_position = x[i, :] + v[i, :]
            x[i, :] = np.clip(new_position, lb, ub).astype(int)

            fx = obj(x[i, :])

            if debug:
                print(
                    f"Particle {i}: Velocity = {v[i, :]}, Position = {x[i, :]}, Fitness = {fx}"
                )

            if fx < fp[i] and is_feasible(x[i, :]):
                p[i, :] = x[i, :].copy()
                fp[i] = fx

                if fx < fg:
                    if debug:
                        print(f"New best for swarm at iteration {it}: {x[i, :]} {fx}")

                    g = x[i, :].copy()
                    fg = fx

        step_sizes = np.linalg.norm(v, axis=1)
        if debug:
            print(f"Step sizes: {step_sizes}")

        if np.all(step_sizes <= minstep):
            print(f"Stopping search: Particle velocities below {minstep}")
            break
        if np.abs(fg - np.min(fp)) <= minfunc:
            print(f"Stopping search: Objective function improvement below {minfunc}")
            break

        if debug:
            print(f"Iteration {it}: Global best = {g}, Objective = {fg}")
        it += 1

    print(f"Stopping search: Maximum iterations reached --> {maxiter}")

    if not is_feasible(g):
        print("However, the optimization couldn't find a feasible design. Sorry")
    return g, fg
