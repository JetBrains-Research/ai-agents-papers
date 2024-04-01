# Papers we read over March 25 - March 31

## :robot: Agents
| :scroll: Paper                                                                                                    | :link: Resources                         |
|:------------------------------------------------------------------------------------------------------------------|:-----------------------------------------|
| [CodePlan: Repository-level Coding using LLMs and Planning](https://arxiv.org/abs/2309.12499) (Microsoft, FSE'24) | [code](https://arxiv.org/abs/2309.12499) |
| [MAGIS: LLM-Based Multi-Agent Framework for GitHub Issue Resolution](https://arxiv.org/abs/2403.17927)            |                                          |
## :bookmark: Other
| :scroll: Paper                                                                                                                                     | :link: Resources                                                                                                                                                                                                      |
|:---------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Can large language models explore in-context?](https://arxiv.org/abs/2403.15371) (Microsoft)                                                      |                                                                                                                                                                                                                       |
| [Agent-FLAN: Designing Data and Methods of Effective Agent Tuning for Large Language Models](https://arxiv.org/abs/2403.12881v1) (InternLM)        | [code](https://arxiv.org/abs/2403.12881v1), [website](https://internlm.github.io/Agent-FLAN/), [dataset](https://huggingface.co/datasets/internlm/Agent-FLAN), [model](https://huggingface.co/internlm/Agent-FLAN-7b) |
| [RepoHyper: Better Context Retrieval Is All You Need for Repository-Level Code Completion](https://arxiv.org/abs/2403.06095)                       | [code](https://arxiv.org/abs/2403.06095)                                                                                                                                                                              |
| [Enhancing LLM-Based Coding Tools through Native Integration of IDE-Derived Static Context](https://arxiv.org/abs/2402.03630) (LLM4Code @ ICSE'24) |                                                                                                                                                                                                                       |
| [Evaluating Large Language Models with Runtime Behavior of Program Execution](https://arxiv.org/abs/2403.16437)                                    |                                                                                                                                                                                                                       |
## :world_map: Benchmarks & Environments
| :scroll: Paper                                                                                                                                 | :link: Resources                                                                                      |
|:-----------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------|
| [DebugBench: Evaluating Debugging Capability of Large Language Models](https://arxiv.org/abs/2401.04621)                                       | [code](https://arxiv.org/abs/2401.04621), [dataset](https://huggingface.co/datasets/Rtian/DebugBench) |
| [R2E: Turning any Github Repository into a Programming Agent Test Environment](https://openreview.net/pdf?id=xsytkViOsd) (LLMAgents @ ICLR'24) |                                                                                                       |
| [MacGyver: Are Large Language Models Creative Problem Solvers?](https://arxiv.org/abs/2311.09682) (NAACL'24, AI2)                              | [code](https://arxiv.org/abs/2311.09682)                                                              |
## :thinking: Reasoning & Planning
| :scroll: Paper                                                                                      | :link: Resources   |
|:----------------------------------------------------------------------------------------------------|:-------------------|
| [LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks](https://arxiv.org/abs/2402.01817) |                    |


# :mag: :book: In-Depth Paper Highlights

<details><summary>:scroll: <a href="https://arxiv.org/abs/2309.12499"><b>CodePlan: Repository-level Coding using LLMs and Planning</b></a> – by <a href="https://github.com/MartSlaaf">Yaroslav Zharov</a></summary>
A relatively old paper on repository-level code editing.
The authors embarked on a journey to employ LLM-based agents for this task.

They employ static analysis as the planner augmentation for the agent, which seems reasonable for code.
Given an initial instruction (e.g., someone changed the definition of one function) the method:
1. performs an analysis to find code chunks that are affected by this change (e.g., external calls, inheritance, etc.). If there are no chunks that are affected, the method goes directly to the testing step (5).
2. each of those chunks of code is added to the planning graph, it is connected to each node of the graph it depends on. Each new node is marked as pending.
3. each node of the computational graph, that has no pending nodes it depends on is offered to an agent to be changed. The prompt contains the following information:
    a. the chunk of code to change
    b. the spatial context (other methods in the same class, other functions in the same file, etc)
    c. the temporal context (what's the diff from the method start to the current state)
    d. the causal context (what's caused this node to be added, 4. what changes were introduced to the nodes it depends on)
the method goes to the first step, to add new nodes, now when the new set of changes was introduced.
5. (we come here only when there are no unaltered affected chunks of code). The resulting repository is passed to some testing engine, and authors employ compilation/type-checking as quality assurance.
6. If there are some errors during the testing, they are introduced as initial instructions for the new iteration of the method, and everything goes to the first stage again.

The authors assess their method from two points of view:
1. How well does it find the proper code chunks to edit. For this they measure matching blocks (edited both by the real programmer, and by the method), missed blocks (edited by real programmer but not by the method), and the spurious blocks (edited by the method, but not by the programmer), effectively finding accuracy and recall for their method in terms of code chunks.
2. How well does the code editing work. For this they measure editor distance between the predicted and the target code, and diffBLEU, which is, effectively, BLEU measured between the diff produced by the method and the diff produced by the programmer. The authors argue, that it helps to not overwhelm BLEU with lots of code that wasn't changed.
</details>

<details><summary>:scroll: <a href="https://arxiv.org/abs/2403.15371"><b>Can large language models explore in-context?</b></a> – by <a href="https://github.com/MartSlaaf">Yaroslav Zharov</a></summary>

The authors tried LLMs as the strategy engines to solve the Multi-Armed Bandits problem.
The problem is stated as follows (you can skip this if you know the multi-armed bandits): the agent has several options (arms) with their own associated probability of the reward. At each step, the agent activates one arm, which samples the reward (either 0 or 1) from the corresponding distribution. The aim of the agent is to maximize the received reward during the T steps. A good strategy, therefore, should balance exploration (you need to have some samples from each arm to define the one with the largest average) with exploitation (you need to activate the arm with the largest average reward as many times as possible).

The authors compared the LLMs to several well-known strategies (Thompson Sampling, greedy, Upper Confidence Bound) and concluded that LLMs (mostly) behave like a greedy strategy. To test how different prompting affects the models, the authors considered two different scenarios (presenting the task as click-a-button or which-ad-to-choose), task framing (either directly prompting the model to explore or not), types of history (raw or pre-calculated averages), output formats (single action, or probability distribution over actions), and planning strategies (direct answer, or chain-of-thought). And all of them, except GPT-4 + one specific combination, were greedy. Several exceptions were uniform (activating all arms randomly, without any exploitation).

The authors conclude that LLMs aren't good enough to replace the sampling strategies. External tools, e.g., summarizing history, were able to improve performance a bit.

Practical takeaway: we should not forget that the LLMs are:
* Language models indeed, and therefore, we should seek to extract from them the bias they learned on the great scale data they consumed instead of expecting them to behave as optimal algorithms on synthetic debiased problems. I guess if the arms were not made equal in appearance, the results may have changed drastically.
* Inductive in the sense that their next prediction can be pretty much defined by their previous predictions when they are added to the prompt.
* Faulty calculators (In my recent experience, GPT-4 tried to generate division by zero error by dividing 10 by 2).

My thoughts on the paper formatting:
* The authors first discuss several results and introduce the metrics they use in those discussions and plots. I was never a fan of the maxim that ""the figure should appear strictly after the text that refers to it"", but explaining the metrics one section later than using them is too much.
* The paper is overflown with small findings that aren't working on the larger story of the paper. I think this is a good example of how it can damage your paper to lay out too many details simultaneously. I personally think that it could be better to move additional findings, not working on the storyline, to an appendix.
</details>