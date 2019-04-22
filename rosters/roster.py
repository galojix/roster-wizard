"""Scheduling example 2."""
from ortools.sat.python import cp_model


def main():
    """Run main program."""
    # This program tries to find an optimal assignment of nurses to shifts
    # (3 shifts per day, for 7 days), subject to some constraints (see below).
    # Each nurse can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    # Could perhaps assign priorities to shift requests.
    num_nurses = 21
    num_shifts = 3
    num_days = 7
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    shift_requests = [
        [
            [0, 0, 1],
            [0, 0, 0],
            [0, 0, 1],
            [0, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
            [0, 0, 1],
        ],
        [
            [0, 0, 1],
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 0],
            [0, 0, 1],
        ],
        [
            [0, 1, 0],
            [0, 1, 0],
            [0, 0, 0],
            [1, 0, 0],
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
        ],
        [
            [0, 0, 1],
            [0, 1, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 0],
            [1, 0, 0],
            [0, 0, 0],
        ],
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
            [0, 1, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 0],
        ],
        [
            [0, 0, 0],
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ],
        [
            [0, 1, 0],
            [0, 1, 0],
            [0, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 0],
        ],
        [
            [0, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [0, 0, 0],
        ],
        [
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 0],
            [0, 0, 0],
        ],
        [
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 0, 0],
        ],
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 0],
        ],
        [
            [0, 1, 0],
            [0, 1, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
        ],
        [
            [1, 0, 0],
            [1, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
        ],
        [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
        ],
        [
            [0, 1, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
        ],
        [
            [1, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
        ],
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 0],
        ],
        [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
        ],
        [
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ],
        [
            [0, 0, 0],
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
        ],
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 0],
        ],

    ]
    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.NewBoolVar(f"shift_n{n}d{d}s{s}")

    # Each shift is assigned to exactly two nurses.
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(n, d, s)] for n in all_nurses) == 5)

    # Each nurse works at most one shift per day.
    for n in all_nurses:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 1)

    # min_shifts_assigned is the largest integer such that every nurse can be
    # assigned at least that number of shifts.
    min_shifts_per_nurse = 5
    # 2 * (num_shifts * num_days) // num_nurses
    max_shifts_per_nurse = 5
    # min_shifts_per_nurse + 1 - 1
    for n in all_nurses:
        num_shifts_worked = sum(
            shifts[(n, d, s)] for d in all_days for s in all_shifts
        )
        model.Add(min_shifts_per_nurse <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_nurse)

    model.Maximize(
        sum(
            shift_requests[n][d][s] * shifts[(n, d, s)]
            for n in all_nurses
            for d in all_days
            for s in all_shifts
        )
    )
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)
    for d in all_days:
        print("Day", d)
        for n in all_nurses:
            for s in all_shifts:
                if solver.Value(shifts[(n, d, s)]) == 1:
                    if shift_requests[n][d][s] == 1:
                        print("Nurse", n, "works shift", s, "(requested).")
                    else:
                        print("Nurse", n, "works shift", s, "(not requested).")
        print()

    # Statistics.
    print()
    print("Statistics")
    print(
        "  - Number of shift requests met = %i" % solver.ObjectiveValue(),
        "(out of",
        num_nurses * min_shifts_per_nurse,
        ")",
    )
    print("  - wall time       : %f s" % solver.WallTime())


if __name__ == "__main__":
    main()
