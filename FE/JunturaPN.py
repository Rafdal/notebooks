import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

class JunturaPN():
    # Symbolic variables and constants
    NA, ND, q, er, e0 = sp.symbols('N_{{A}} N_{{D}} q \\varepsilon_{{r}} \\varepsilon_{{0}}', positive=True, real=True)
    k, T, ni = sp.symbols('k T n_{{i}}', positive=True, real=True)
    x = sp.symbols('x', real=True)
    xp, xn = sp.symbols('x_{{p}} x_{{n}}', positive=True, real=True)
    W = sp.symbols('W', positive=True, real=True)
    VT, Vbi, V = sp.symbols('V_{{T}} V_{{bi}} V', real=True)

    # Equations
    VT_eq = (k * T) / q
    V_bi_eq = VT * sp.ln((NA * ND) / (ni**2))
    xp_eq = sp.sqrt((2 * er * e0) * (Vbi - V) * (ND / (NA*(NA + ND))) / q)
    xn_eq = sp.sqrt((2 * er * e0) * (Vbi - V) * (NA / (ND*(NA + ND))) / q)
    xp_xn_eq = sp.Eq(NA * xp, ND * xn)
    W_eq = xn + xp
    ro_x_eq = sp.Piecewise(
        (-q*NA, (-xp <= x) & (x <= 0)),    # -xp < x < 0 
        (q * ND, (0 < x) & (x <= xn)),     # 0 < x < xn
        (0, True)                           # otherwise
    )
    # perform integration from 0 to x to get the other functions
    E_x_eq = (sp.integrate(ro_x_eq, (x, -xp, x)) / (er * e0)).simplify()
    v_x_eq = -sp.integrate(E_x_eq, x).simplify()

    # Constant values (NAMES referred to attributes of the class)
    const = {
        'k': 1.38e-23,
        'q': 1.6e-19,
        'e0': 8.85e-14
    }

    # Variables and necessary equations for the calculations
    # (NAMES referred to attributes of the class)
    var = {
        'T': [None, None, 'K'],
        'VT': [None, VT_eq, 'V'],
        'Vbi': [None, V_bi_eq, 'V'],
        'NA': [None, None, 'cm^{-3}'],
        'ND': [None, None, 'cm^{-3}'],
        'ni': [None, None, 'cm^{-3}'],
        'V': [None, None, 'V'],
        'xp': [None, xp_eq, 'cm'],
        'xn': [None, xn_eq, 'cm'],
        'W': [None, W_eq, 'cm'],
        'er': [None, None, ''],
    }

    fun = {
        'ro_x': [ro_x_eq, 'C/cm^3'],
        'E_x': [E_x_eq, 'V/cm'],
        'V_x': [v_x_eq, 'V']
    }

    # Symbolic functions
    ro_x = sp.Function('\\rho')(x)
    E_x = sp.Function('E')(x)
    V_x = sp.Function('V')(x)

    def function(self, key):
        if key in self.fun:
            return self.fun[key][0]
        else:
            print(f"No existe '{key}', opciones: {self.fun.keys()}")

    # Plot functions
    def plot(self, key, x=None):
        if x is None:
            x = np.linspace(-2*self['xp'], 2*self['xn'], 1000)
        
        if key in self.fun:
            fun_eq, unit = self.fun[key]
            # substitute free symbols
            for s in (fun_eq.free_symbols - {self.x}):
                s_val = self.symbol_to_value(s)
                fun_eq = fun_eq.subs(s, s_val)
            print("lambdify: ", fun_eq)
            fun = sp.lambdify(self.x, fun_eq, 'numpy')
            y = np.array([fun(xi) for xi in x])
            title = "$" + sp.latex(getattr(self, key)) + "$"
            ylabel = f'{title} [{unit}]'
            self.plot_fun(x, y, title, xlabel='x [cm]', ylabel=ylabel)
        else:
            print(f"No existe '{key}', opciones: {self.fun.keys()}")

    def plot_fun(self, x, y, title, xlabel, ylabel):
        plt.plot(x, y)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        # add X=0 and Y=0 lines
        plt.axvline(0, color='k', linestyle='-')
        plt.axhline(0, color='k', linestyle='-')
        plt.grid()
        plt.show()


    def print(self, key, decimals=None, eng=False):
        if isinstance(key, list):
            try:
                symbols = ""
                for k in key:
                    symbols += getattr(self, k).name + "\\,\\space\\space "
                display(sp.Symbol(symbols))
            except:
                pass
            for k in key:
                self.print_key(k, decimals, eng)
        elif isinstance(key, str):
            self.print_key(key, decimals, eng)
        else:
            raise ValueError(f"key debe ser un string o una lista de strings")

    def print_key(self, key, decimals=None, eng=False):
        try:
            val = self[key]
        except ValueError as e:
            print(e)
            return
        
        if decimals is None:
            if eng:
                str_val = f"{val:.2e}"
            else:
                str_val = f"{val}"
        else:
            if eng:
                str_val = f"{val:.{decimals}e}"
            else:
                str_val = f"{val:.{decimals}f}"

        print(key, "=", str_val, self.var[key][2])



    # Show all values
    def values(self):
        return {k: v[0] for k, v in self.var.items()}

    # Show undefined variables
    def undefined_values(self):
        return [k for k, v in self.var.items() if v[0] is None]

    # Constructor
    def __init__(self):
        pass

    def __setitem__(self, key, value):
        if key in self.var:
            self.var[key][0] = value
        else:
            raise ValueError(f"No existe '{key}' en {self.var}")

    def __getitem__(self, key): # key is a string
        if not key in self.var and not key in self.const:
            raise ValueError(f"No existe '{key}'")
        
        if key in self.const:
            return self.const[key]
        
        if key in self.var:

            val, val_eq, _ = self.var[key]

            if val is None and val_eq is None:
                raise ValueError(f"No se ha definido '{key}'")
            
            if val is None and val_eq is not None:
                # replace constants
                for ck, cv in self.const.items():
                    c_symbol = getattr(self, ck)
                    val_eq = val_eq.subs(c_symbol, cv)

                # look for undefined symbols
                for s in val_eq.free_symbols:
                    
                    # ACA
                    s_val = self.symbol_to_value(s)
                    val_eq = val_eq.subs(s, s_val)

                val = val_eq.evalf()         

            return float(val)
        

    def symbol_to_value(self, symbol):
        # get attribute name from symbol name
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, sp.Symbol) and attr.name == symbol.name:
                return self[attr_name]