import random
import sys


def parse(filename):
    clauses = []
    count = 0
    for line in open(filename):

        if line[0] == 'c':
            continue
        if line[0] == 'p':
            n_vars = int(line.split()[2])
            lit_clause = [[] for _ in range(n_vars * 2 + 1)]
            continue

        clausePos = 0
        clauseNeg = 0
        for literal in line[:-2].split():
            literal = int(literal)
            if literal > 0:
                clausePos ^= 1 << literal-1
            else:
                clauseNeg ^= 1 << (-literal - 1)
            lit_clause[literal].append(count)
        clauses.append((clausePos, clauseNeg))
        count += 1
    return clauses, n_vars, lit_clause


def get_random_interpretation(n_vars):
    interpretation = 0
    for i in range(n_vars):
        if random.random() < 0.5:
            interpretation ^= 1 << (i)

    return interpretation


def get_true_sat_lit(clauses, interpretation: int):
    true_sat_lit = [0 for _ in clauses]
    for index, clause in enumerate(clauses):
        true_sat_lit[index] += bin(interpretation & clause[0]).count("1") + bin((interpretation & clause[1]) ^ clause[1]).count("1")
    return true_sat_lit


def update_tsl(literal_to_flip, true_sat_lit, lit_clause):
    for clause_index in lit_clause[literal_to_flip]:
        true_sat_lit[clause_index] += 1
    for clause_index in lit_clause[-literal_to_flip]:
        true_sat_lit[clause_index] -= 1


def compute_broken(clause, true_sat_lit, lit_clause, omega=0.4):
    break_min = sys.maxsize
    best_literals = []
    literals = []
    for lit_index, binary in enumerate(bin(clause[0])[::-1]):
        if binary == "1":
            literals.append(lit_index + 1)

    for lit_index, binary in enumerate(bin(clause[1])[::-1]):
        if binary == "1":
            literals.append(-lit_index - 1)

    for literal in literals:

        break_score = 0

        for clause_index in lit_clause[-literal]:
            if true_sat_lit[clause_index] == 1:
                break_score += 1

        if break_score < break_min:
            break_min = break_score
            best_literals = [literal]
        elif break_score == break_min:
            best_literals.append(literal)

    if break_min != 0 and random.random() < omega:
        best_literals = literals

    return random.choice(best_literals)


def run_sat(clauses, n_vars, lit_clause, max_flips_proportion=4):
    max_flips = n_vars * max_flips_proportion
    while 1:
        interpretation = get_random_interpretation(n_vars)
        true_sat_lit = get_true_sat_lit(clauses, interpretation)
        for _ in range(max_flips):

            unsatisfied_clauses_index = [index for index, true_lit in enumerate(true_sat_lit) if
                                         not true_lit]

            if not unsatisfied_clauses_index:
                return interpretation

            clause_index = random.choice(unsatisfied_clauses_index)
            unsatisfied_clause = clauses[clause_index]

            lit_to_flip = compute_broken(unsatisfied_clause, true_sat_lit, lit_clause)

            update_tsl(lit_to_flip, true_sat_lit, lit_clause)

            interpretation ^= 1 << (abs(lit_to_flip) - 1 )


def main():

    clauses, n_vars, lit_clause = parse(sys.argv[1])

    solution = run_sat(clauses, n_vars, lit_clause)

    sol_arr = [(index + 1) if binary=="1" else (-index - 1) for index, binary in enumerate(bin(solution)[:1:-1])]
    
    while(len(sol_arr) < n_vars):
        sol_arr.append(-len(sol_arr) - 1)

    print('s SATISFIABLE')
    print('v ' + ' '.join(map(str, sol_arr)) + ' 0')


if __name__ == '__main__':
    main()
