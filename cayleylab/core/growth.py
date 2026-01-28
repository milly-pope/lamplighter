# Growth analysis for Cayley graphs
# For exact groups: compute exact ω
# For others: investigate convergence or estimate at chosen radius

from .bfs import build_ball
import math


def classify_growth(omega, poly_deg=None):
    """Classify growth type based on omega"""
    if omega is None:
        return "unknown"
    
    if abs(omega - 1.0) < 0.01:
        if poly_deg:
            return f"polynomial (degree ≈ {poly_deg:.1f})"
        return "polynomial"
    elif omega > 1.0:
        return f"exponential (ω = {omega:.4f})"
    else:
        return f"subexponential (ω = {omega:.4f})"


def exact_free_group(rank):
    omega = 2 * rank - 1
    return omega, f"Free group F_{rank}: ω = 2r-1 = {omega}"

def exact_integers(dim):
    return 1.0, f"ℤ^{dim}: polynomial growth (ω = 1, degree {dim})"

def exact_dihedral_inf():
    return 1.0, "D∞: same as ℤ, polynomial growth (ω = 1)"

def spectral_radius(matrix):
    n = len(matrix)
    v = [1.0] * n
    for _ in range(100):
        w = [sum(matrix[i][j] * v[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(x*x for x in w))
        if norm < 1e-12:
            return 0.0
        v = [x/norm for x in w]
    return norm

def exact_automaton(matrix):
    omega = spectral_radius(matrix)
    return omega, f"Automaton: ω = spectral_radius(M) ≈ {omega:.6f}"

def detect_exact_method(group):
    name = group.name.lower()
    
    if "free" in name or name.startswith("f_"):
        if hasattr(group, 'rank'):
            return ("free", group.rank)
        if "_" in name:
            try:
                rank = int(name.split("_")[1].split()[0])
                return ("free", rank)
            except:
                pass
    
    if name == "z^2" or name == "z2":
        return ("Zd", 2)
    
    if name == "d∞" or name == "dinf":
        return ("Dinf", None)
    
    return (None, None)


def analyze_growth(group, gens, radius, mode="auto", exact_kind=None, exact_param=None, 
                   automaton_matrix=None, estimate_r=None):
    """
    Analyze growth for a group.
    
    Modes:
    - "auto": Try exact method if available, else investigative
    - "exact": Use exact formula (F_r, Z^d, D∞, automaton)
    - "investigate": Show full root sequence for user to examine
    - "estimate": Use σ_r^(1/r) at user-specified r as ω estimate
    """
    # Compute σ_r and b_r up to radius N
    sigma_list = []
    b_list = []
    
    for r in range(radius + 1):
        V, E, dist, labels, words = build_ball(group, gens, r)
        b_list.append(len(V))
        sigma_list.append(sum(1 for d in dist if d == r))
    
    # Compute r-th roots σ_r^(1/r)
    roots = []
    for r in range(1, len(sigma_list)):
        if sigma_list[r] > 0:
            roots.append(sigma_list[r] ** (1.0/r))
    
    # Try exact method if mode allows
    omega_exact = None
    exact_source = None
    
    if mode == "auto":
        kind, param = detect_exact_method(group)
        if kind:
            exact_kind = kind
            exact_param = param
    
    if mode == "exact" or (mode == "auto" and exact_kind):
        if exact_kind == "free":
            omega_exact, exact_source = exact_free_group(exact_param or 2)
        elif exact_kind == "Zd":
            omega_exact, exact_source = exact_integers(exact_param or 2)
        elif exact_kind == "Dinf":
            omega_exact, exact_source = exact_dihedral_inf()
        elif exact_kind == "automaton" and automaton_matrix:
            omega_exact, exact_source = exact_automaton(automaton_matrix)
    
    # Estimate mode: use specified radius
    omega_est = None
    est_source = None
    if mode == "estimate":
        if estimate_r is None:
            estimate_r = radius
        if estimate_r > 0 and estimate_r <= len(roots):
            omega_est = roots[estimate_r - 1]
            est_source = f"σ_{estimate_r}^(1/{estimate_r})"
    
    # Polynomial degree estimate for ω = 1
    poly_deg = None
    omega_val = omega_exact if omega_exact else omega_est
    if omega_val and abs(omega_val - 1.0) < 0.01 and radius >= 4:
        log_pairs = [(math.log(r), math.log(b_list[r])) 
                     for r in range(max(2, radius-3), radius+1) if b_list[r] > 0]
        if len(log_pairs) >= 3:
            n = len(log_pairs)
            sx = sum(x for x,y in log_pairs)
            sy = sum(y for x,y in log_pairs)
            sxx = sum(x*x for x,y in log_pairs)
            sxy = sum(x*y for x,y in log_pairs)
            denom = n*sxx - sx*sx
            if abs(denom) > 1e-10:
                poly_deg = (n*sxy - sx*sy) / denom
    
    # Package result
    if omega_exact:
        omega_result = {
            "value": omega_exact, 
            "kind": "exact", 
            "source": exact_source,
            "classification": classify_growth(omega_exact, poly_deg)
        }
    elif omega_est:
        omega_result = {
            "value": omega_est,
            "kind": "estimate",
            "source": est_source,
            "classification": classify_growth(omega_est, poly_deg)
        }
    else:
        omega_result = {
            "value": None, 
            "kind": "investigative", 
            "source": "examine convergence of σ_r^(1/r) sequence",
            "classification": "investigate"
        }
    
    return {
        "sigma": sigma_list,
        "b": b_list,
        "omega": omega_result,
        "roots": roots,
        "poly_degree": poly_deg,
        "mode": mode
    }


def plot_convergence(roots, omega_exact=None):
    """Plot convergence of r-th roots"""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available for plotting")
        return
    
    r_values = list(range(1, len(roots) + 1))
    
    plt.figure(figsize=(10, 6))
    plt.plot(r_values, roots, 'b.-', label='σ_r^(1/r)', markersize=8)
    
    if omega_exact:
        plt.axhline(y=omega_exact, color='r', linestyle='--', label=f'ω (exact) = {omega_exact:.4f}')
    
    plt.xlabel('radius r', fontsize=12)
    plt.ylabel('σ_r^(1/r)', fontsize=12)
    plt.title('Convergence of r-th roots to growth exponent ω', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()


def format_growth_table(result, show_plot=False):
    sigma = result["sigma"]
    b = result["b"]
    omega_info = result["omega"]
    roots = result["roots"]
    poly_deg = result["poly_degree"]
    mode = result.get("mode", "auto")
    
    lines = []
    lines.append("\nGrowth Analysis:")
    lines.append("=" * 60)
    lines.append(f"{'r':<5} {'σ_r':<12} {'b_r':<12} {'σ_r^(1/r)':<15}")
    lines.append("-" * 60)
    
    for r in range(len(sigma)):
        root_str = f"{roots[r-1]:.6f}" if r > 0 and r-1 < len(roots) else "-"
        lines.append(f"{r:<5} {sigma[r]:<12} {b[r]:<12} {root_str:<15}")
    
    lines.append("=" * 60)
    lines.append("")
    
    if omega_info["kind"] == "exact":
        lines.append(f"Growth: {omega_info['classification']}")
        lines.append(f"  ω = {omega_info['value']:.6f} (exact)")
        lines.append(f"  {omega_info['source']}")
    elif omega_info["kind"] == "estimate":
        lines.append(f"Growth: {omega_info['classification']}")
        lines.append(f"  ω ≈ {omega_info['value']:.6f} (estimated at r={result['sigma'].index(max([s for i,s in enumerate(result['sigma']) if i > 0 and i <= len(roots) and abs(roots[i-1] - omega_info['value']) < 0.0001], default=0))})")
        lines.append(f"  Source: {omega_info['source']}")
    else:
        lines.append("Growth: investigative mode")
        lines.append(f"  Examine the σ_r^(1/r) sequence above.")
        lines.append(f"  Values: {' → '.join(f'{r:.3f}' for r in roots[-5:])}")
        if show_plot:
            lines.append(f"  Plotting convergence graph...")
    
    output = "\n".join(lines)
    
    # Show plot if requested and in investigate mode
    if show_plot and omega_info["kind"] == "investigative":
        plot_convergence(roots)
    elif show_plot and omega_info["kind"] == "exact":
        plot_convergence(roots, omega_info["value"])
    
    return output
