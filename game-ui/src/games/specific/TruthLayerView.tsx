import { useState } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumInput, PremiumText } from '../../components/shared/PremiumComponents';
import { Layers, Eye } from 'lucide-react';
import { motion } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const TruthLayerView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    const question = gameState.current_question || "Waiting for the first layer to peel back...";
    const layer = gameState.current_layer || 1;
    const reflections = gameState.reflections || [];

    const handleAnswer = async () => {
        if (!sessionId || !gameSlug || !input) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'answer', input);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) { console.error(e); }
        setLoading(false);
        setInput("");
    };

    return (
        <PremiumGameLayout
            title="Truth & Layer"
            subtitle={`Depth Level: ${layer}`}
            icon={Layers}
            backgroundVar="void"
            guideText="1. Each question digs deeper into your thoughts.\n2. Be honest; the AI truth analyzer detects shallow responses.\n3. Reaching Level 3 unlocks the core revelation.\n4. Share the experience with other Seekers to see their layers."
        >
            <div className="flex flex-col h-full items-center justify-center">

                {/* Layer Indicators */}
                <div className="flex justify-center mb-16 gap-6 relative">
                    <div className="absolute top-1/2 left-0 w-full h-[1px] bg-white/10 -z-10" />
                    {[1, 2, 3].map((l) => (
                        <motion.div
                            key={l}
                            animate={{
                                scale: layer === l ? 1.5 : 1,
                                backgroundColor: layer >= l ? (l === 3 ? '#FFD700' : '#8B5CF6') : '#334155'
                            }}
                            className="w-4 h-4 rounded-full border-4 border-midnight shadow-xl z-10"
                        />
                    ))}
                </div>

                <div className="w-full max-w-2xl text-center mb-12 relative group">
                    <div className="absolute -inset-10 bg-indigo-500/10 blur-3xl rounded-full opacity-50 group-hover:opacity-75 transition duration-1000" />
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        key={question}
                        className="relative"
                    >
                        <h3 className="text-3xl md:text-5xl font-light text-white leading-tight font-premium">
                            <PremiumText text={question} />
                        </h3>
                    </motion.div>
                </div>

                <div className="w-full max-w-md bg-white/5 p-6 rounded-2xl border border-white/10 backdrop-blur-md shadow-2xl">
                    <PremiumInput
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        placeholder="Speak your truth..."
                        className="bg-transparent border-none text-center text-xl placeholder:text-white/20"
                    />
                    <div className="h-[1px] w-full bg-gradient-to-r from-transparent via-white/20 to-transparent my-4" />
                    <PremiumButton
                        className="w-full py-4 text-xs tracking-[0.2em]"
                        onClick={handleAnswer}
                        disabled={loading || !input}
                    >
                        {loading ? 'REVEALING...' : 'REVEAL TRUTH'}
                    </PremiumButton>
                </div>

                <div className="mt-8 text-white/20 text-xs tracking-widest uppercase flex items-center gap-2">
                    <Eye size={12} /> Only truth moves you deeper
                </div>
            </div>
        </PremiumGameLayout>
    );
};
