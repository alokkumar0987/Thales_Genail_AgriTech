import React, { useState, useRef, useEffect } from "react";
import { FaMicrophone, FaPaperPlane, FaImage } from "react-icons/fa";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const BACKEND_URL = "http://localhost:8000";

const ChatbotPage = () => {
  const [messages, setMessages] = useState([]);
  const [textInput, setTextInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [sessionId, setSessionId] = useState(null);

  // ✅ Show fake welcome message on load
  useEffect(() => {
    const timer = setTimeout(() => {
      setMessages([
        { type: "bot", content: "👋 Welcome to Agri Help! How can I assist you today?" },
      ]);
    }, 800);
    return () => clearTimeout(timer);
  }, []);

  // ✅ Send Text Message
  const handleSend = async () => {
    if (!textInput.trim()) return;

    setMessages((prev) => [...prev, { type: "user", content: textInput }]);

    try {
      const response = await fetch(`${BACKEND_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: textInput,
          session_id: sessionId,
        }),
      });

      const data = await response.json();
      setSessionId(data.session_id);
      setMessages((prev) => [...prev, { type: "bot", content: data.response }]);
    } catch (err) {
      console.error("Error sending text:", err);
      setMessages((prev) => [
        ...prev,
        { type: "bot", content: "⚠️ Something went wrong, try again." },
      ]);
    }

    setTextInput("");
  };

  // ✅ Upload Image
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setMessages((prev) => [
      ...prev,
      { type: "user", content: URL.createObjectURL(file), isImage: true },
    ]);

    const formData = new FormData();
    formData.append("file", file);
    if (sessionId) formData.append("session_id", sessionId);

    try {
      const response = await fetch(`${BACKEND_URL}/upload-image`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setSessionId(data.session_id);
      setMessages((prev) => [...prev, { type: "bot", content: data.response }]);
    } catch (err) {
      console.error("Error uploading image:", err);
      setMessages((prev) => [
        ...prev,
        { type: "bot", content: "⚠️ Failed to process image." },
      ]);
    }
  };

  // 🎤 VOICE RECORDING FUNCTIONALITY
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await sendAudioToBackend(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Microphone access denied. Please allow microphone permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendAudioToBackend = async (audioBlob) => {
    setIsProcessingVoice(true);
    
    setMessages((prev) => [...prev, { type: "user", content: "🎤 Voice message...", isVoice: true }]);

    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.wav');
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    try {
      const response = await fetch(`${BACKEND_URL}/voice-query`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setSessionId(data.session_id);
      
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages.pop();
        return [...newMessages, { type: "bot", content: data.response }];
      });
    } catch (error) {
      console.error('Error sending audio:', error);
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages.pop();
        return [...newMessages, { type: "bot", content: "⚠️ Error processing voice query. Please try again." }];
      });
    } finally {
      setIsProcessingVoice(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="pt-[300px] md:pt-[250px] px-4 sm:px-6 md:px-10 min-h-screen bg-gray-200">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Panel (Desktop Inputs + Heading) */}
        <div className="hidden md:flex flex-col space-y-4 bg-green-800 shadow-lg p-6 shadow-md rounded-lg">
          <h1 className="text-2xl font-bold text-green-300 mb-4">🌾 Kissan Help</h1>

          {/* Text Input */}
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 border border-gray-300 rounded-full px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
            />
            <button
              onClick={handleSend}
              className="bg-green-600 text-white px-4 py-2 rounded-full hover:bg-green-700 transition"
            >
              <FaPaperPlane />
            </button>
          </div>

          {/* Image Upload */}
          <label className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 cursor-pointer transition">
            <FaImage />
            <span>Upload Image</span>
            <input type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
          </label>

          {/* Voice Input */}
          <button
            onClick={toggleRecording}
            disabled={isProcessingVoice}
            className={`px-4 py-2 rounded-lg flex items-center justify-center transition ${
              isRecording
                ? "bg-red-600 hover:bg-red-700 text-white"
                : isProcessingVoice
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
          >
            <FaMicrophone className="mr-2" />
            {isProcessingVoice ? "Processing..." : isRecording ? "Recording..." : "Record Voice"}
          </button>
        </div>

        {/* Right Panel (Chat Window) */}
        <div className="md:col-span-2 bg-gray-100 shadow-xl chat-container overflow-y-auto scrollbar-hide rounded-lg p-6 flex flex-col h-[70vh]">
          {/* Heading for Mobile */}
          <h1 className="md:hidden text-xl font-bold text-green-700 mb-4 text-center">
            🌾 Kissan Help
          </h1>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto mb-4 space-y-3">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`px-2 py-2 h-auto rounded-lg max-w-[70%] text-sm sm:text-base animate-fadeIn ${
                    msg.type === "user"
                      ? "bg-green-600 text-white"
                      : "bg-gray-200 text-gray-900"
                  }`}
                >
                  {msg.isImage ? (
                    <img src={msg.content} alt="User upload" className="rounded-lg max-h-40" />
                  ) : msg.isVoice ? (
                    <div className="flex items-center space-x-2">
                      <FaMicrophone />
                      <span>{msg.content}</span>
                    </div>
                  ) : (
                    <div className="prose prose-sm max-w-none prose-p:leading-relaxed prose-headings:text-green-700 prose-strong:text-green-800">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Mobile Input */}
          <div className="md:hidden flex items-center space-x-2 border-t pt-3">
            {/* Image Button */}
            <label className="bg-green-600 hover:bg-green-700 text-white p-3 rounded-full cursor-pointer transition">
              <FaImage />
              <input type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
            </label>

            {/* Text Input */}
            <input
              type="text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Type..."
              className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
            />

            {/* Send Button */}
            <button
              onClick={handleSend}
              className="bg-green-600 text-white px-4 py-2 rounded-full hover:bg-green-700 transition"
            >
              <FaPaperPlane />
            </button>

            {/* Voice Button */}
            <button
              onClick={toggleRecording}
              disabled={isProcessingVoice}
              className={`p-3 rounded-full transition ${
                isRecording
                  ? "bg-red-600 hover:bg-red-700 text-white"
                  : isProcessingVoice
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700 text-white"
              }`}
            >
              <FaMicrophone />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;
