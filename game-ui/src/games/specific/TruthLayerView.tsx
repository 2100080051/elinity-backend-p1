import { useState, useEffect } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumText } from '../../components/shared/PremiumComponents';
import {
    Layers, Activity, ShieldAlert,
    Target, Fingerprint,
    Zap, Lock, Unlock, Hash,
    Cpu, Network, Radio
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const TruthLayerView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [flash, setFlash] = useState(false);

    if (!gameState) return null;

    const question = gameState.current_question || "Initiating probe...";
    const layer = gameState.layer || 1;
    const layerTitle = gameState.layer_title || "The Persona";
    const integrity = gameState.integrity ?? 100;
    const vulnerability = gameState.vulnerability ?? 10;
    const shielding = gameState.shielding ?? 50;
    const analysis = gameState.proxy_analysis || "Awaiting subject response.";
    const frequency = gameState.visual_frequency || "Stable baseline.";
    const subliminal = gameState.subliminal_prompt || "";

    useEffect(() => {
        if (subliminal) {
            setFlash(true);
            const timer = setTimeout(() => setFlash(false), 500);
            return () => clearTimeout(timer);
        }
    }, [subliminal]);

    const handleAnswer = async () => {
        if (!sessionId || !gameSlug || !input) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'answer', input);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) { console.error("Neural interruption:", e); }
        setLoading(false);
        setInput("");
    };

    return (
        <PremiumGameLayout
            title="Morphological Probe"
            subtitle={`Diagnostic: ${layerTitle}`}
            icon={Fingerprint}
            backgroundVar="void"
            guideText="Access the core truth through iterative psychological piercing. Shielding inhibits core-proximity. Integrity is the condition of successful sync."
        >
            <div className="flex flex-col h-full relative overflow-hidden bg-black/20">

                {/* --- SUBLIMINAL FLASH LAYER --- */}
                <AnimatePresence>
                    {flash && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 0.1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 z-0 flex items-center justify-center pointer-events-none"
                        >
                            <span className="text-[20vw] font-black uppercase text-white tracking-widest">{subliminal}</span>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* --- TOP HUD (BIOMETRICS) --- */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-10 z-20">
                    {/* Integrity */}
                    <div className="flex flex-col gap-2">
                        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.3em] text-cyan-500">
                            <div className="flex items-center gap-2"><Cpu size={12} /> Sync Integrity</div>
                            <span>{integrity}%</span>
                        </div>
                        <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                            <motion.div animate={{ width: `${integrity}%` }} className="h-full bg-cyan-500 shadow-[0_0_10px_#06b6d4]" />
                        </div>
                    </div>

                    {/* Shielding */}
                    <div className="flex flex-col gap-2">
                        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.3em] text-orange-500">
                            <div className="flex items-center gap-2"><Lock size={12} /> Defensive Shielding</div>
                            <span>{shielding}%</span>
                        </div>
                        <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                            <motion.div animate={{ width: `${shielding}%` }} className="h-full bg-orange-500 shadow-[0_0_10px_#f59e0b]" />
                        </div>
                    </div>

                    {/* Vulnerability */}
                    <div className="flex flex-col gap-2">
                        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.3em] text-purple-400">
                            <div className="flex items-center gap-2"><Activity size={12} /> Neural Exposure</div>
                            <span>{vulnerability}%</span>
                        </div>
                        <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                            <motion.div animate={{ width: `${vulnerability}%` }} className="h-full bg-purple-500 shadow-[0_0_10px_#a855f7]" />
                        </div>
                    </div>
                </div>

                {/* --- MAIN INTERFACE AREA --- */}
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-10 items-center px-10 pb-10 min-h-0">

                    {/* Concentric Layer Visualization (4 cols) */}
                    <div className="lg:col-span-4 relative flex items-center justify-center">
                        <div className="relative aspect-square w-full max-w-[300px]">
                            {[...Array(7)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    initial={false}
                                    animate={{
                                        scale: (7 - i) / 7,
                                        borderColor: layer > (7 - i) ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.05)',
                                        borderWidth: layer === (7 - i) ? '3px' : '1px'
                                    }}
                                    className={`absolute inset-0 rounded-full border transition-all duration-1000 ${layer === (7 - i) ? 'shadow-[0_0_30px_rgba(255,255,255,0.1)]' : ''}`}
                                />
                            ))}
                            <div className="absolute inset-0 flex items-center justify-center">
                                <motion.div
                                    animate={{
                                        opacity: [0.1, 0.4, 0.1],
                                        scale: [1, 1.2, 1]
                                    }}
                                    transition={{ repeat: Infinity, duration: 4 }}
                                    className="w-10 h-10 bg-cyan-500 rounded-full blur-xl"
                                />
                                <Hash className="w-5 h-5 text-white/40 font-black" />
                            </div>
                        </div>

                        {/* Analysis Box Overlay */}
                        <div className="absolute -bottom-10 left-0 right-0 p-6 bg-black/60 border border-white/5 rounded-2xl backdrop-blur-2xl">
                            <div className="flex items-center gap-2 mb-2">
                                <Radio className="w-3 h-3 text-cyan-400 animate-pulse" />
                                <span className="text-[10px] uppercase font-black tracking-widest text-white/30">Proxy Analysis</span>
                            </div>
                            <p className="text-[10px] font-mono leading-relaxed text-cyan-100/60 lowercase">
                                {analysis}
                            </p>
                        </div>
                    </div>

                    {/* The Aperture Question (8 cols) */}
                    <div className="lg:col-span-8 flex flex-col gap-10 h-full justify-center">
                        <div className="relative">
                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={question}
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    transition={{ duration: 0.8 }}
                                    className="relative z-10"
                                >
                                    <h2 className="text-4xl md:text-5xl lg:text-7xl font-extralight text-white leading-tight font-premium">
                                        <PremiumText text={question} />
                                    </h2>
                                </motion.div>
                            </AnimatePresence>
                        </div>

                        {/* Input Area */}
                        <div className="w-full max-w-2xl">
                            <div className="relative group">
                                <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-[2rem] blur-xl opacity-0 group-focus-within:opacity-100 transition-all duration-700" />
                                <div className="relative bg-black/40 border border-white/10 rounded-[2rem] px-10 py-6 overflow-hidden focus-within:border-cyan-500/40 transition-all">
                                    <input
                                        value={input}
                                        onChange={e => setInput(e.target.value)}
                                        onKeyDown={e => e.key === 'Enter' && handleAnswer()}
                                        placeholder="Type for diagnostic verification..."
                                        className="w-full bg-transparent border-none text-2xl font-serif text-white placeholder:text-white/5 focus:outline-none italic"
                                        disabled={loading}
                                    />
                                    <div className="flex justify-between items-center mt-6">
                                        <div className="flex items-center gap-4">
                                            <div className="flex gap-1">
                                                {[...Array(7)].map((_, i) => (
                                                    <div key={i} className={`h-3 w-1.5 rounded-sm ${i < layer ? 'bg-cyan-500 shadow-[0_0_5px_cyan]' : 'bg-white/5'}`} />
                                                ))}
                                            </div>
                                            <span className="text-[9px] uppercase font-black tracking-widest text-white/20">Depth Calibration</span>
                                        </div>
                                        <PremiumButton
                                            onClick={handleAnswer}
                                            disabled={loading || !input}
                                            className="px-10 py-3 rounded-xl text-[10px] font-black tracking-widest uppercase transition-all"
                                        >
                                            {loading ? <Activity className="animate-ping" size={12} /> : 'Sync Truth'}
                                        </PremiumButton>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* --- FOOTER (WAVEFORM) --- */}
                <div className="absolute bottom-0 inset-x-0 h-32 pointer-events-none overflow-hidden opacity-20">
                    <svg viewBox="0 0 1000 100" className="w-full h-full">
                        <motion.path
                            animate={{
                                d: [
                                    "M0 50 Q 250 10, 500 50 T 1000 50",
                                    "M0 50 Q 250 90, 500 50 T 1000 50",
                                    "M0 50 Q 250 10, 500 50 T 1000 50"
                                ]
                            }}
                            transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                            fill="none"
                            stroke="cyan"
                            strokeWidth="1"
                        />
                    </svg>
                    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 text-[8px] font-mono text-cyan-400/40 uppercase tracking-[1em]">
                        Visual Frequency: {frequency}
                    </div>
                </div>

            </div>
        </PremiumGameLayout>
    );
};
