import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    PenTool,
    BookOpen,
    Layers,
    Palette,
    Zap,
    Wind,
    Sparkles,
    MessageSquare,
    ChevronRight,
    ChevronLeft
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const ComicCreatorView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        ink_reserves = 100,
        current_panel = {},
        style = 'Modern',
        page_number = 1,
        available_actions = [],
        status = 'active'
    } = gameState;

    const handleAction = async (action: string) => {
        if (!action.trim() || !sessionId || !gameSlug || loading) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'action', action);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("Ink-Slinger communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#f1f1f1] text-[#1a1a1a] font-serif p-4 md:p-8 flex flex-col gap-6 relative overflow-hidden">
            {/* Comic Texture Overlay */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none grayscale contrast-200" style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 0)', backgroundSize: '4px 4px' }} />

            {/* Header - Edition Info */}
            <div className="flex flex-wrap items-end justify-between gap-4 border-b-4 border-black pb-4 z-10">
                <div className="flex items-center gap-6">
                    <div className="w-20 h-20 bg-black text-white flex items-center justify-center -rotate-3 shadow-lg">
                        <PenTool className="w-10 h-10" />
                    </div>
                    <div>
                        <h1 className="text-4xl font-black uppercase italic tracking-tighter leading-none">Ink-Slinger Prime</h1>
                        <div className="flex items-center gap-4 mt-1">
                            <span className="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded tracking-widest uppercase">Issue #{page_number}</span>
                            <span className="text-xs font-black uppercase tracking-widest text-black/40">{style} Era // Unrestricted</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <div className="text-right">
                        <p className="text-[10px] uppercase font-black tracking-widest mb-1">Ink Reserve</p>
                        <div className="w-48 h-10 bg-white border-4 border-black relative overflow-hidden rounded-sm group">
                            <motion.div
                                animate={{ width: `${ink_reserves}%` }}
                                className="absolute inset-y-0 left-0 bg-black"
                            />
                            <span className="absolute inset-0 flex items-center justify-center text-xs font-black mix-blend-difference text-white uppercase tracking-tighter">
                                {ink_reserves}% LOADED
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow">
                {/* Main Comic Panel */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-white border-4 border-black shadow-[15px_15px_0_rgba(0,0,0,0.1)] p-8 relative overflow-hidden flex flex-col justify-center"
                    >
                        {/* Halftone Accents */}
                        <div className="absolute top-0 right-0 w-32 h-32 opacity-10 rotate-45 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#000 2px, transparent 0)', backgroundSize: '8px 8px' }} />

                        {/* Dialogue Balloon */}
                        {current_panel.dialogue && (
                            <motion.div
                                initial={{ y: -20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                className="absolute top-10 left-10 max-w-[70%]"
                            >
                                <div className="bg-white border-2 border-black rounded-[2rem] px-6 py-4 shadow-md relative">
                                    <p className="text-sm font-bold italic text-black leading-tight uppercase tracking-tight">
                                        {current_panel.dialogue}
                                    </p>
                                    <div className="absolute -bottom-4 left-10 w-0 h-0 border-[15px] border-transparent border-t-black after:absolute after:-top-[17px] after:-left-[15px] after:border-[15px] after:border-transparent after:border-t-white" />
                                </div>
                            </motion.div>
                        )}

                        {/* Narrative Text */}
                        <div className="z-10 mt-auto">
                            <div className="bg-yellow-100 border-2 border-black p-6 shadow-sm mb-6 inline-block rotate-1 translate-x-4">
                                <p className="text-xl font-black uppercase italic text-black leading-tight tracking-tight">
                                    {scene}
                                </p>
                            </div>

                            {/* Sound Effects */}
                            <div className="flex gap-4 items-center">
                                {current_panel.effects?.map((eff: string, i: number) => (
                                    <motion.span
                                        key={i}
                                        initial={{ scale: 0 }}
                                        animate={{ scale: [0, 1.2, 1] }}
                                        className="text-4xl font-black text-red-500 uppercase tracking-tighter drop-shadow-md z-20"
                                        style={{ rotate: `${(Math.random() * 20) - 10}deg` }}
                                    >
                                        {eff}!
                                    </motion.span>
                                ))}
                            </div>
                        </div>

                        {/* Panel Number */}
                        <div className="absolute bottom-4 right-4 text-[10px] font-black bg-black text-white px-2 py-1 uppercase tracking-widest">
                            Panel {current_panel.number || '1.1'}
                        </div>
                    </motion.div>

                    {/* Action Interface */}
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-wrap gap-2">
                            {available_actions.map((action: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(action)}
                                    disabled={loading}
                                    className="px-6 py-2 bg-black text-white rounded-sm hover:-translate-y-1 hover:shadow-lg transition-all font-black uppercase text-xs tracking-widest flex items-center gap-2"
                                >
                                    <ChevronRight className="w-4 h-4" />
                                    {action}
                                </button>
                            ))}
                        </div>

                        <div className="relative group">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Write the next panel's destiny..."
                                className="w-full bg-white border-4 border-black py-4 px-6 focus:outline-none shadow-sm text-lg font-black uppercase tracking-tight italic"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-2 top-2 bottom-2 px-6 bg-black text-white font-black uppercase text-sm tracking-widest hover:bg-red-500 transition-colors"
                            >
                                DRAFT
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right: Meta Info & Tools */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    {/* Visual Comp */}
                    <div className="bg-white border-4 border-black p-6 shadow-md">
                        <h3 className="text-xs font-black uppercase tracking-widest border-b-2 border-black pb-2 mb-4 flex items-center gap-2">
                            <Layers className="w-4 h-4" /> Visual Composition
                        </h3>
                        <div className="space-y-4">
                            <InfoRow label="Framing" value={current_panel.composition || 'Medium Shot'} />
                            <InfoRow label="Atmosphere" value={style || 'Default'} />
                            <div className="h-px bg-black/10 my-4" />
                            <p className="text-[10px] text-black/40 leading-relaxed uppercase font-bold">
                                THE INK-SLINGER ADAPTS TO YOUR NARRATIVE INPUT. BE DESCRIPTIVE TO CHANGE PERSPECTIVES.
                            </p>
                        </div>
                    </div>

                    {/* Quick Palettes */}
                    <div className="bg-white border-4 border-black p-6 shadow-md">
                        <h3 className="text-xs font-black uppercase tracking-widest border-b-2 border-black pb-2 mb-4 flex items-center gap-2">
                            <Palette className="w-4 h-4" /> Narrative Brushes
                        </h3>
                        <div className="grid grid-cols-2 gap-2">
                            <PaletteButton icon={<Zap className="w-3 h-3" />} label="Action" onClick={() => setInput(prev => prev + " [Sudden Action]")} />
                            <PaletteButton icon={<MessageSquare className="w-3 h-3" />} label="Dialogue" onClick={() => setInput(prev => prev + " [Dialogue: ]")} />
                            <PaletteButton icon={<Sparkles className="w-3 h-3" />} label="Effects" onClick={() => setInput(prev => prev + " [POW!]")} />
                            <PaletteButton icon={<Layers className="w-3 h-3" />} label="Style Shift" onClick={() => setInput(prev => prev + " [Cinema Style]")} />
                        </div>
                    </div>
                </div>
            </div>

            {status === 'out_of_ink' && (
                <div className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-md flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full bg-white border-8 border-black p-12 text-center shadow-[40px_40px_0_rgba(255,255,255,0.1)]"
                    >
                        <h2 className="text-7xl font-black uppercase italic tracking-tighter text-black mb-4 underline decoration-red-500">EXT. FIN</h2>
                        <p className="text-xl font-bold uppercase tracking-tight text-black mb-8">The creator has exhausted their creative essence.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="w-full bg-black text-white py-4 font-black uppercase tracking-widest hover:bg-red-500 transition-colors"
                        >
                            RESTART THE MULTIVERSE
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const InfoRow = ({ label, value }: { label: string, value: string }) => (
    <div className="flex justify-between items-center">
        <span className="text-[10px] uppercase font-black text-black/30 tracking-widest">{label}</span>
        <span className="text-xs font-bold text-black uppercase tracking-tight italic">{value}</span>
    </div>
);

const PaletteButton = ({ icon, label, onClick }: { icon: React.ReactNode, label: string, onClick: () => void }) => (
    <button
        onClick={onClick}
        className="flex items-center gap-2 p-2 border-2 border-black hover:bg-yellow-100 transition-colors"
    >
        {icon}
        <span className="text-[10px] font-black uppercase tracking-tighter">{label}</span>
    </button>
);
