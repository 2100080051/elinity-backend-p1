import React, { useState, useRef, useEffect } from 'react';
import { useGameWebSocket } from '../../hooks/useGameWebSocket';
import { Send, MessageSquare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGame } from '../../context/GameContext'; // Add context import

export const ChatSidebar = () => {
    const { messages, sendMessage } = useGameWebSocket();
    const { players } = useGame(); // Get players from context
    const [input, setInput] = useState("");
    const [isOpen, setIsOpen] = useState(true);
    const endRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim()) {
            sendMessage(input);
            setInput("");
        }
    };

    return (
        <div className={`fixed right-0 top-0 h-full bg-midnight/90 backdrop-blur-md border-l border-white/10 transition-all duration-300 z-50 ${isOpen ? 'w-80' : 'w-12'}`}>
            {/* Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="absolute -left-10 top-4 p-2 bg-midnight/80 rounded-l-md border-y border-l border-white/10 text-white hover:text-gold"
            >
                <MessageSquare size={20} />
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="flex flex-col h-full"
                    >
                        {/* Header */}
                        <div className="p-4 border-b border-white/10">
                            <h3 className="font-premium font-bold text-gold tracking-wider">LIVE CHAT</h3>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {messages.map((msg, i) => {
                                const senderName = players[msg.user_id]?.name || msg.sender || "Unknown";
                                return (
                                    <div key={i} className={`flex ${msg.isSelf ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[80%] p-3 rounded-lg text-sm ${msg.isSelf ? 'bg-deep-purple text-white' : 'bg-white/10 text-gray-200'}`}>
                                            <p>{msg.message}</p>
                                            <span className="text-[10px] opacity-50 block text-right mt-1 truncate max-w-[100px]">{senderName}</span>
                                        </div>
                                    </div>
                                )
                            })}
                            <div ref={endRef} />
                        </div>

                        {/* Input */}
                        <form onSubmit={handleSend} className="p-4 border-t border-white/10 bg-midnight">
                            <div className="relative">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Type a message..."
                                    className="w-full bg-black/30 border border-white/10 rounded-full py-2 px-4 pr-10 text-sm focus:outline-none focus:border-gold/50 transition-colors"
                                />
                                <button
                                    type="submit"
                                    className="absolute right-2 top-1.5 p-1 text-gold hover:text-white transition-colors"
                                >
                                    <Send size={16} />
                                </button>
                            </div>
                        </form>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
