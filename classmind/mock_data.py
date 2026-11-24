"""Demo Google Classroom: 3 courses, a semester of posts, slide decks and syllabus announcements.

Shape matches what classroom.sync() returns, so the pipeline cannot tell mock from real.
"""

COURSES = [
    {"id": "pdc", "name": "Parallel & Distributed Computing", "section": "CS-A", "teacher": "Dr. Ayesha Khan"},
    {"id": "genai", "name": "Generative AI", "section": "AI-B", "teacher": "Dr. Usman Tariq"},
    {"id": "se", "name": "Software Engineering", "section": "SE-A", "teacher": "Ms. Sara Malik"},
]


def _deck(*slides):
    return [{"slide": i + 1, "title": t, "text": b} for i, (t, b) in enumerate(slides)]


PDC_LECTURES = {
    1: ("Introduction to Parallel Computing", _deck(
        ("Why parallel computing?", "Single-core clock speeds stopped scaling around 2005 because of power and heat limits. Performance now comes from adding more cores, so software must be written to run in parallel."),
        ("Concurrency vs parallelism", "Concurrency is structuring a program as independent tasks. Parallelism is executing tasks at the same time on multiple processing units. A concurrent program may run on one core; a parallel one needs several."),
        ("Speedup and efficiency", "Speedup S = T_serial / T_parallel. Efficiency E = S / p where p is the number of processors. Ideal (linear) speedup is S = p."),
    )),
    2: ("Flynn's Taxonomy and Parallel Architectures", _deck(
        ("Flynn's taxonomy", "Flynn classifies computers by instruction and data streams: SISD (classic uniprocessor), SIMD (vector units, GPUs), MISD (rare, fault-tolerant systems) and MIMD (multicore CPUs, clusters)."),
        ("Shared vs distributed memory", "In shared memory all cores access one address space (UMA or NUMA). In distributed memory each node has private memory and nodes communicate by passing messages over a network."),
        ("Cache coherence", "When cores cache the same memory line, a coherence protocol such as MESI keeps the copies consistent. False sharing happens when independent variables share one cache line and cause needless invalidations."),
    )),
    3: ("Amdahl's Law and Gustafson's Law", _deck(
        ("Amdahl's law", "Amdahl's law bounds speedup when a fraction f of a program is serial: S(p) = 1 / (f + (1 - f) / p). As p grows, speedup approaches 1/f. With 10% serial code, maximum speedup is 10x no matter how many cores are added."),
        ("Amdahl's law example", "If 95% of a program is parallel and we use 8 cores: S = 1 / (0.05 + 0.95/8) = 5.93. Doubling to 16 cores only gives 9.14, showing diminishing returns."),
        ("Gustafson's law", "Gustafson's law assumes the problem size grows with the number of processors: S(p) = p - f(p - 1). It gives a more optimistic view of scaling for large workloads (weak scaling)."),
        ("Strong vs weak scaling", "Strong scaling keeps the total problem size fixed while adding processors (Amdahl). Weak scaling keeps the work per processor fixed (Gustafson)."),
    )),
    4: ("Parallel Algorithm Design", _deck(
        ("Foster's methodology", "Foster's PCAM design steps: Partitioning, Communication, Agglomeration and Mapping."),
        ("Decomposition techniques", "Data decomposition splits the data across tasks; task (functional) decomposition splits the work into different operations. Recursive decomposition is used for divide-and-conquer problems."),
        ("Load balancing", "Static load balancing assigns work before execution; dynamic load balancing (work stealing, task queues) reassigns work at run time to keep all processors busy."),
    )),
    5: ("Shared Memory Programming with OpenMP", _deck(
        ("OpenMP basics", "OpenMP uses compiler directives such as #pragma omp parallel to create a team of threads in a fork-join model."),
        ("Parallel for and scheduling", "#pragma omp parallel for splits loop iterations among threads. Schedules: static, dynamic and guided. Use reduction(+:sum) to combine partial results safely."),
        ("Race conditions", "A race condition occurs when threads access shared data and at least one writes without synchronisation. Fix with critical sections, atomics, or by making data private."),
    )),
    6: ("Distributed Memory Programming with MPI", _deck(
        ("MPI model", "MPI programs run as multiple processes, each with a rank in a communicator such as MPI_COMM_WORLD."),
        ("Point-to-point communication", "MPI_Send and MPI_Recv transfer messages between two ranks. Blocking calls can deadlock if both processes send first; non-blocking MPI_Isend/MPI_Irecv avoid this."),
        ("Collectives", "Collective operations involve all ranks: MPI_Bcast, MPI_Scatter, MPI_Gather, MPI_Reduce and MPI_Allreduce."),
    )),
}

GENAI_LECTURES = {
    1: ("Transformers and Attention", _deck(
        ("Self-attention", "Self-attention computes softmax(QK^T / sqrt(d_k)) V, letting every token attend to every other token in the sequence."),
        ("Transformer block", "A transformer block stacks multi-head attention, a feed-forward network, residual connections and layer normalisation."),
    )),
    2: ("Prompt Engineering", _deck(
        ("Prompting patterns", "Zero-shot, few-shot and chain-of-thought prompting. Clear instructions and examples improve output quality."),
        ("Structured output", "Ask the model for JSON that follows a schema so downstream code can parse the result reliably."),
    )),
    3: ("Retrieval-Augmented Generation", _deck(
        ("What is RAG?", "Retrieval-Augmented Generation retrieves relevant documents from a knowledge base and passes them to the LLM as context, grounding answers in sources and reducing hallucination."),
        ("Chunking and embeddings", "Documents are split into chunks, embedded into vectors and stored in a vector database. Hybrid search combines vector similarity with keyword (BM25) scores."),
        ("Evaluating RAG", "Measure retrieval hit rate at k, and answer faithfulness: the share of claims supported by the retrieved sources."),
    )),
}

SE_LECTURES = {
    1: ("Software Process Models", _deck(
        ("Waterfall vs Agile", "Waterfall runs phases in sequence; Agile delivers in short iterations with continuous feedback. Scrum uses sprints, a product backlog and daily stand-ups."),
    )),
    2: ("Requirements Engineering", _deck(
        ("Functional vs non-functional", "Functional requirements state what the system does; non-functional requirements state qualities such as performance, security and usability."),
    )),
}


def _lecture_posts(course_id, lectures, start_day):
    posts = []
    for n, (title, deck) in lectures.items():
        posts.append({
            "id": f"{course_id}-lec{n}", "course_id": course_id, "type": "material",
            "title": f"Lecture {n}: {title}",
            "description": f"Slides for lecture {n} uploaded. Please go through them before the next class.",
            "date": f"2026-09-{start_day + 7 * (n - 1):02d}",
            "attachments": [{"name": f"Lecture{n:02d}_{title.split()[0]}.pptx", "mime": "pptx", "slides": deck}],
        })
    return posts


ITEMS = (
    _lecture_posts("pdc", PDC_LECTURES, 1)
    + _lecture_posts("genai", GENAI_LECTURES, 2)
    + _lecture_posts("se", SE_LECTURES, 3)
    + [
        {"id": "pdc-syl1", "course_id": "pdc", "type": "announcement", "date": "2026-10-06",
         "title": "Sessional 1 syllabus",
         "description": "Dear students, Sessional 1 will be held on 14 October. The syllabus for Sessional 1 covers lectures 1 to 4 (including Amdahl's and Gustafson's law numericals).",
         "attachments": []},
        {"id": "pdc-syl2", "course_id": "pdc", "type": "announcement", "date": "2026-11-10",
         "title": "Sessional 2 course content",
         "description": "Sessional 2 covers lectures 5 to 6 (OpenMP and MPI). Bring calculators.",
         "attachments": []},
        {"id": "pdc-a1", "course_id": "pdc", "type": "assignment", "date": "2026-09-20",
         "title": "Assignment 1: Speedup analysis",
         "description": "Compute speedup and efficiency for the given programs using Amdahl's law. Due 27 September.",
         "attachments": []},
        {"id": "pdc-q1", "course_id": "pdc", "type": "assignment", "date": "2026-09-25",
         "title": "Quiz 1",
         "description": "Online quiz on Flynn's taxonomy and parallel architectures. 15 minutes.",
         "attachments": []},
        {"id": "genai-syl", "course_id": "genai", "type": "announcement", "date": "2026-10-08",
         "title": "Mid exam portion",
         "description": "Sessional 1 syllabus: lectures 1 to 3.",
         "attachments": []},
        {"id": "genai-misc", "course_id": "genai", "type": "announcement", "date": "2026-10-12",
         "title": "Important - read before Monday",
         "description": "Check the shared folder.",
         "attachments": []},
        {"id": "genai-ref", "course_id": "genai", "type": "material", "date": "2026-09-30",
         "title": "Reference: Attention Is All You Need (paper)",
         "description": "Optional reading for interested students.",
         "attachments": []},
        {"id": "se-proj", "course_id": "se", "type": "assignment", "date": "2026-10-01",
         "title": "Project proposal submission",
         "description": "Submit your semester project proposal (max 4 pages). Due 10 October.",
         "attachments": []},
    ]
)
