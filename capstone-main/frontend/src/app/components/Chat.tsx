"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Bot, User, RefreshCw } from "lucide-react";
import DocumentDialog from "../../components/DocumentDialog";

interface Message {
  content: {
    relevant_agent?: string;
    other_agents?: [
      {
        name: string;
        capability: number;
      }
    ];
    top_documents?: string[];
    switched?: boolean;
    query_used: string;
    conversation_history?: string[];
    clarify?: boolean;
  };
  role: "user" | "assistant";
  timestamp: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return `${String(date.getHours()).padStart(2, "0")}:${String(
      date.getMinutes()
    ).padStart(2, "0")}`;
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    const timestamp = new Date().toISOString();

    const userMessage: Message = {
      content: {
        query_used: input,
      },
      role: "user",
      timestamp,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await fetch(
        `http://localhost:8000/agents?query=${encodeURIComponent(input)}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

      const assistantMessage: Message = {
        content: {
          relevant_agent: data.relevant_agent,
          other_agents: data.other_agents,
          top_documents: data.top_documents,
          switched: data.switched,
          conversation_history: data.conversation_history,
          clarify: data.clarify,
          query_used: data.query_used,
        },
        role: "assistant",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white border-b p-4 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <Bot className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-xl font-bold text-gray-800">
              Nexteer AI Dispatcher
            </h1>
            <p className="text-sm text-gray-500">
              Intelligent routing and response system
            </p>
          </div>
        </div>
        <button
          onClick={clearChat}
          className="flex items-center space-x-1 text-gray-600 hover:text-gray-800 
            bg-gray-100 px-3 py-1.5 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Clear Chat</span>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-10">
            <Bot className="h-16 w-16 mx-auto mb-4 text-blue-500" />
            <h2 className="text-xl font-semibold mb-2">
              Welcome to Nexteer AI Dispatcher
            </h2>
            <p className="text-gray-600">
              I can help route your queries to the right department and provide
              relevant information. How can I assist you today?
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`flex space-x-2 max-w-[80%] ${
                message.role === "user" ? "flex-row-reverse" : "flex-row"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center
                  ${message.role === "user" ? "bg-blue-500" : "bg-gray-500"}`}
              >
                {message.role === "user" ? (
                  <User className="h-5 w-5 text-white" />
                ) : (
                  <Bot className="h-5 w-5 text-white" />
                )}
              </div>
              <div
                className={`p-4 rounded-lg ${
                  message.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-white border border-gray-200 text-black"
                }`}
              >
                {message.role === "user" && (
                  <p className="whitespace-pre-wrap">
                    {message.content.query_used}
                  </p>
                )}
                {message.content.clarify ? (
                  <p>
                    I need more information to assist you. Can you please
                    clarify your query?
                  </p>
                ) : (
                  <>
                    {message.role === "assistant" && (
                      <>
                        {message.content.relevant_agent && (
                          <p>
                            I have identified the most relevant agent for your
                            query:{" "}
                            <strong>{message.content.relevant_agent}</strong>
                          </p>
                        )}
                        {message.content.other_agents &&
                          message.content.other_agents.length > 0 && (
                            <p>
                              I have also found other agents who can help you
                              with your query:{" "}
                              {message.content.other_agents.map((agent) => (
                                <strong key={agent.name}>{agent.name}</strong>
                              ))}
                            </p>
                          )}
                        <br />
                        {message.content.top_documents &&
                          message.content.top_documents.length > 0 && (
                            <>
                              <p>
                                Here are some top documents that might help you:
                              </p>
                              <ul className="list-disc list-inside text-sm">
                                {message.content.top_documents.map((doc) => (
                                  <li key={doc}>
                                    <code>{doc}</code>
                                  </li>
                                ))}
                              </ul>
                              <br />
                            </>
                          )}
                        {message.content.switched && (
                          <p>
                            I have switched to a different agent to better
                            assist you.
                          </p>
                        )}
                      </>
                    )}
                  </>
                )}

                <span
                  className={`text-xs ${
                    message.role === "user" ? "text-blue-100" : "text-black"
                  }`}
                >
                  {formatTime(message.timestamp)}
                </span>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-4 bg-white border-t">
        <div className="flex space-x-4">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about Nexteer..."
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none 
              focus:ring-2 focus:ring-blue-500 max-h-32 min-h-[2.5rem] resize-y text-black"
            disabled={isLoading}
          />
          <DocumentDialog />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
              focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 
              disabled:cursor-not-allowed flex items-center justify-center min-w-[5rem]
              transition-colors"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <>
                <Send className="h-5 w-5" />
              </>
            )}
          </button>
        </div>
        <div className="mt-2 flex justify-between items-center">
          <p className="text-xs text-gray-500">
            Press Enter to send, Shift + Enter for new line
          </p>
          <p className="text-xs text-gray-500">Powered by Nexteer AI</p>
        </div>
      </form>
    </div>
  );
}
