import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Music,
    Mic2,
    Flame,
    Users,
    Zap,
    Radio,
    Volume2,
    ChevronRight,
    TrendingUp,
    Award,
    Speaker
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const RapBattleView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    if (!gameState) return null;

    const {
        scene = '',
        flow = 0,
        hype = 0,
        round = 1,
        arena = {},
        available_actions = [],
        status = 'active'
    } = gameState;

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [scene]);

    const handleAction = async (action: string) => {
        if (!action.trim() || !sessionId || !gameSlug || loading) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'action', action);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("Vers-Artifact communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#0c0c0e] text-[#f0f0f0] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Urban Texture Overlay */}
            <div className="absolute inset-0 opacity-20 pointer-events-none mix-blend-overlay" style={{ backgroundImage: 'url("https://www.transparenttextures.com/patterns/asphalt-dark.png")' }} />

            {/* Header - Arena Info */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-orange-500/20 rounded-2xl border border-orange-500/30 shadow-[0_0_20px_rgba(249,115,22,0.2)]">
                        <Mic2 className="w-6 h-6 text-orange-500" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black italic tracking-tighter text-white uppercase leading-none">
                            Rap Battle <span className="text-orange-500">Vol.{round}</span>
                        </h1>
                        <p className="text-[10px] uppercase font-bold tracking-[0.3em] text-orange-500/70 mt-1">{arena.location || 'Unknown Venue'}</p>
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <div className="flex flex-col items-center">
                        <Users className="w-5 h-5 text-white/20 mb-1" />
                        <span className="text-xs font-black text-white/40 uppercase tracking-widest">{arena.audience_count || '5K'} Deep</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow h-0 pb-4">
                {/* Left: Performance Metrics */}
                <div className="lg:col-span-3 flex flex-col gap-6">
                    {/* Flow State */}
                    <div className="bg-white/5 border border-white/10 rounded-[2rem] p-6 backdrop-blur-xl flex flex-col gap-4 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                            <TrendingUp className="w-16 h-16" />
                        </div>
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40">Flow State Meter</span>
                        <div className="flex items-end justify-between">
                            <span className="text-4xl font-black italic tracking-tighter text-white">{flow}%</span>
                            <Zap className={`w-6 h-6 ${flow > 70 ? 'text-yellow-400 animate-pulse' : 'text-white/20'}`} />
                        </div>
                        <div className="h-3 w-full bg-black/40 rounded-full border border-white/5 overflow-hidden">
                            <motion.div
                                animate={{ width: `${flow}%` }}
                                className="h-full bg-gradient-to-r from-orange-600 to-yellow-400"
                            />
                        </div>
                    </div>

                    {/* Hype Meter */}
                    <div className="bg-white/5 border border-white/10 rounded-[2rem] p-6 backdrop-blur-xl flex flex-col gap-4 flex-grow relative overflow-hidden">
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40">Crowd Hype Energy</span>
                        <div className="flex-grow flex items-end justify-center gap-2 pt-4">
                            {[...Array(10)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    animate={{ height: `${20 + (Math.random() * 60)}%` }}
                                    transition={{ repeat: Infinity, duration: 0.5, delay: i * 0.05 }}
                                    className={`w-3 rounded-full ${i < (hype / 10) ? 'bg-orange-500' : 'bg-white/5'}`}
                                />
                            ))}
                        </div>
                        <div className="text-center">
                            <span className="text-2xl font-black italic tracking-tighter text-white uppercase">{hype}% Hype</span>
                        </div>
                    </div>
                </div>

                {/* center: Verse Stream */}
                <div className="lg:col-span-9 flex flex-col gap-6">
                    <div
                        ref={scrollRef}
                        className="flex-grow bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-10 overflow-y-auto backdrop-blur-3xl relative group custom-scrollbar"
                    >
                        <div className="absolute top-6 left-6 flex items-center gap-2">
                            <Speaker className="w-4 h-4 text-orange-500" />
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-orange-500/50">Live_Feed // 808_Sub_Frequency</span>
                        </div>

                        <div className="prose prose-invert max-w-none prose-p:text-3xl prose-p:leading-tight prose-p:font-black prose-p:italic prose-p:tracking-tighter prose-p:uppercase prose-p:text-white selection:bg-orange-500/30">
                            {scene.split('\n').map((line: string, i: number) => (
                                <motion.p
                                    initial={{ x: -20, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    transition={{ delay: 0.1 }}
                                    key={i}
                                    className="mb-6 last:mb-0 mix-blend-difference drop-shadow-[0_4px_10px_rgba(0,0,0,0.8)]"
                                >
                                    {line}
                                </motion.p>
                            ))}
                        </div>
                    </div>

                    {/* Controls */}
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-wrap gap-2 justify-center">
                            {available_actions.map((line: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(line)}
                                    disabled={loading}
                                    className="px-6 py-2 bg-white/5 border border-white/10 rounded-xl hover:bg-orange-500/20 hover:border-orange-500/40 transition-all text-[10px] font-black uppercase tracking-widest text-white/60 hover:text-white flex items-center gap-2"
                                >
                                    <ChevronRight className="w-3 h-3 text-orange-500" />
                                    {line}
                                </button>
                            ))}
                        </div>

                        <div className="flex gap-4 items-center">
                            <div className="flex-grow relative overflow-hidden group rounded-[2rem]">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                    placeholder="Drop your verse here..."
                                    className="w-full bg-white/5 border border-white/10 py-5 px-8 focus:outline-none focus:border-orange-500/50 transition-all text-white placeholder:text-white/10 text-xl font-black italic uppercase tracking-tighter"
                                />
                                <div className="absolute bottom-0 left-0 h-1 bg-orange-500" style={{ width: `${(input.length % 100)}%` }} />
                            </div>
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="h-20 w-20 bg-orange-500 rounded-[2rem] flex flex-col items-center justify-center text-black hover:bg-orange-400 active:scale-95 transition-all shadow-2xl group shadow-orange-950/20"
                            >
                                {loading ? <Radio className="w-8 h-8 animate-spin" /> : (
                                    <>
                                        <Flame className="w-8 h-8 group-hover:scale-120 transition-transform" />
                                        <span className="text-[10px] font-black uppercase">BARS</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Victory Overlay */}
            <AnimatePresence>
                {status === 'vanguard' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="fixed inset-0 z-[100] bg-orange-500 flex flex-col items-center justify-center p-10 text-black text-center"
                    >
                        <Award className="w-32 h-32 mb-8 animate-bounce" />
                        <h2 className="text-8xl font-black italic tracking-tighter uppercase mb-4">Vanguard Found</h2>
                        <p className="text-2xl font-black uppercase tracking-[0.5em] opacity-40 mb-12 border-b-4 border-black pb-4">The Pit Has Chosen</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-16 py-6 border-4 border-black text-2xl font-black uppercase hover:bg-black hover:text-orange-500 transition-all"
                        >
                            Encore Round
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
