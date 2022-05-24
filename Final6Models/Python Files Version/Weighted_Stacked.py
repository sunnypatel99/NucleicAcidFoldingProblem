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


m = Model("Weighted_Stacking")


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


# ## w_ij

# In[16]:


ls_wtup = []
for i in range(1,len(s)-2):
    for j in range(i+3,len(s)+1):
        ls_wtup.append((i,j))
        
w_ij = {}
w_ij


# In[17]:


for i in range(1,len(s)-2):
    for j in range(i+3,len(s)+1):
        if ((a[i] == 1) & (u[j] == 1) & (a[i+1] == 1) & (u[j-1] == 1)):
            w_ij[i,j] = 9
        elif ((a[i] == 1) & (u[j] == 1) & (c[i+1] == 1) & (g[j-1] == 1)):
            w_ij[i,j] = 21
        elif ((a[i] == 1) & (u[j] == 1) & (g[i+1] == 1) & (c[j-1] == 1)):
            w_ij[i,j] = 24
        elif ((a[i] == 1) & (u[j] == 1) & (u[i+1] == 1) & (a[j-1] == 1)):
            w_ij[i,j] = 13
            
        elif ((c[i] == 1) & (g[j] == 1) & (a[i+1] == 1) & (u[j-1] == 1)):
            w_ij[i,j] = 22
        elif ((c[i] == 1) & (g[j] == 1) & (c[i+1] == 1) & (g[j-1] == 1)):
            w_ij[i,j] = 33
        elif ((c[i] == 1) & (g[j] == 1) & (g[i+1] == 1) & (c[j-1] == 1)):
            w_ij[i,j] = 34
        elif ((c[i] == 1) & (g[j] == 1) & (u[i+1] == 1) & (a[j-1] == 1)):
            w_ij[i,j] = 24
            
        elif ((g[i] == 1) & (c[j] == 1) & (a[i+1] == 1) & (u[j-1] == 1)):
            w_ij[i,j] = 21
        elif ((g[i] == 1 )& (c[j] == 1) & (c[i+1] == 1) & (g[j-1] == 1)):
            w_ij[i,j] = 24
        elif ((g[i] == 1) & (c[j] == 1) & (g[i+1] == 1) & (c[j-1] == 1)):
            w_ij[i,j] = 33
        elif ((g[i] == 1) & (c[j] == 1) & (u[i+1] == 1) & (a[j-1] == 1)):
            w_ij[i,j] = 21
            
        elif ((u[i] == 1 )& (a[j] == 1) & (a[i+1] == 1) & (u[j-1] == 1)):
            w_ij[i,j] = 12
        elif ((u[i] == 1) & (a[j] == 1) & (c[i+1] == 1) & (g[j-1] == 1)):
            w_ij[i,j] = 23
        elif ((u[i] == 1) & (a[j] == 1) & (g[i+1] == 1) & (c[j-1] == 1)):
            w_ij[i,j] = 21
        elif ((u[i] == 1) & (a[j] == 1) & (u[i+1] == 1) & (a[j-1] == 1)):
            w_ij[i,j] = 16
        else:
            w_ij[i,j] = 1
            

w_ij


# ## w_nj

# In[18]:


ls_wnjtup = []
for j in range(3,len(s)):
    ls_wnjtup.append((len(s),j))


w_nj = {}
w_nj


# In[19]:


for j in range(3,len(s)):
    if ((a[len(s)] == 1) & (u[j] == 1) & (a[1] == 1) & (u[j-1] == 1)):
        w_nj[len(s),j] = 9
    elif ((a[len(s)] == 1) & (u[j] == 1) & (c[1] == 1) & (g[j-1] == 1)):
        w_nj[len(s),j] = 21
    elif ((a[len(s)] == 1) & (u[j] == 1) & (g[1] == 1) & (c[j-1] == 1)):
        w_nj[len(s),j] = 24
    elif ((a[len(s)] == 1) & (u[j] == 1) & (u[1] == 1) & (a[j-1] == 1)):
        w_nj[len(s),j] = 13

    elif ((c[len(s)] == 1) & (g[j] == 1) & (a[1] == 1) & (u[j-1] == 1)):
        w_nj[len(s),j] = 22
    elif ((c[len(s)] == 1) & (g[j] == 1) & (c[1] == 1) & (g[j-1] == 1)):
        w_nj[len(s),j] = 33
    elif ((c[len(s)] == 1) & (g[j] == 1) & (g[1] == 1) & (c[j-1] == 1)):
        w_nj[len(s),j] = 34
    elif ((c[len(s)] == 1) & (g[j] == 1) & (u[1] == 1) & (a[j-1] == 1)):
        w_nj[len(s),j] = 24

    elif ((g[len(s)] == 1) & (c[j] == 1) & (a[1] == 1) & (u[j-1] == 1)):
        w_nj[len(s),j] = 21
    elif ((g[len(s)] == 1 )& (c[j] == 1) & (c[1] == 1) & (g[j-1] == 1)):
        w_nj[len(s),j] = 24
    elif ((g[len(s)] == 1) & (c[j] == 1) & (g[1] == 1) & (c[j-1] == 1)):
        w_nj[len(s),j] = 33
    elif ((g[len(s)] == 1) & (c[j] == 1) & (u[1] == 1) & (a[j-1] == 1)):
        w_nj[len(s),j] = 21

    elif ((u[len(s)] == 1 )& (a[j] == 1) & (a[1] == 1) & (u[j-1] == 1)):
        w_nj[len(s),j] = 12
    elif ((u[len(s)] == 1) & (a[j] == 1) & (c[1] == 1) & (g[j-1] == 1)):
        w_nj[len(s),j] = 23
    elif ((u[len(s)] == 1) & (a[j] == 1) & (g[1] == 1) & (c[j-1] == 1)):
        w_nj[len(s),j] = 21
    elif ((u[len(s)] == 1) & (a[j] == 1) & (u[1] == 1) & (a[j-1] == 1)):
        w_nj[len(s),j] = 16
    else:
        w_nj[len(s),j] = 1


w_nj


# ## Additional Constraints for Q_ij and Q_nj variables

# In[20]:


m.addConstrs(2*q_ij[i,j] <= x[i,j] + x[i+1,j-1] for i in range(1,len(s)-2) for j in range(i+3,len(s)+1))


# In[21]:


m.addConstrs(2*q_nj[len(s),j] <= x[j,len(s)] + x[1,j-1] for j in range(3,len(s)))


# ## Q_i,i+1

# In[22]:


ls_ii1tup = []
for i in range(1,len(s)):
    ls_ii1tup.append((i,i+1))

m.addVars(ls_ii1tup,name='Q_ij',vtype=GRB.BINARY)
for i in range(1,len(s)):
    q_ij[i,i+1] = 0

q_ij


# ## Q_i,i+2

# In[23]:


ls_ii2tup = []
for i in range(1,len(s)-1):
    ls_ii2tup.append((i,i+2))

m.addVars(ls_ii2tup,name='Q_ij',vtype=GRB.BINARY)
for i in range(1,len(s)-1):
    q_ij[i,i+2] = 0

q_ij


# ## Q_n,n-1

# In[24]:


q_nj[len(s),len(s)-1] = 0


# ## Q_n,n-2

# In[25]:


q_nj[len(s),len(s)-2] = 0


# ## Non-Crossing Constraint

# In[26]:


m.addConstrs(quicksum(x[k,l] for k in range(i+1,j) for l in [i for i in list(range(1,len(s)+1)) if i >= j]) <= (10**6)*(1-x[i,j]) for i in range(1,len(s)+1) for j in range(i+1,len(s)+1))


# ## Character in At most one pair

# In[27]:


m.addConstrs(quicksum([x[i,k] for i in range(1,k)]) + quicksum([x[k,j] for j in list(range(k+1,len(s)+1))]) <= 1 for k in ONE_N)


# # Objective

# In[28]:


m.setObjective((quicksum(f[i,j]*x[i,j] for i in ONE_N for j in list(range(i+1,len(s)+1)))) + 
               (quicksum(w_ij[i,j] * q_ij[i,j] for i in range(1,len(s)-2) for j in range(i+3,len(s)+1)) + 
               (quicksum(w_nj[len(s),j] * q_nj[len(s),j] for j in range(3,len(s))))),GRB.MAXIMIZE)


# In[29]:


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
        if (v.x == 1)
            print("%s = %g" % (v.varName, v.x))
    print("Optimal objective value:\n{}".format(m.objVal))
    print("Runtime is:", m.Runtime)


# In[30]:


m.write("check.lp")

