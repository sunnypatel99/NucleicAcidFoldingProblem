#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from gurobipy import *


# In[2]:


with open('test_case.txt') as text_file:
    data = text_file.read().splitlines()

data


# In[3]:


s = data[1]
len(s)


# In[4]:


m = Model("Simple")


# In[5]:


m.setParam('OutputFlag',True)
m.setParam('TimeLimit', 5*60)


# # Pre-Processing Data

# In[6]:


ONE_N = list(range(1,len(s)+1))
ONE_N


# ## A_i, U_i, C_i, G_i

# In[7]:


a = {}
u = {}
c = {}
g = {}


# In[8]:


index = 1
for n in s:
    if (n == 'A'):
        a[index] = 1
        u[index] = 0
        c[index] = 0
        g[index] = 0
    if (n == 'U'):
        a[index] = 0
        u[index] = 1
        c[index] = 0
        g[index] = 0
    if (n == 'C'):
        a[index] = 0
        u[index] = 0
        c[index] = 1
        g[index] = 0
    if (n == 'G'):
        a[index] = 0
        u[index] = 0
        c[index] = 0
        g[index] = 1
    
    index += 1


# In[9]:


print(a)
print(u)
print(c)
print(g)
print(s)


# ## X_ij

# In[10]:


ls_tup = []
for i in range(1,len(s)):
    for j in range(i+1,len(s)+1):
        ls_tup.append((i,j))
        
x = m.addVars(ls_tup,name='X_ij',vtype=GRB.BINARY)
x


# ## Complementary Pairs

# In[11]:


for i in ONE_N:
    for j in range(i+1,len(s)+1):
        if (a[i] + a[j] + c[i] + c[j] == 2):
            x[i,j] = 0
        if (a[i] + a[j] + g[i] + g[j] == 2):
            x[i,j] = 0
        if (u[i] + u[j] + c[i] + c[j] == 2):
            x[i,j] = 0
        if (u[i] + u[j] + g[i] + g[j] == 2):
            x[i,j] = 0


# # Objective Function

# In[12]:


m.setObjective((quicksum(x[i,j] for i in ONE_N for j in list(range(i+1,len(s)+1)))),GRB.MAXIMIZE)


# # Constraints

# ## Character can be in at most 1 pair

# In[13]:


m.addConstrs(quicksum([x[i,k] for i in range(1,k)]) + quicksum([x[k,j] for j in list(range(k+1,len(s)+1))]) <= 1 for k in ONE_N)


# ## Non-Crossing Constraint

# In[14]:


m.addConstrs(quicksum(x[k,l] for k in range(i+1,j) for l in [i for i in list(range(1,len(s)+1)) if i >= j]) <= (10**6)*(1-x[i,j]) for i in range(1,len(s)+1) for j in range(i+1,len(s)+1))


# In[15]:


# Optimize the model
m.optimize()
# Print the result
status_code = {1: 'LOADED', 2: 'OPTIMAL', 3: 'INFEASIBLE', 4: 'INF_OR_UNBD', 5: 'UNBOUNDED'}
status = m.status
print("The optimization status is {}".format(status_code[status]))
if status == 2:
# Retrieve variables value
    print("Optimal solution:")
    for v in m.getVars():
        if (v.x == 1):
            print("%s = %g" % (v.varName, v.x))
    print("Optimal objective value:\n{}".format(m.objVal))
    print("Runtime is:", m.Runtime)


# In[16]:


m.write("check.lp")

