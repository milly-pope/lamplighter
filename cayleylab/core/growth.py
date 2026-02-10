# Growth analysis for Cayley graphs

from .bfs import build_ball
import math


def format_series(coeffs):
    # Turn list of coefficients into polynomial string
    terms = []
    for r, c in enumerate(coeffs):
        if c == 0:
            continue
        if r == 0:
            terms.append(str(c))
        elif r == 1:
            terms.append(f"{c} z" if c > 1 else "z")
        else:
            terms.append(f"{c} z^{r}" if c > 1 else f"z^{r}")
    return " + ".join(terms) if terms else "0"


def estimate_asymptote(roots, tail_length=10):
    """
    Estimate ω by fitting σ_r^(1/r) = ω + A/r to the last tail_length values.
    Uses linear regression with y = σ_r^(1/r), x = 1/r.
    Returns (omega_estimate, A_coefficient) or None if insufficient data.
    """
    if len(roots) < tail_length:
        return None
    
    # Use last tail_length values
    tail_start = len(roots) - tail_length
    y_vals = roots[tail_start:]
    r_vals = list(range(tail_start + 1, len(roots) + 1))  # r values (1-indexed)
    x_vals = [1.0/r for r in r_vals]  # x = 1/r
    
    # Linear regression: y = ω + A·x
    n = len(x_vals)
    sum_x = sum(x_vals)
    sum_y = sum(y_vals)
    sum_xx = sum(x*x for x in x_vals)
    sum_xy = sum(x*y for x, y in zip(x_vals, y_vals))
    
    # Solve for slope A and intercept ω
    denom = n * sum_xx - sum_x * sum_x
    if abs(denom) < 1e-10:
        return None
    
    A = (n * sum_xy - sum_x * sum_y) / denom
    omega = (sum_y - A * sum_x) / n
    
    return (omega, A)


def classify_growth(omega, poly_deg=None):
    """
    Classify growth type based on ω and polynomial degree.
    
    Per dissertation Definition 6.1:
    - exponential growth if ω > 1
    - subexponential growth if ω = 1
      - polynomial growth if β(k) ≼ k^d for some d
      - intermediate growth otherwise
    """
    if omega is None:
        return "unknown"
    
    if omega > 1.0 + 0.01:
        return "exponential"
    elif abs(omega - 1.0) < 0.01:
        # Subexponential: ω = 1
        if poly_deg is not None:
            return f"polynomial (degree ≈ {poly_deg:.1f})"
        else:
            return "subexponential (possibly intermediate)"
    else:
        # ω < 1 shouldn't happen mathematically, but handle gracefully
        return f"anomalous (ω = {omega:.4f})"


def exact_free_group(rank):
    omega = 2 * rank - 1
    return omega, f"Free group F_{rank}: ω = 2r-1 = {omega}"

def exact_integers(dim):
    return 1.0, f"ℤ^{dim}: polynomial growth (ω = 1, degree {dim})"

def exact_dihedral_inf():
    return 1.0, "D∞: same as ℤ, polynomial growth (ω = 1)"

def exact_Z_offsets():
    return 1.0, "ℤ with offsets: polynomial growth (ω = 1, degree 1)"

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
    
    if name == "z" and hasattr(group, 'offsets'):
        return ("Z_offsets", None)
    
    return (None, None)


def analyze_growth(group, gens, radius, mode="auto", exact_kind=None, exact_param=None, 
                   automaton_matrix=None, estimate_r=None, show_series=False):
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
        elif exact_kind == "Z_offsets":
            omega_exact, exact_source = exact_Z_offsets()
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
    
    # Asymptotic estimate from tail fitting (for investigative/auto modes)
    asymptote = None
    if len(roots) >= 10 and (mode == "investigate" or mode == "auto"):
        fit_result = estimate_asymptote(roots)
        if fit_result:
            asymptote = {"omega": fit_result[0], "A": fit_result[1]}
    
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
    
    result = {
        "sigma": sigma_list,
        "b": b_list,
        "omega": omega_result,
        "roots": roots,
        "poly_degree": poly_deg,
        "mode": mode,
        "asymptote": asymptote
    }
    
    # Add series if requested
    if show_series:
        result["S_series"] = format_series(sigma_list)
        result["B_series"] = format_series(b_list)
        # Check identity: b_r should equal sum of sigma up to r
        identity_ok = all(b_list[r] == sum(sigma_list[:r+1]) for r in range(len(b_list)))
        result["series_identity_ok"] = identity_ok
    
    return result


def plot_convergence(roots, omega_exact=None, asymptote=None):
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
    
    if asymptote:
        omega_est = asymptote["omega"]
        plt.axhline(y=omega_est, color='orange', linestyle=':', linewidth=2, 
                   label=f'ω (asymptote fit) ≈ {omega_est:.4f}')
    
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
    asymptote = result.get("asymptote")
    poly_deg = result["poly_degree"]
    
    lines = []
    lines.append("\nGrowth Analysis:")
    lines.append("=" * 60)
    lines.append(f"{'r':<5} {'σ_r':<12} {'b_r':<12} {'σ_r^(1/r)':<15}")
    lines.append("-" * 60)
    
    for r in range(len(sigma)):
        root_str = f"{roots[r-1]:.6f}" if r > 0 and r-1 < len(roots) else "-"
        lines.append(f"{r:<5} {sigma[r]:<12} {b[r]:<12} {root_str:<15}")
    
    lines.append("=" * 60)
    
    # Series if included
    if "S_series" in result:
        lines.append("")
        lines.append(f"S(z) = {result['S_series']}")
        lines.append(f"B(z) = {result['B_series']}")
        check = "OK" if result.get("series_identity_ok") else "FAILED"
        lines.append(f"Check B(z) = S(z)/(1-z): {check}")
    
    lines.append("")
    
    if omega_info["kind"] == "exact":
        lines.append(f"Growth: {omega_info['classification']}")
        lines.append(f"  ω = {omega_info['value']:.6f} (exact)")
        lines.append(f"  {omega_info['source']}")
    elif omega_info["kind"] == "estimate":
        lines.append(f"Growth: {omega_info['classification']}")
        lines.append(f"  ω ≈ {omega_info['value']:.6f}")
        lines.append(f"  Source: {omega_info['source']}")
    else:
        lines.append("Growth: investigative mode")
        lines.append(f"  Examine the σ_r^(1/r) sequence above.")
        lines.append(f"  Values: {' → '.join(f'{r:.3f}' for r in roots[-5:])}")
        if asymptote:
            lines.append(f"  Asymptotic estimate: ω ≈ {asymptote['omega']:.6f} (fit to tail)")
        if show_plot:
            lines.append(f"  Plotting convergence graph...")
    
    output = "\n".join(lines)
    
    # Show plot if requested and in investigate mode
    if show_plot and omega_info["kind"] == "investigative":
        plot_convergence(roots, asymptote=asymptote)
    elif show_plot and omega_info["kind"] == "exact":
        plot_convergence(roots, omega_info["value"])
    
    return output
