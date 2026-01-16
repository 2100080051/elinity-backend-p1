import { useState } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumCard, PremiumInput } from '../../components/shared/PremiumComponents';
import { Mic2, Activity, Volume2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const EchoesView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [input, setInput] = useState("");

    const prompt = gameState.last_ai_response?.creative_prompt || "The silence waits for your voice. How do you feel right now?";
    const echo = gameState.last_ai_response?.echo_synthesis || "";

    const handleSubmit = async () => {
        const resp = await sendAction(gameSlug!, sessionId!, userId, 'express', input);
        if (resp.ok) updateGameState(resp.state);
        setInput("");
    };

    return (
        <PremiumGameLayout
            title="Echoes & Expressions"
            subtitle="Resonance Chamber"
            icon={Mic2}
            backgroundVar="void"
            guideText="1. Express your inner thoughts and feelings in the resonance chamber.\n2. The AI synthesizes an 'Echo' based on the collective frequency of the group.\n3. Watch your words visualize as frequencies in the chamber.\n4. Discover shared resonances with other participants."
        >
            <div className="h-full flex flex-col items-center justify-center relative">

                {/* Visualizer */}
                <div className="absolute top-0 left-0 w-full h-1/2 flex items-center justify-center gap-2 pointer-events-none opacity-30 z-0">
                    {[...Array(30)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="w-3 bg-gradient-to-t from-transparent via-gold/50 to-transparent rounded-full"
                            animate={{
                                height: [20, Math.random() * 150 + 20, 20],
                                opacity: [0.3, 0.8, 0.3]
                            }}
                            transition={{
                                duration: 1.5,
                                repeat: Infinity,
                                ease: "easeInOut",
                                delay: i * 0.1
                            }}
                        />
                    ))}
                </div>

                <div className="relative z-10 w-full max-w-2xl flex flex-col gap-8">
                    {/* Prompt Card */}
                    <motion.div
                        layout
                        className="text-center p-8 md:p-12 rounded-[3rem] bg-gradient-to-b from-white/10 to-transparent border border-white/10 backdrop-blur-md shadow-2xl"
                    >
                        <h3 className="text-gold/60 font-bold mb-6 uppercase text-xs tracking-[0.3em] flex items-center justify-center gap-2">
                            <Activity size={12} /> Current Frequency
                        </h3>
                        <p className="text-3xl md:text-5xl font-light text-white leading-tight font-premium">"{prompt}"</p>

                        {echo && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mt-8 bg-black/40 p-6 rounded-2xl border border-white/5 inline-block"
                            >
                                <div className="flex items-center justify-center gap-2 text-gold mb-2">
                                    <Volume2 size={16} /> <span className="text-xs uppercase tracking-widest">Echo Synthesized</span>
                                </div>
                                <p className="text-gray-300 italic font-serif">"{echo}"</p>
                            </motion.div>
                        )}
                    </motion.div>

                    {/* Input Area */}
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-purple-500 via-gold to-blue-500 rounded-2xl opacity-20 group-hover:opacity-50 blur transition duration-500" />
                        <div className="relative bg-[#0f0c18] border border-white/10 rounded-2xl p-2 flex items-center">
                            <PremiumInput
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                placeholder="Type your expression to resonate..."
                                className="bg-transparent border-none text-center text-lg h-14"
                                onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                            />
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-gold/50"><Mic2 size={24} /></div>
                        </div>
                    </div>

                    <PremiumButton onClick={handleSubmit} className="w-full py-4 text-xs tracking-[0.2em] shadow-[0_0_20px_rgba(255,215,0,0.1)] hover:shadow-[0_0_30px_rgba(255,215,0,0.3)] transition-shadow">
                        TRANSMIT RESONANCE
                    </PremiumButton>
                </div>
            </div>
        </PremiumGameLayout>
    );
};
