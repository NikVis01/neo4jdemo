# Twiga Neo4j Demo

# Knowledge Graph Q&A

## Comparing performance of Q&A in knowledge graphs and naive RAG.

### Problem: 

RAG is an amazing way to reduce the input context to LLMs. Although LLMs with massive context windows exist (they can probably receive entire textbooks at this point) - long contexts will increase LLM inference costs with and much of the text will not be relevant to the users query. Another limitation to RAG is deciding the number of chunks or how big chunks should be. Smaller chunks means you can retrieve more specific things, but larger chunks allows the LLM to have knowledge of broader topics, eg. “Summarize chapters 1,2,3,4,…” or “What is the general theme of this textbook?”. Knowledge graphs mitigate this problem by constructing nodes and edges, representing concept and their relations to other concepts, enabling global answers.

For more information on the value of knowledge graphs, I suggest reading the GraphRAG [paper](https://microsoft.github.io/graphrag/#graphrag-vs-baseline-rag) from Microsoft.

### Assignment:

This assignment aimed to explore the usage of knowledge graphs in answering questions to TIE textbooks. There are many different libraries one could use to leverage knowledge graphs - under the hood nearly all of them use a graph database called Neo4j (a Swedish company based in Malmö!). Our task was to:

1. Construct a knowledge graph from a textbook PDF 
   1. Can you visualize the knowledge graph somehow?
2. Evaluate performance relative to a baseline RAG by comparing answers from identical queries relevant to the textbook contents.
   1. Please perform RAG in your preferred manner - no need for anything fancy. LangChain naive RAG tutorial: [link](https://python.langchain.com/docs/tutorials/rag/).

... And we succeeded!

* [Neo4j / OpenAI](https://neo4j.com/blog/news/graphrag-python-package/)

# CURRENT DB STRUCTURE

![image](https://github.com/user-attachments/assets/d05d083d-aa18-4e50-ba72-a1eeb3d33e46)


## DEV TEAM LEAD NOTES & DEV TEAM Q&A:
N: Super impressed with your initiative in the implementation with very little input from Alvaro, Robert, and I. You should be proud of this work.
   I agree with your choice of "Intent Expansion" (I typically call this "Query Expansion" or "Query Preprocessing")
   Interesting choice on not wanting to walk too far on the graph traversal. I know little about KGs but I can see how this would make sense given that these are high school textbooks and typically assignments don't involve more 
   interconnected knowledge than a couple of steps in the tree. Eg. students aren't required to answer questions relating eg. cloud formations to migration patterns.

Q: What is the format of the Neo4J graph responses? I see in the demo you show just the Content but I recall that KGs often return relationships (eg. x -> relation to -> y)

A: It depends on how the Cypher query is constructed and its result returned. In our case the relationships weren't expressive or valuable directly our return dictionary did not contain them. This was mostly a limit we set for ourselves, 
   and we've since learned that using an LLM we could embed meaning into relationships between nodes as well.

Q: What are the key applications you see of KGs as opposed to standard vector DB search? Is there more/less value in using it in other subjects than geography?

A: There are a few both pros and cons. Most importantly it lets us query by semantic similiarity (in our implementation), we sort of follow the red thread of the book to some extent while also searching by query. 
   You take into account similarity between different parts of the book, potentially global (also where community generation with the Leiden method is valuable). 
   In a normal rag you only consider similarity of chunks to the query but we do this too as well as similarity between parts of the book. 
   Touching on this is also how we restructure the books content not trusting the book's initial structure, which we think can potentially showcase more complex relationships and similarity between chunks, especially when using an LLM 
   to create the relationships.

   We're unsure what impact the subject can have but we've seen certain types of user queries affect the value of graphRAG. 
   Queries performed worse when the topic was less connected to its neighbors, so it's better for books that are more specialized and tries to build a broad view of a subject. We're still unsure of this and would love to research more.

