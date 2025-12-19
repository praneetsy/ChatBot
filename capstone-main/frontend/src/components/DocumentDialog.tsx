"use client";
import React from "react";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";
import { Textarea } from "../components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
const DocumentDialog = () => {
  const [selectedAgent, setSelectedAgent] = React.useState("");
  const [documentText, setDocumentText] = React.useState("");

  const addDocument = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/metadata?agent_name=${selectedAgent}&text=${encodeURIComponent(
          documentText
        )}`
      );
      const data = await response.json();
      alert("Document added successfully");
      console.log(data);
      setSelectedAgent("");
      setDocumentText("");
    } catch (error) {
      alert("Error adding document");
      console.error("Error adding document: ", error);
    }
  };
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
          focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 
          disabled:cursor-not-allowed flex items-center justify-center min-w-[5rem]
          transition-colors"
        >
          Add Document
        </button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle> Add Document </DialogTitle>
        <Select
          value={selectedAgent}
          onValueChange={(val) => setSelectedAgent(val)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select an agent" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Customer Database Search">
              Customer Database Search
            </SelectItem>
            <SelectItem value="Organizational Information">
              Organizational Information
            </SelectItem>
          </SelectContent>
        </Select>
        <Textarea
          value={documentText}
          onChange={(e) => setDocumentText(e.target.value)}
          placeholder="Enter document text here..."
        />
        <DialogFooter>
          <DialogClose asChild>
            <button onClick={() => addDocument()}>
              <span className="text-blue-600">Add Document</span>
            </button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default DocumentDialog;
