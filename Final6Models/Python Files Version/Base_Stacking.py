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


s = data[7]
len(s)


# In[4]:


m = Model("Base_Stacking")


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


# ## d_ij Minimum Distance Constraint

# In[11]:


ls_dtup = []
for i in ONE_N:
    for j in range(i+1,len(s)+1):
        ls_dtup.append((i,j))

d = {}

for i in ONE_N:
    for j in range(i+1,len(s)+1):
        w = min(j-i,len(s)-j+i)
        d[i,j] = w

d


# In[12]:


for i in ONE_N:
    for j in range(i+1,len(s)+1):
        if d[i,j] < 3:
            x[i,j] = 0

x


# ## f_ij

# In[13]:


ls_ftup = []
for i in ONE_N:
    for j in range(i+1,len(s)+1):
        ls_ftup.append((i,j))
        


        
f = {}

temp = ''
temp = 'x' + s
temp
for i in ONE_N:
    for j in range(i+1,len(s)+1):
        if (((temp[i] == 'C') & (temp[j] == 'G')) or ((temp[i] == 'G') & (temp[j] == 'C'))):
            f[i,j] = 3
        elif (((temp[i] == 'A') & (temp[j] == 'U')) or ((temp[i] == 'U') & (temp[j] == 'A'))):
            f[i,j] = 2
        elif (((temp[i] == 'G') & (temp[j] == 'U')) or ((temp[i] == 'U') & (temp[j] == 'G'))):
            f[i,j] = 0.1
        elif (((temp[i] == 'A') & (temp[j] == 'C')) or ((temp[i] == 'C') & (temp[j] == 'A'))):
            f[i,j] = 0.05
        else:
            f[i,j] = 0

f


# ## Q_ij

# In[14]:


ls_qtup = []
for i in range(1,len(s)-2):
    for j in range(i+3,len(s)+1):
        ls_qtup.append((i,j))

q_ij = m.addVars(ls_qtup,name='Q_ij',vtype=GRB.BINARY)
q_ij


# ## Q_nj

# In[15]:


ls_njtup = []
for j in range(3,len(s)):
    ls_njtup.append((len(s),j))
    
    
q_nj = m.addVars(ls_njtup,name='Q_nj',vtype=GRB.BINARY)
q_nj


# ## Additional Constraints for Q_ij and Q_nj variables

# In[16]:


m.addConstrs(2*q_ij[i,j] <= x[i,j] + x[i+1,j-1] for i in range(1,len(s)-2) for j in range(i+3,len(s)+1))


# In[17]:


m.addConstrs(2*q_nj[len(s),j] <= x[j,len(s)] + x[1,j-1] for j in range(3,len(s)))


# ## Q_i,i+1

# In[18]:


ls_ii1tup = []
for i in range(1,len(s)):
    ls_ii1tup.append((i,i+1))

m.addVars(ls_ii1tup,name='Q_ij',vtype=GRB.BINARY)
for i in range(1,len(s)):
    q_ij[i,i+1] = 0

q_ij


# ## Q_i,i+2

# In[19]:


ls_ii2tup = []
for i in range(1,len(s)-1):
    ls_ii2tup.append((i,i+2))

m.addVars(ls_ii2tup,name='Q_ij',vtype=GRB.BINARY)
for i in range(1,len(s)-1):
    q_ij[i,i+2] = 0

q_ij


# ## Q_n,n-1

# In[20]:


q_nj[len(s),len(s)-1] = 0


# ## Q_n,n-2

# In[21]:


q_nj[len(s),len(s)-2] = 0


# ## Non-Crossing Constraint

# In[22]:


m.addConstrs(quicksum(x[k,l] for k in range(i+1,j) for l in [i for i in list(range(1,len(s)+1)) if i >= j]) <= (10**6)*(1-x[i,j]) for i in range(1,len(s)+1) for j in range(i+1,len(s)+1))


# ## Character in At most one pair

# In[23]:


m.addConstrs(quicksum([x[i,k] for i in range(1,k)]) + quicksum([x[k,j] for j in list(range(k+1,len(s)+1))]) <= 1 for k in ONE_N)


# # Objective

# In[24]:


m.setObjective((quicksum(f[i,j]*x[i,j] for i in ONE_N for j in list(range(i+1,len(s)+1)))) + 
               (quicksum(q_ij[i,j] for i in range(1,len(s)-2) for j in range(i+3,len(s)+1)) + 
               (quicksum(q_nj[len(s),j] for j in range(3,len(s))))),GRB.MAXIMIZE)


# In[25]:


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
        if(v.x == 1):
            print("%s = %g" % (v.varName, v.x))
    print("Optimal objective value:\n{}".format(m.objVal))
    print("Runtime is:", m.Runtime)


# In[ ]:


m.write("check.lp")

