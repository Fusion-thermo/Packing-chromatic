from pyomo.environ import ConcreteModel, Var, Objective, SolverFactory, ConstraintList
from pyomo.environ import PositiveIntegers, RangeSet, Binary
#https://bsubercaseaux.github.io/blog/2023/packingchromatic/

def even_indices(i0,j0,k,n):
    #i,j is the lowest i cell in the diamond
    #we consider for the calculation that it is in the center, it's corrected when added to the list
    indices=[]
    d=k//2
    for i in range(i0-d,i0+d+1):
        for j in range(j0-d,j0+d+1):
            if i+d>0 and i+d<=n and j>0 and j<=n and abs(i0-i) + abs(j0-j) <= d:
                indices.append((i+d,j))
    return indices

def odd_indices(i0,j0,k,n):
    #we consider to be in a k+1 pair diamond but removing the central horizontal line
    indices=[]
    k+=1
    d=k//2
    for i in range(i0-d,i0):
        for j in range(j0-d,j0+d+1):
            if i+d>0 and i+d<=n and j>0 and j<=n and abs(i0-i) + abs(j0-j) <= d:
                indices.append((i+d,j))
    for i in range(i0+1,i0+d+1):
        for j in range(j0-d,j0+d+1):
            if i+d-1>0 and i+d-1<=n and j>0 and j<=n and abs(i0-i) + abs(j0-j) <= d:
                indices.append((i+d-1,j))
    return indices

def SquareGrid(n):
    # Create a concrete model
    model = ConcreteModel()

    model.I=RangeSet(1,n)
    model.J=RangeSet(1,n)
    m=n**2
    #it has been proven that the infinite grid can be paved with a max of 15 tiles
    if m>15:
        m=15
    model.K=RangeSet(1,m)
    # Variables
    model.a = Var(model.I, model.J, model.K, within=Binary)

    # Objective Function
    #reduce the total sum of integers in the line
    model.obj = Objective(expr=sum(sum(sum(k*model.a[i,j,k] for k in model.K) for j in model.J) for i in model.I))
    #reduce the quantity of numbers above a certain number, way faster but not with the lowest numbers possible
    #model.obj = Objective(expr=sum(sum(sum(model.a[i,j,k] for k in range(7,n**2+1)) for j in model.J) for i in model.I))

    # Constraints :
    model.distance=ConstraintList()
    #not more than one number in a taxicab distance of k cells 
    for k in model.K:
        #no need to add redundant constraints
        m=n+1-k
        if m<2:
            m=2
        for i in range(1,m):
            for j in model.J:
                #could be done earlier and used as an index table
                if k/2==k//2:
                    indices=even_indices(i,j,k,n)
                else:
                    indices=odd_indices(i,j,k,n)
                #print(i,j,k)
                #print(indices)
                #print([(i_d,j_d) for i_d,j_d in indices])
                #i increasing
                model.distance.add(expr=sum(model.a[i_d,j_d,k] for i_d,j_d in indices) <= 1)
                #j increasing, all cells shift sides, however it only works for a square grid
                model.distance.add(expr=sum(model.a[j_d,i_d,k] for i_d,j_d in indices) <= 1)

    #only one number per cell
    model.unique=ConstraintList()
    for i in model.I:
        for j in model.J:
            model.unique.add(expr=sum(model.a[i,j,k] for k in model.K) == 1)


    # Solve the model
    sol = SolverFactory('gurobi').solve(model, tee=True,options_string="TimeLimit=10")

    result=[]
    for i in model.I:
        ligne=[]
        for j in model.J:
            for k in model.K:
                if model.a[i,j,k]() == 1:
                    ligne.append(k)
                    break
        print(ligne)
        result.append(ligne[:])

    return result


if __name__ == "__main__":
    
    result=SquareGrid(5)
    #print(result)
    #print(even_indices(1,3,1,5))
    #print(odd_indices(1,4,1,7))
    #print(odd_indices(1,3,5,6))