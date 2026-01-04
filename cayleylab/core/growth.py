# Growth rate analysis for Cayley balls

from .bfs import build_ball


def compute_growth(group, gens, max_radius):
    # Compute ball sizes for radii 0..max_radius
    # Returns list of (radius, |V|, ratio) tuples
    results = []
    prev_size = 0
    
    for r in range(max_radius + 1):
        V, E, dist, labels, words = build_ball(group, gens, r)
        size = len(V)
        ratio = size / prev_size if prev_size > 0 else 0
        results.append((r, size, ratio))
        prev_size = size
    
    return results


def classify_growth(results):
    # Classify growth type based on ratios
    # Returns: ("polynomial", degree) or ("exponential", base) or ("unknown", None)
    if len(results) < 4:
        return ("unknown", None)
    
    # Check exponential: ratio should be roughly constant
    ratios = [r for _, _, r in results[2:] if r > 0]
    if len(ratios) >= 3:
        avg_ratio = sum(ratios) / len(ratios)
        variance = sum((r - avg_ratio) ** 2 for r in ratios) / len(ratios)
        if variance < 0.5 and avg_ratio > 1.5:
            return ("exponential", avg_ratio)
    
    # Check polynomial: log(size) ~ degree * log(r)
    # For polynomial growth, size ≈ c*r^d
    # Taking consecutive ratios: size(r+1)/size(r) ≈ ((r+1)/r)^d
    # This ratio decreases as r increases
    if len(results) >= 5:
        sizes = [s for _, s, _ in results[1:]]
        if all(sizes[i+1] > sizes[i] for i in range(len(sizes)-1)):
            # Check if ratios are decreasing (characteristic of polynomial)
            ratios = [sizes[i+1]/sizes[i] for i in range(len(sizes)-1)]
            if len(ratios) >= 3 and all(ratios[i+1] < ratios[i] + 0.1 for i in range(len(ratios)-1)):
                # Estimate degree from r=2,3
                if len(results) > 3:
                    r2_size = results[2][1]
                    r3_size = results[3][1]
                    # size ≈ c*r^d, so log(size) ≈ log(c) + d*log(r)
                    # d ≈ log(size(3)/size(2)) / log(3/2)
                    if r2_size > 1 and r3_size > r2_size:
                        import math
                        degree = math.log(r3_size / r2_size) / math.log(3 / 2)
                        return ("polynomial", round(degree, 1))
    
    return ("unknown", None)


def format_growth_table(results, growth_type):
    # Format growth results as a table string
    lines = []
    lines.append("\nGrowth Analysis:")
    lines.append("=" * 50)
    lines.append(f"{'Radius':<10} {'|V|':<15} {'Ratio':<15}")
    lines.append("-" * 50)
    
    for r, size, ratio in results:
        ratio_str = f"{ratio:.3f}" if ratio > 0 else "-"
        lines.append(f"{r:<10} {size:<15} {ratio_str:<15}")
    
    lines.append("=" * 50)
    
    # Add classification
    gtype, param = growth_type
    if gtype == "exponential":
        lines.append(f"Growth Type: Exponential (base ≈ {param:.2f})")
        lines.append(f"Expected: |B(r)| ≈ c · {param:.2f}^r")
    elif gtype == "polynomial":
        lines.append(f"Growth Type: Polynomial (degree ≈ {param})")
        lines.append(f"Expected: |B(r)| ≈ c · r^{param}")
    else:
        lines.append("Growth Type: Unknown (need more data)")
    
    return "\n".join(lines)
