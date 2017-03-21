"""
A generic Runge-Kutta type integrator for integrating CellCenterData2d.
We support a generic Butcher tableau for explicit the Runge-Kutta update


0   |
c_2 | a_21
c_3 | a_31 a_32
:   |  :        .
:   |  :          .
c_s | a_s1 a_s2 ... a_s,s-1
----+---------------------------
    | b_1  b_2  ... b_{s-1}  b_s


the update is

  y_{n+1} = y_n + dt sum_{i=1}^s {b_i k_i}

and the s increment is 

  k_s = f(t + c_s dt, y_n + dt (a_s1 k1 + a_s2 k2 + ... + a_s,s-1 k_{s-1})
"""

import numpy as np
import mesh.patch as patch

a = {}
b = {}
c = {}

# second-order
a[2] = np.array([[0.0, 0.0],
                 [0.5, 0.0]])

b[2] = np.array([0.0, 1.0])

c[2] = np.array([0.0, 0.5])

# fourth-order
a[4] = np.array([[0.0, 0.0, 0.0, 0.0],
                 [0.5, 0.0, 0.0, 0.0],
                 [0.0, 0.5, 0.0, 0.0],
                 [0.0, 0.0, 1.0, 0.0]])

b[4] = np.array([1./6., 1./3., 1./3., 1./6.])

c[4] = np.array([0.0, 0.5, 0.5, 1.0])



class RKIntegrator(object):

    def __init__(self, t, dt, order=2):
        self.s = order

        self.t = t
        self.dt = dt

        self.k = [None]*len(b[self.s])

        self.start = None

    def set_start(self, start):
        self.start = start

    def store_increment(self, n, k_stage):
        self.k[n] = k_stage

    def get_stage_start(self, istage):
        ytmp = patch.cell_center_data_clone(self.start)
        for n in range(ytmp.nvar):
            var = ytmp.get_var_by_index(n)
            for s in range(istage-1):
                var.v()[:,:] += self.dt*a[self.s][istage,s]*self.k[s].v(n=n)[:,:]
        return ytmp

    def get_stage_t(self, n):
        return self.t + c[self.s][n]*dt

    def compute_final_update(self):
        """this constructs the final t + dt update, overwriting the inital data"""
        ytmp = self.start
        for n in range(ytmp.nvar):
            var = ytmp.get_var_by_index(n)
            for s in range(self.s):
                var.v()[:,:] += self.dt*b[self.s][s]*self.k[s].v(n=n)[:,:]
            
        return ytmp

        
