import { useState } from 'react';
import { useGame } from '../context/GameContext';
import { sendAction } from '../api/client';
import { PremiumButton, PremiumText } from '../components/shared/PremiumComponents';
import { Gamepad2, Send, Zap, Activity } from 'lucide-react';
import { PremiumGameLayout } from './PremiumGameLayout';
import { motion, AnimatePresence } from 'framer-motion';

export const GenericGameView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug, players } = useGame();
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    // Dynamic State Rendering
    // We try to find common keys like 'narrative', 'scene', 'story_text', etc.
    const narrative =
        gameState.scene ||
        gameState.narrative ||
        gameState.last_ai_response?.narrative ||
        (gameState.story_text ? gameState.story_text[gameState.story_text.length - 1] : "") ||
        "The game is ready. Fate awaits your command.";

    const turn = gameState.turn || 0;
    const status = gameState.status || 'Active';

    const handleAction = async () => {
        if (!input.trim() || !sessionId || !gameSlug) return;
        setLoading(true);
        try {
            // "action" is the generic action type for most legacy routers
            const resp = await sendAction(gameSlug, sessionId, userId, 'action', input);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("Action error", e);
        }
        setLoading(false);
        setInput("");
    };

    return (
        <PremiumGameLayout
            title={gameSlug?.replace('games-', '').replace('ai-', 'AI ').replace(/-/g, ' ').toUpperCase() || "GAME"}
            subtitle={`Turn ${turn} • ${status}`}
            icon={Gamepad2}
            backgroundVar="void"
            guideText="Interactive AI Experience. Type your action below to proceed."
        >
            <div className="flex flex-col h-full gap-6 relative min-h-[60vh]">

                {/* Main Display */}
                <div className="flex-1 bg-black/40 rounded-3xl p-8 relative overflow-hidden border border-white/10 shadow-2xl">
                    <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/5 to-transparent pointer-events-none" />

                    <div className="relative z-10 flex flex-col h-full">
                        <div className="flex items-center gap-2 mb-6 text-gold/60 text-xs font-bold uppercase tracking-widest">
                            <Activity size={14} /> LIVE SESSION
                        </div>

                        <div className="flex-1 overflow-y-auto custom-scrollbar pr-4">
                            <AnimatePresence mode='wait'>
                                <motion.div
                                    key={JSON.stringify(narrative)}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="font-serif text-xl md:text-2xl text-gray-200 leading-relaxed"
                                >
                                    <PremiumText text={typeof narrative === 'string' ? narrative : JSON.stringify(narrative)} />
                                </motion.div>
                            </AnimatePresence>
                        </div>
                    </div>
                </div>

                {/* Input Area */}
                <div className="relative">
                    <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl blur opacity-75" />
                    <div className="relative bg-[#1a1625] rounded-xl p-2 flex items-center gap-3 border border-white/10 focus-within:border-gold/30 transition-colors">
                        <input
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleAction()}
                            placeholder="What do you do next?"
                            className="flex-1 bg-transparent border-none text-white px-4 py-3 focus:outline-none font-medium placeholder:text-gray-600"
                            disabled={loading}
                        />
                        <PremiumButton
                            onClick={handleAction}
                            disabled={loading || !input}
                            className="px-6 py-3 rounded-lg"
                        >
                            {loading ? <Zap size={18} className="animate-spin" /> : <Send size={18} />}
                        </PremiumButton>
                    </div>
                </div>

            </div>
        </PremiumGameLayout>
    );
};
