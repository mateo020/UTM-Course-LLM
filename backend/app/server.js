const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const { TextLoader } = require("langchain/document_loaders/fs/text");
const { RecursiveCharacterTextSplitter } = require("langchain/text_splitter");
const { MemoryVectorStore } = require("langchain/vectorstores/memory");
const { OpenAIEmbeddings, ChatOpenAI } = require("@langchain/openai");
const {
    RunnableSequence,
    RunnablePassthrough,
    RunnableMap,
} = require("@langchain/core/runnables");
const { StringOutputParser } = require("@langchain/core/output_parsers");
const { ChatPromptTemplate } = require("@langchain/core/prompts");
const { formatDocumentsAsString } = require("langchain/util/document");
const { create_retrieval_chain } = require("langchain/chains");
const { createStuffDocumentsChain } = require("langchain/chains/combine_documents");
const {BM25Retriever} = require("@langchain/community/retrievers/bm25")
const fs = require("fs");



// Load course data from JSON
const courseData = JSON.parse(fs.readFileSync("./files/courses.json", "utf-8"));


// Create documents for each course
const documents = courseData.map((course) => {
    return {
      pageContent: `${course.course_code}: ${course.description} Prerequisites: ${course.prerequisites}`,
      metadata: {
        course_code: course.title,
      },
    };
  });
// Create BM25Retriever from the documents
const BM25_retriever = BM25Retriever.fromDocuments(documents, { k: 15 });




require("dotenv").config();
// const { create_history_aware_retriever } = require("langchain/retrievers");
const app = express();
const corsOptions = {
    origin: ["http://localhost:5173"],
};
const hub = require("langchain/hub");

app.use(cors(corsOptions));
app.use(bodyParser.json());

(async () => {
    try {
        if (!process.env.OPENAI_API_KEY) {
            throw new Error("Missing OPENAI_API_KEY in environment variables.");
        }

        // // Load and process documents
        const loaderCourse = new TextLoader("./files/course_data (4).txt");
        const loaderPrograms = new TextLoader("./files/program_info (2).txt");
        const courseDocs = await loaderCourse.load();
        const programDocs = await loaderPrograms.load();

        // Combine and split the documents
        const allDocs = [...courseDocs, ...programDocs];
        const textSplitter = new RecursiveCharacterTextSplitter({
            chunkSize: 5000, // Smaller size to ensure splitting
            chunkOverlap: 100,
        });
        const splits = await textSplitter.splitDocuments(allDocs);
        
        
        console.log("Number of splits:", splits.length);
        if (splits.length === 0) {
        console.error("No splits generated.");
        }
        splits.forEach((split) => {
            if (typeof split.pageContent !== "string") {
              console.error("Invalid chunk:", split);
            }
          });
          


        //Create a vector store
        const embeddings = new OpenAIEmbeddings({
            model: "text-embedding-3-small",
          });
        const vectorStore = new MemoryVectorStore(embeddings);

        const BATCH_SIZE = 100; // Adjust based on your API rate limit

        for (let i = 0; i < splits.length; i += BATCH_SIZE) {
        const batch = splits.slice(i, i + BATCH_SIZE);
        try {
            console.log(`Processing batch ${i / BATCH_SIZE + 1}`);
            await vectorStore.addDocuments(batch);
        } catch (error) {
            console.error(`Error processing batch ${i / BATCH_SIZE + 1}:`, error.message);
        }
        }

     
        const retriever = vectorStore.asRetriever();
       
        // const retriever = create_history_aware_retriever({
        //     baseRetriever: vectorStore.asRetriever()
        // });


        //Set up the language model
        const llm = new ChatOpenAI({
            apiKey: process.env.OPENAI_API_KEY,
            model: "gpt-4",
            temperature: 0,
            streaming: true,
            verbose: true,
        });
        


        const prompt = await hub.pull("rlm/rag-prompt");

        console.log("Loaded prompt:", prompt);
        const ragChain = await createStuffDocumentsChain({
            llm,
            prompt,
            outputParser: new StringOutputParser(),
          });

      

        // Handle API requests
        app.post("/api", async (req, res) => {
            try {
                const { question, chatHistory } = req.body;

                if (!question) {
                    return res.status(400).json({ error: "The 'question' field is required." });
                }

                // Retrieve context and invoke the RAG chain
                const context = await retriever.invoke(question);
                const response = await ragChain.invoke({
                    context: context,
                    question: question,
                });
                
                console.log(question)
                console.log(chatHistory)
                res.status(200).json({ answer: response });
            } catch (error) {
                console.error("Error processing API request:", error);
                res.status(500).json({ error: error.message });
            }
        });

        // **New Endpoint for Course Search**
        app.post("/search", async (req, res) => {
            try {
                const { query } = req.body;

                if (!query) {
                    return res.status(400).json({ error: "The 'query' field is required." });
                }

                // Use the BM25 retriever to find relevant courses
                const results = await BM25_retriever.invoke(query);

                // Format the results
                const formattedResults = results.map((result) => ({
                    course_code: result.metadata.course_code,
                    content: result.pageContent,
                }));
                console.log(formattedResults)

                res.status(200).json({ results: formattedResults });
            } catch (error) {
                console.error("Error processing search request:", error);
                res.status(500).json({ error: error.message });
            }
        });

        // Start the server
        app.listen(8080, () => {
            console.log("Server started on port 8080");
        });
    } catch (error) {
        console.error("Error setting up the server:", error);
    }
})();
