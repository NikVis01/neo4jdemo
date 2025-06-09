# neo4jdemo

# Knowledge Graph Q&A

## Comparing performance of Q&A in knowledge graphs and naive RAG.

### Problem: 

RAG is an amazing way to reduce the input context to LLMs. Although LLMs with massive context windows exist (they can probably receive entire textbooks at this point) - long contexts will increase LLM inference costs with and much of the text will not be relevant to the users query. Another limitation to RAG is deciding the number of chunks or how big chunks should be. Smaller chunks means you can retrieve more specific things, but larger chunks allows the LLM to have knowledge of broader topics, eg. “Summarize chapters 1,2,3,4,…” or “What is the general theme of this textbook?”. Knowledge graphs mitigate this problem by constructing nodes and edges, representing concept and their relations to other concepts, enabling global answers.

For more information on the value of knowledge graphs, I suggest reading the GraphRAG [paper](https://microsoft.github.io/graphrag/#graphrag-vs-baseline-rag) from Microsoft.

### Assignment:

This assignment aims to explore the usage of knowledge graphs in answering questions to TIE textbooks. There are many different libraries one could use to leverage knowledge graphs - under the hood nearly all of them use a graph database called Neo4j (a Swedish company based in Malmö!). Your task is to:

1. Construct a knowledge graph from a textbook PDF 
   1. Can you visualize the knowledge graph somehow?
2. Evaluate performance relative to a baseline RAG by comparing answers from identical queries relevant to the textbook contents.
   1. Please perform RAG in your preferred manner - no need for anything fancy. LangChain naive RAG tutorial: [link](https://python.langchain.com/docs/tutorials/rag/).

### Notes:

* No need for a fancy UI - you can do it in a Python file (.py) or notebook (.ipynb).
* Depending on the library, you may first have to extract text to markdown or to a string - then construct the knowledge graph. I will give you freedom to choose the specific library and will provide some alternatives below.
* No need to parse the WHOLE textbook - you may start exploring with a subset. Please include any PDF parsing/ingestion in your work.
* Feel free to try hybrid versions if you like!

### Library alternatives:

* [Neo4j / OpenAI](https://neo4j.com/blog/news/graphrag-python-package/)
* [LangChain](https://neo4j.com/labs/genai-ecosystem/langchain/#\_knowledge_graph_construction)
* [LlamaIndex](https://neo4j.com/labs/genai-ecosystem/llamaindex/)


Layers:

1. THEMES
- Headings: Fishing, Forestry, Planted Forests, Natural Forests

2. HEADINGS

Fishing
- content

Forestry
- content
-> Planted Forests: Agriculture

Planted Forests
- content
-> Natural Forests: Man-made

Natural Forests
- content
-> Planted Forests: Theseus


// Here's some useful Cypher Scripts:

// Creating/Modifying primary and tertriary nodes:
MERGE (t:Themes {name:"Themes"})

MERGE (a:Theme {name:"Fishing"})
SET a.content = "Fishing involves catching fish and other water creatures from oceans, lakes, seas, dams, rivers and ponds for domestic or commercial purposes."

MERGE (b:Theme {name:"Forestry"})
SET b.content = "Forestry is a set of practises that involve managing forests for ecological, social and economic purposes."

MERGE (c:Theme {name:"Natural Forests"})
SET c.content = "Natural forests are the forests that generated themselves naturally."

MERGE (d:Theme {name:"Planted Forests"})
SET d.content = "Planted forests are those in which trees are planted by human beings. They are commonly known as grown trees"

// Creating/Modifying relationships between nodes:

// ── 3. Link the master node to all individual Theme nodes
MATCH (root:Themes {name: "Themes"})

MATCH (theme:Theme)
WHERE theme.name IN ["Fishing", "Forestry", "Planted Forests", "Natural Forests"]

MERGE (root)-[:HAS_THEME]->(theme)