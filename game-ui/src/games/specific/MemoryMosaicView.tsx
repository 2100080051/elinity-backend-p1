import { useState } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumText } from '../../components/shared/PremiumComponents';
import {
    Image, Sparkles, Plus, Ghost,
    Eye, Wind, Zap, Layers,
    Focus, Palette, History,
    Maximize2, ChevronUp, CircleDashed
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const MemoryMosaicView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const theme = gameState.theme || "The Archival Void";
    const memories = gameState.memories || [];
    const synthesis = gameState.last_synthesis || "The archive is awaiting its first fragment.";
    const clarity = gameState.clarity ?? 10;
    const resonance = gameState.resonance ?? 50;
    const hue = gameState.hue || "#FFFFFF";
    const cluster = gameState.cluster || "The Awakening";
    const config = gameState.kaleidoscope_config || { sides: 6, primary_color: "Silver" };

    const handleShare = async () => {
        if (!sessionId || !gameSlug || !input) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'share_memory', input);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) { console.error("Archival Error:", e); }
        setLoading(false);
        setInput("");
    };

    return (
        <PremiumGameLayout
            title="Memory Mosaic"
            subtitle={`${theme} • ${cluster}`}
            icon={Focus}
            backgroundVar="starfield"
            guideText="Manifest fragments of the past. The Lens of Atavism weaves them into a chromatic history. Clarity defines the detail, Resonance defines the harmony."
        >
            <div className="flex flex-col h-full gap-8 relative overflow-hidden p-6 md:p-10">

                {/* --- AMBIENT CAVE BACKGROUND --- */}
                <div
                    className="absolute inset-0 z-0 opacity-20 pointer-events-none blur-[100px] transition-colors duration-[2000ms]"
                    style={{ backgroundColor: hue }}
                />

                {/* --- ARCHIVAL HUD (TOP) --- */}
                <div className="flex justify-between items-start z-20">
                    <div className="flex gap-10">
                        {/* Clarity Circle */}
                        <div className="flex flex-col items-center gap-2">
                            <div className="relative w-16 h-16 flex items-center justify-center">
                                <svg className="w-full h-full -rotate-90">
                                    <circle cx="32" cy="32" r="30" fill="none" stroke="currentColor" strokeWidth="2" className="text-white/5" />
                                    <motion.circle
                                        cx="32" cy="32" r="30" fill="none" stroke="currentColor" strokeWidth="2"
                                        className="text-cyan-400" strokeDasharray="188.4"
                                        animate={{ strokeDashoffset: 188.4 - (1.884 * clarity) }}
                                    />
                                </svg>
                                <Eye className="absolute w-4 h-4 text-cyan-400" />
                            </div>
                            <span className="text-[9px] font-black uppercase tracking-widest text-cyan-400/60">Clarity: {clarity}%</span>
                        </div>

                        {/* Resonance Circle */}
                        <div className="flex flex-col items-center gap-2">
                            <div className="relative w-16 h-16 flex items-center justify-center">
                                <svg className="w-full h-full -rotate-90">
                                    <circle cx="32" cy="32" r="30" fill="none" stroke="currentColor" strokeWidth="2" className="text-white/5" />
                                    <motion.circle
                                        cx="32" cy="32" r="30" fill="none" stroke="currentColor" strokeWidth="2"
                                        className="text-pink-500" strokeDasharray="188.4"
                                        animate={{ strokeDashoffset: 188.4 - (1.884 * resonance) }}
                                    />
                                </svg>
                                <Wind className="absolute w-4 h-4 text-pink-500" />
                            </div>
                            <span className="text-[9px] font-black uppercase tracking-widest text-pink-500/60">Resonance: {resonance}%</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="px-5 py-2 bg-black/40 border border-white/10 rounded-2xl backdrop-blur-xl flex items-center gap-3">
                            <Palette size={14} style={{ color: hue }} />
                            <div className="flex flex-col">
                                <span className="text-[8px] text-white/30 uppercase font-black tracking-widest">Active Hue</span>
                                <span className="text-[10px] font-bold text-white uppercase">{cluster}</span>
                            </div>
                        </div>
                        <div className="px-5 py-2 bg-black/40 border border-white/10 rounded-2xl backdrop-blur-xl flex items-center gap-3">
                            <Layers size={14} className="text-white/40" />
                            <span className="text-[10px] font-bold text-white">{memories.length} Shards</span>
                        </div>
                    </div>
                </div>

                {/* --- LENS SYNTHESIS (MAIN MESSAGE) --- */}
                <div className="relative z-10 flex flex-col items-center text-center px-4 max-w-4xl mx-auto py-10">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={synthesis}
                            initial={{ opacity: 0, y: 10, filter: 'blur(10px)' }}
                            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                            exit={{ opacity: 0, y: -10, filter: 'blur(10px)' }}
                            className="space-y-6"
                        >
                            <Sparkles className="w-6 h-6 text-white/20 mx-auto" />
                            <h2 className="text-2xl md:text-4xl text-white font-serif italic leading-relaxed">
                                <PremiumText text={synthesis} />
                            </h2>
                            <div className="flex items-center justify-center gap-3 text-[10px] font-black uppercase tracking-[0.5em] text-white/20">
                                <span className="h-px w-10 bg-white/10" />
                                Current Frequency: {config.primary_color} {config.fractal_type}
                                <span className="h-px w-10 bg-white/10" />
                            </div>
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* --- FRAGMENT GRID (MOSAIC) --- */}
                <div className="flex-1 min-h-0 flex flex-col z-20 overflow-hidden">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xs font-black uppercase tracking-[0.3em] text-white/40 flex items-center gap-3">
                            <History size={14} /> Recorded History
                        </h3>
                        <button className="text-[9px] font-black uppercase tracking-widest text-white/20 hover:text-white transition-colors">Expand Archival Log</button>
                    </div>

                    <div className="flex-1 overflow-x-auto overflow-y-hidden custom-scrollbar pb-6 flex items-stretch gap-6">
                        <AnimatePresence mode="popLayout">
                            {memories.map((mem: any, i: number) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, scale: 0.8, x: 50 }}
                                    animate={{ opacity: 1, scale: 1, x: 0 }}
                                    whileHover={{ y: -10, scale: 1.02 }}
                                    className="relative flex-none w-72 h-full flex flex-col group"
                                >
                                    <div className="absolute inset-0 bg-white/5 rounded-3xl -z-10 group-hover:bg-white/10 transition-colors" />
                                    <div
                                        className="absolute top-0 left-0 w-full h-2 rounded-t-3xl blur-[2px] opacity-60"
                                        style={{ backgroundColor: hue }}
                                    />

                                    <div className="flex-1 p-8 flex flex-col justify-center items-center text-center overflow-hidden">
                                        <Maximize2 className="absolute top-6 right-6 w-3 h-3 text-white/10 group-hover:text-white/40 opacity-0 group-hover:opacity-100 transition-all" />
                                        <p className="text-lg text-white/80 font-serif italic leading-relaxed line-clamp-6">
                                            "{mem.text}"
                                        </p>
                                    </div>

                                    <div className="p-6 border-t border-white/5 flex justify-between items-center bg-black/20 rounded-b-3xl">
                                        <div className="flex flex-col">
                                            <span className="text-[8px] uppercase font-black text-white/30">Shard ID</span>
                                            <span className="text-[10px] font-mono text-white/50">#ATV-{1000 + i}</span>
                                        </div>
                                        <div className="h-8 w-8 rounded-full border border-white/10 flex items-center justify-center">
                                            <span className="text-[10px] font-bold text-white/40">{i + 1}</span>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {/* Placeholder for new shard */}
                        <div className="flex-none w-72 h-full border-2 border-dashed border-white/5 rounded-3xl flex flex-col items-center justify-center gap-4 text-white/10">
                            <Plus size={32} />
                            <span className="text-[10px] uppercase font-black tracking-widest text-center">Awaiting Next Fragment</span>
                        </div>
                    </div>
                </div>

                {/* --- INTERACTION OVERLAY --- */}
                <div className="mt-6 mx-auto w-full max-w-4xl z-30">
                    <div className="relative group">
                        <div
                            className="absolute -inset-1 rounded-[3rem] blur-2xl opacity-0 group-focus-within:opacity-20 transition-opacity duration-1000"
                            style={{ backgroundColor: hue }}
                        />
                        <div className="relative bg-black/60 border border-white/10 rounded-[3rem] p-4 flex items-center gap-6 shadow-3xl backdrop-blur-[40px]">
                            <div className="w-14 h-14 rounded-full bg-white/5 flex items-center justify-center text-white/40 group-focus-within:text-white transition-colors">
                                <History size={24} />
                            </div>
                            <input
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleShare()}
                                placeholder="Whisper a fading fragment into the lens..."
                                className="flex-1 bg-transparent border-none text-2xl font-serif text-white placeholder:text-white/5 focus:outline-none italic"
                                disabled={loading}
                            />
                            <PremiumButton
                                onClick={handleShare}
                                disabled={loading || !input}
                                className="px-12 py-4 rounded-full font-black text-[10px] tracking-widest uppercase transition-all"
                            >
                                {loading ? <Hash className="animate-spin" size={16} /> : 'SYNTHESIZE'}
                            </PremiumButton>
                        </div>
                    </div>

                    <div className="mt-4 flex justify-center gap-8">
                        <div className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-white/20">
                            <CircleDashed className="animate-spin-slow w-3 h-3" />
                            Archival Loop Active
                        </div>
                        <div className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-white/20">
                            <ChevronUp className="animate-bounce w-3 h-3" />
                            Stability: Optimal
                        </div>
                    </div>
                </div>

            </div>
        </PremiumGameLayout>
    );
};

// CSS for rotating a dashed circle
const Hash = ({ className, size }: { className?: string, size?: number }) => (
    <div className={`relative ${className}`} style={{ width: size, height: size }}>
        <div className="absolute inset-0 border border-dashed border-current rounded-full animate-spin-slow" />
        <div className="absolute inset-2 border border-dotted border-current rounded-full animate-reverse-spin" />
    </div>
);
