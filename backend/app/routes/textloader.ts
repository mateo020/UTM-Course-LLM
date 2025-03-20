import "dotenv/config";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { loadQAStuffChain } from "langchain/chains";
import { TextLoader } from "langchain/document_loaders/fs/text";

import { Document } from "@langchain/core/documents";
import { DocumentInterface } from "@langchain/core/documents";

export default async (question = "", filePath = "") => {
  const fileExtension = filePath.split(".").pop();
  let loader;

 if (fileExtension === "txt") {
    loader = new TextLoader(filePath);
  } else {
    return "unsupported file type";
  }

  const docs = await loader.load();

  const vectorStore = await MemoryVectorStore.fromDocuments(
    docs,
    new OpenAIEmbeddings()
  );

  const searchResponse = await vectorStore.similaritySearch(question, 1);
  const textRes = searchResponse
    .map((item: DocumentInterface<Record<string, any>>) => item?.pageContent)
    .join("\n");
  const llm = new OpenAI({ modelName: "gpt-4" });
  const chain = loadQAStuffChain(llm);

  const result = await chain.invoke({
    input_documents: [new Document({ pageContent: `${textRes}` })],
    question,
  });

  console.log(`\n\n Question: ${question}`);
  console.log(`\n\n Answer: ${result.text}`);
  return result.text;
};