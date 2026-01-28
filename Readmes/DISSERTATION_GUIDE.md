# Dissertation Writing Guide

## Introduction - How to Frame Your Project

### The Mathematical Focus

Your dissertation is about **exploring geometric group theory through computation**. The software is a tool you built to investigate mathematical questions, not the main focus itself.

**Frame it like this:**
- Primary goal: Study growth rates, dead-end elements, and metric properties of Cayley graphs
- The tool: A computational system you developed to make this exploration feasible
- The mathematics: Wreath products, lamplighter groups, word metrics, growth functions

### Suggested Introduction Paragraph

"This dissertation explores metric and combinatorial properties of Cayley graphs for several infinite groups, with particular focus on wreath products and the lamplighter group. To facilitate this investigation, I developed a computational tool that constructs Cayley graphs via breadth-first search and analyzes their growth rates and dead-end elements. Using this system, I investigated conjectures about polynomial vs exponential growth, examined the structure of dead-ends in Z/2 ≀ Z, and explored how generator choices affect graph geometry."

### One-Sentence Summary Options

- "A computational exploration of growth rates and dead-end elements in wreath product Cayley graphs"
- "Investigating metric properties of lamplighter and wreath product groups through algorithmic construction"
- "Computer-assisted analysis of Cayley graphs for infinite groups"

## What to Include in Your Writeup

### Chapter 1: Background Mathematics
- Cayley graph definition and basic properties
- Word metric and balls B_R
- Growth functions: polynomial vs exponential
- Dead-end elements (definition from Cleary-Taback)
- Wreath products C ≀ D construction
- Examples: Z², lamplighter L₂ = Z/2 ≀ Z

### Chapter 2: The Computational Tool
**Keep this brief (2-3 pages) - you're explaining your methodology, not teaching programming**

What to cover:
- **Purpose**: "To study these groups computationally, I built a system that constructs Cayley graphs and analyzes their properties"
- **Core idea**: BFS from identity element up to radius R
- **Groups implemented**: Z², D∞, F₂, lamplighter, general wreath products
- **Key features**: Build balls, export visualizations, compute growth, find dead-ends
- **Why this design**: Unified algorithm works for any group by abstracting operations

What NOT to include:
- Detailed code listings
- Implementation of hash tables or data structures  
- Type systems or software engineering patterns
- Step-by-step algorithm pseudocode (cite BFS as standard)

### Chapter 3: Mathematical Investigations

**This is your main content - what you discovered using the tool**

Structure by mathematical question:

#### 3.1 Growth Rate Classification
- Computed |B_R| for various groups and radii
- Compared Z² (polynomial, degree 2) vs lamplighter (exponential, base ≈2.5)
- Tables showing ball sizes up to R=10
- Ratio analysis: |B_{R+1}|/|B_R| behavior

#### 3.2 Dead-End Elements
- Definition and mathematical significance
- Finding dead-ends at specific radii
- The canonical R=7 dead-end in lamplighter
- Escape depths and witness words
- Comparison across different wreath products

#### 3.3 Generator Dependence
- How generator choice affects graph structure
- Different generating sets for same group
- Impact on growth constants and dead-end distribution

### Chapter 4: Results and Analysis

Present your findings:
- Tables of computed values
- Cayley graph visualizations (exported PNGs)
- Growth function plots
- Specific examples with mathematical interpretation

### Chapter 5: Conclusions

- What you learned about these groups
- Which conjectures were confirmed/refuted
- Limitations of computational approach
- Future mathematical questions to explore

## Bullet Points for System Description

**When describing your computational tool (Chapter 2), include:**

✓ **System Purpose**
- Built to explore Cayley graphs algorithmically
- Enables study of groups that are difficult to analyze by hand
- Allows systematic investigation of balls at various radii

✓ **Mathematical Foundations**
- Uses standard BFS algorithm starting from identity
- Constructs ball B_R = {g ∈ G : |g| ≤ R}
- States represent group elements, edges represent generator multiplication

✓ **Groups Supported**
- Integer lattices (Z, Z²)
- Free groups (F₂)
- Infinite dihedral group (D∞)
- Lamplighter group (Z/2 ≀ Z)
- General wreath products (C ≀ D for various C, D)

✓ **Analysis Capabilities**
- Compute growth functions (sphere and ball sizes)
- Export visualizations for small radii
- Detect dead-end elements on spheres
- Evaluate words to find reduced forms

✓ **Design Rationale** (brief!)
- Single BFS algorithm works for all groups
- Each group provides identity and generator operations
- Python implementation for clarity and rapid development

✓ **Validation**
- Verified against hand calculations for small examples
- Matches known theoretical results (e.g., lamplighter growth rate)
- Reproduces published dead-end examples

## What to Emphasize vs What to Minimize

### EMPHASIZE (Mathematical Content):
- Growth rate phenomena you observed
- Specific dead-end structures you found
- Comparisons between different groups
- Connection to theoretical results in literature
- Mathematical insights gained from computation

### MINIMIZE (Implementation Details):
- Programming language choice
- Data structure implementations
- Code organization patterns
- Software engineering practices
- User interface design

## Example: How to Present a Result

**Good (Mathematics-focused):**

"For the lamplighter group L₂ = Z/2 ≀ Z with standard generators {t, T, a}, I computed balls up to radius R=10. The ball sizes exhibit exponential growth with ratio converging to approximately 2.5, confirming the known growth rate. At radius R=7, the system identified one dead-end element: the state with head at position 0 and lamps lit at positions {-1, 0, 1}. This element requires 3 steps to escape the ball, achieved by the word 'ttt' (moving the head right three times)."

**Not as good (Tool-focused):**

"I implemented a BFS algorithm in Python that builds Cayley graphs. The program uses hash tables to store visited states and a queue for exploration. After running the lamplighter with radius 10, the output showed exponential growth. The dead-end detection feature found one element at distance 7."

## Writing Style Tips

### Keep it Mathematical
- Use proper notation: |B_R|, S_R, ≀, Z/2
- Define terms: "Let G = ⟨S⟩ be a finitely generated group..."
- State results: "Theorem 3.1 predicts... Our computation confirms..."
- Reference literature: "Following Cleary-Taback [CT05], we define..."

### Treat Computation as Evidence
- "Computation reveals that..."
- "The data suggests..."
- "For R ≤ 10, we observe..."
- "This confirms the theoretical prediction..."

### Be Precise About Limitations
- "Computed for R ≤ 10 due to exponential growth"
- "These examples support but do not prove..."
- "Further investigation would require..."

## Mathematical Background (Chapter 1)

### Cayley Graphs
- Definition: Given group G and generator set S, vertices are group elements, edges are right multiplication by generators
- Word metric: d(g, h) = length of shortest word in S relating g to h
- Ball notation: B_R = {g ∈ G : |g| ≤ R}

### Groups Implemented
- **Z²**: Integer lattice, polynomial growth ~R²
- **D∞**: Infinite dihedral group
- **F_2**: Free group on 2 generators, exponential growth
- **Z/2 ≀ Z**: Lamplighter group, exponential growth ~2.5^R
- **C ≀ D**: General wreath products with configurable base and top

### Growth Rates
- **Polynomial**: |B_R| ~ R^d for some d (e.g., Z², Z³)
- **Exponential**: |B_R| ~ c^R for some c > 1 (e.g., F_2, lamplighter)
- **Classification**: Compare ratios |B_{R+1}|/|B_R| as R → ∞

### Dead-End Elements
- **Definition**: g at distance R is a dead-end if ∀s ∈ S: |g·s| ≤ R
- **Depth**: Minimum k ≥ 1 such that some word of length k moves beyond B_R
- **Example**: In Z/2 ≀ Z at radius 7, the state with three consecutive lamps lit has depth 3

## High-Level System Architecture (For Brief Technical Section)

**Keep this to ~1 page maximum in your dissertation**

### The Core Idea

The system builds Cayley graphs using breadth-first search from the identity element. Rather than writing separate algorithms for each group, I designed a unified approach: each group provides an identity element and a set of generators, and the same BFS works for all of them.

**Key abstraction**: A "group" just needs to provide:
- `identity()` - starting point
- `default_generators()` - edges to explore
- `pretty(state)` - readable representation

Each generator provides:
- `apply(state)` - how to move from one element to another

With this minimal interface, one BFS algorithm handles Z², free groups, lamplighter, and wreath products identically.

### State Representation

Each group represents elements canonically:
- **Z²**: tuple (x, y)
- **Lamplighter**: (head_position, lamp_configuration)
  - Lamps stored sparsely as sorted tuple of (position, value) pairs
  - Only non-zero entries stored
- **Wreath products**: (position_in_top_group, tape)
  - Generalizes lamplighter to arbitrary C ≀ D

Canonical forms ensure the same group element always has the same representation, preventing duplicate vertices in the graph.

### What the System Does

1. **Build balls**: Construct B_R by exploring all elements within R steps
2. **Compute growth**: Record |S_r| and |B_r| for r = 0, 1, ..., R
3. **Find dead-ends**: Identify elements where all generator moves don't increase distance
4. **Export graphs**: Generate visualizations for small radii (R ≤ 8 typically)

### Implementation Scope

**What I implemented:**
- BFS algorithm for generic groups (60 lines)
- Six group implementations (Z², D∞, F₂, lamplighter, lamplighter over Z², general wreath products)
- Growth rate analysis
- Dead-end detection algorithm
- Export to DOT/PNG via Graphviz

**What I used from libraries:**
- Python standard collections (deque, dict)
- Graphviz for visualization
- Basic matplotlib for plotting

Total: ~1500 lines of Python across all files

## Technical Details (For Appendix or Omit Entirely)

**Only include if you have space or examiner specifically wants implementation details**

## Sample System Description (Copy/Adapt for Your Dissertation)

**This is what a ~1 page technical section might look like:**

---

### 2.3 Computational Tools

To investigate these properties systematically, I developed a computational system for constructing and analyzing Cayley graphs. The tool implements breadth-first search from the identity element to build balls B_R for specified radius R, then analyzes their growth and structure.

**Groups implemented:** The system supports Z², the infinite dihedral group D∞, the free group F₂, the standard lamplighter group Z/2 ≀ Z, and general wreath products C ≀ D where both C and D can be chosen from Z, Z/n, Z², D∞, Dn(n), or Free(k).

**Core algorithm:** Starting from the identity e, BFS explores all elements reachable in at most R steps by repeatedly applying generators. Each group provides its identity element and generator operations; a single BFS implementation works for all groups by calling these operations abstractly. States are represented canonically (e.g., for lamplighter: head position plus sorted list of lit lamps) to ensure unique representation of each group element.

**Analysis capabilities:** The system computes |S_r| and |B_r| for r = 0, 1, ..., R, allowing growth rate classification. It identifies dead-end elements—those at distance R where no single generator move increases distance—and computes their escape depth. For visualization, it exports Cayley graphs as DOT files rendered via Graphviz.

**Validation:** I verified the implementation against hand calculations for Z² balls up to R=4 and confirmed the lamplighter growth rate matches theoretical predictions (~2.5^R). The detected dead-end at radius 7 in the lamplighter matches the example from Cleary and Taback [CT05].

Using this tool, I investigated the following questions...

---

**That's it! Keep it concise and mathematical, then move on to your actual results.**

### Growth Rate Examples

**Z²**: |B_R| is polynomial
- R=5: 41 vertices (ratio ~1.19)
- R=10: 161 vertices (ratio ~1.09)
- Ratios converge to 1 → polynomial

**Lamplighter**: |B_R| is exponential
- R=5: 83 vertices (ratio ~2.7)
- R=7: 569 vertices (ratio ~2.6)
- Ratios stay > 2 → exponential

**Classification**: Compare |B_{R+1}|/|B_R| → if stabilizes near 1, polynomial; if > 1, exponential

### Dead-End Examples

**Lamplighter at R=7**:
- Sphere has 123 elements
- Found 1 dead-end: state = (0, {-1:1, 0:1, 1:1}) (three lamps lit, head centered)
- Depth = 3 (witness: `t t t`)
- Matches theoretical prediction from Cleary-Taback

**Finite groups** (e.g., Z/2 ≀ Z/5):
- May or may not have dead-ends depending on radius
- Good test case for algorithm correctness

## Testing and Validation (Chapter 4)

### Manual Verification

**Small cases by hand**:
- Z² ball of radius 2 should have 13 vertices (draw diamond)
- D∞ ball with r, s generators at radius 3 should have specific structure
- Free group F_2 at radius 2 → count words of length ≤ 2

**Known results**:
- Lamplighter growth rate ~2.46 (check against literature)
- Dead-end at R=7 in lamplighter (check state matches description)

### Code Testing

**Approach**: Direct testing via interactive UI
- Run various configurations
- Check output visually (PNG graphs)
- Compare ball sizes to hand calculations for small R

**No formal test suite**: Code simplified to student level, no test framework

## Future Extensions (Chapter 5)

**Additional groups**:
- Heisenberg group
- SL(2, Z)
- Braid groups

**Optimization**:
- For very large balls, use better hash tables or databases
- Parallel BFS for multicore systems
- C extension for critical loops

**Visualization**:
- 3D rendering for Z³
- Interactive web-based graph viewer
- Animation of BFS progress

**Analysis**:
- Automated growth function fitting
- Geodesic counting
- Metric balls vs combinatorial balls

## Writing Tips

### Structure Suggestion

1. **Introduction**: Cayley graphs, motivation, goals
2. **Background**: Groups, Cayley graphs, growth, dead-ends (with examples)
3. **Design**: Architecture decisions, state representations, BFS algorithm
4. **Implementation**: Code structure, key algorithms, wreath products
5. **Results**: Growth experiments, dead-end analysis, validation
6. **Conclusion**: Summary, what worked, future work

### Mathematical Rigor

**Balance formalism and accessibility**:
- Define groups, generators, Cayley graphs formally
- Give intuitive explanations alongside formal definitions
- Use examples liberally (Z, Z², F_2 before lamplighter)

**Proofs**:
- Don't need to prove BFS correctness (standard algorithm)
- DO explain why canonicalization ensures correctness
- Cite papers for growth rate and dead-end theory

### Code Presentation

**Show snippets, not everything**:
- Include key parts of BFS algorithm
- Show one example group implementation (e.g., Z²)
- Abstract details to appendix or say "see codebase"

**Explain design rationale**:
- Why duck typing vs formal interfaces?
- Why tuples vs classes for states?
- Why dict vs other data structures?

### Results Presentation

**Tables**:
- Growth rates for different groups
- Ball sizes at various radii
- Dead-end counts per radius

**Graphs**:
- Visual Cayley graphs (PNG exports)
- Growth functions plotted (|B_R| vs R)
- Ratio plots to show polynomial vs exponential

**Examples**:
- Show actual dead-end states with pretty printing
- Include witness words for escapes
- Demonstrate different generator sets

## Common Questions (FAQ)

**Q: Why Python instead of C/C++?**

A: Simplicity and expressiveness. Python dicts provide fast hashing out of the box. For balls with <100k vertices (typical for student projects), speed is not limiting factor. Premature optimization would complicate code without benefit.

**Q: Why no type hints?**

A: Student-level code. Type hints are professional software engineering practice, but add verbosity. For a research project at this scale, simple comments suffice.

**Q: How do you know your BFS is correct?**

A: Test on known cases (Z², small examples verified by hand), check against literature values (lamplighter growth rate), ensure state canonicalization prevents revisits.

**Q: What if two states hash to same value?**

A: Python's default hash for tuples is collision-resistant for practical sizes. Would need billions of states before collisions become likely. Can verify by checking `len(visited) == len(set(visited.keys()))` if concerned.

**Q: Why not use graph libraries like NetworkX?**

A: We do use them for visualization (export.py). But for construction, BFS with custom state types is simpler - NetworkX nodes would need to store states anyway, adding indirection.

## Key References

- **Cayley graphs**: Standard textbook (e.g., Rotman "Theory of Groups")
- **Growth rates**: Gromov, "Groups of polynomial growth"
- **Lamplighter**: Cleary-Taback papers on dead-ends in lamplighter groups
- **Wreath products**: Standard construction in group theory texts

---

**Good luck with your dissertation!** Remember: explain design choices clearly, validate results carefully, and don't forget to discuss what you learned from implementation challenges.
