from rich.style import Style

from tuitorial import Chapter, Focus, Step, TuitorialApp
from tuitorial.helpers import create_bullet_point_chapter

problem_statement, extras = zip(
    *[
        (
            "Scientists and engineers often work with complex simulation workflows.",
            "These workflows involve multiple steps, such as data preprocessing, model execution, and analysis.",
        ),
        (
            "Core logic is often encapsulated in functions that depend on each other.",
            "For example, [bold blue]calculate_fidelity(...)[/] might depend on the output of [bold blue]create_circuit(...)[/], which also depends on other inputs.",
        ),
        (
            "Managing complex computational workflows can be challenging.",
            "As the number of steps and dependencies increases, it becomes harder to keep track of the flow of data and ensure correct execution.",
        ),
        (
            "Keeping track of dependencies between functions requires a lot of bookkeeping.",
            "Manually managing inputs and outputs for each function can be error-prone and time-consuming.",
        ),
        (
            "Once you have a working pipeline, you may want to run it with different parameters.",
            "This usually involves writing boilerplate code with loops over the parameters, executing the functions, and collecting the results.",
        ),
        (
            "Running on laptop usually requires vastly different code than in parallel on a cluster.",
            "Adapting code for different execution environments often involves significant code duplication and platform-specific logic.",
        ),
        (
            "Reproducibility and maintainability are crucial in scientific computing.",
            "It's essential to be able to rerun experiments with the same results and easily update or extend the workflow.",
        ),
        (
            "Ideally, we focus on the science and not the plumbing.",
            "Scientists should spend more time on the problem and less time on writing execution details and boilerplate code.",
        ),
        (
            "What if we could automate the creation, execution, and management of function pipelines?",
            "Not wasting time on plumbing and gathering results!",
        ),
    ],
)


# Create a chapter for the problem statement using the helper function
problem_chapter = create_bullet_point_chapter(
    "Introduction",
    list(problem_statement),
    extras=list(extras),
    marker="1.",
    style=Style(color="bright_yellow", bold=True),
)

# Chapter 1: Introduction to pipefunc
intro_code = """
from pipefunc import pipefunc, Pipeline

@pipefunc(output_name="c")
def f(a, b):
    return a + b

@pipefunc(output_name="d")
def g(b, c, x=1):
    return b * c * x

pipeline = Pipeline([f, g])
result = pipeline("d", a=2, b=3)  # Returns 18
"""

intro_steps = [
    Step(
        "Welcome to pipefunc\nA Python library for creating and executing function pipelines",
        [Focus.range(0, 2, Style(color="bright_cyan", bold=True))],
    ),
    Step(
        "Creating Pipeline Functions\nUse @pipefunc decorator to specify output names",
        [
            Focus.regex(
                r"@pipefunc.*\n.*def.*\n.*return.*\n",
                Style(color="bright_yellow", bold=True),
            ),
        ],
    ),
    Step(
        "Building the Pipeline\nCombine functions into a Pipeline object",
        [Focus.regex(r"pipeline = Pipeline.*", Style(color="bright_green", bold=True))],
    ),
    Step(
        "Executing the Pipeline\nCall the pipeline with desired output and inputs",
        [Focus.regex(r"result = pipeline.*", Style(color="bright_magenta", bold=True))],
    ),
]

# Chapter 2: Core Concepts
concepts_code = """
# 1. Function Dependencies
@pipefunc(output_name="y")
def process(x):  # Input requirements automatically detected
    return x * 2

# 2. Automatic Execution Order
pipeline = Pipeline([f1, f2, f3])  # Order determined by dependencies

# 3. Type Validation
@pipefunc(output_name="result")
def compute(x: int) -> float:  # Type hints are validated
    return float(x * 2)

# 4. Resource Management
@pipefunc(output_name="data", resources={"memory": "1GB"})
def heavy_computation(x):
    return process_large_data(x)
"""

concepts_steps = [
    Step(
        "Function Dependencies\nInput requirements are automatically detected",
        [
            Focus.regex(
                r"# 1.*\n.*@pipefunc.*\n.*def process.*\n.*return.*",
                Style(color="bright_yellow", bold=True),
            ),
        ],
    ),
    Step(
        "Automatic Execution Order\nPipeline determines optimal execution sequence",
        [Focus.regex(r"# 2.*\n.*pipeline = Pipeline.*", Style(color="bright_green", bold=True))],
    ),
    Step(
        "Type Validation\nType hints are checked for compatibility",
        [
            Focus.regex(
                r"# 3.*\n.*@pipefunc.*\n.*def compute.*\n.*return.*",
                Style(color="bright_blue", bold=True),
            ),
        ],
    ),
    Step(
        "Resource Management\nSpecify resource requirements per function",
        [
            Focus.regex(
                r"# 4.*\n.*@pipefunc.*\n.*def heavy_computation.*\n.*return.*",
                Style(color="bright_magenta", bold=True),
            ),
        ],
    ),
]

# Create chapters and run the tutorial
chapters = [
    problem_chapter,
    Chapter("Introduction to pipefunc", intro_code, intro_steps),  # type: ignore[arg-type]
    Chapter("Core Concepts", concepts_code, concepts_steps),  # type: ignore[arg-type]
]

app = TuitorialApp(chapters)
app.run()
