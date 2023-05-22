from pyomo.environ import ConcreteModel, Var, Objective, SolverFactory, ConstraintList
from pyomo.environ import PositiveIntegers, RangeSet, Binary

def LineGrid(n):
    # Create a concrete model
    model = ConcreteModel()

    model.I=RangeSet(1,n)
    #it has been proven that the infinite line can be paved with a max of 3 tiles periodically : 1 2 1 3
    m=n
    if m>3:
        m=3
    model.J=RangeSet(1,m)
    # Variables
    model.a = Var(model.I, model.J, within=Binary)

    # Objective Function
    #reduce the total sum of integers in the line
    model.obj = Objective(expr=sum(sum(j*model.a[i,j] for j in model.J) for i in model.I))
 

    # Constraints :
    model.distance=ConstraintList()
    #not more than one number j in a taxicab distance of j cells 
    for j in model.J:
        for m in range(1,n-j+1):
            #print([(i,j) for i in range(m, m+j+1)])
            model.distance.add(expr=sum(model.a[i,j] for i in range(m, m+j+1)) <= 1)

    #only one number per cell
    model.unique=ConstraintList()
    for i in model.I:
        model.unique.add(expr=sum(model.a[i,j] for j in model.J) == 1)


    # Solve the model
    sol = SolverFactory('gurobi').solve(model, tee=True)

    # CHECK SOLUTION STATUS

    # Get a JSON representation of the solution
    sol_json = sol.json_repn()
    # Check solution status
    if sol_json['Solver'][0]['Status'] != 'ok':
        return None
    if sol_json['Solver'][0]['Termination condition'] != 'optimal':
        return None

    result=[]
    for i in model.I:
        for j in model.J:
            if model.a[i,j]() == 1:
                result.append(j)
                break

    return result


if __name__ == "__main__":
    
    result=LineGrid(10)
    print(result)