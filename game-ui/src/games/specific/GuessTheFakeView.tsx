import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FileSearch,
    UserPlus,
    Zap,
    Activity,
    ShieldAlert,
    Search,
    ChevronRight,
    TrendingUp,
    Fingerprint,
    Layers,
    Sparkles,
    SearchCode,
    AlertTriangle,
    Lightbulb,
    Cpu,
    Coffee,
    Gavel
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const GuessTheFakeView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        suspicion = 10,
        case: caseName = 'The Midnight Heist',
        stress = 10,
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
            console.error("Detonator communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#111111] text-[#eab308] font-mono p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Interrogation Room Lighting */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-yellow-500/10 rounded-full blur-[150px]" />
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/concrete-wall.png')] opacity-20" />
            </div>

            {/* Header - Detonator HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b-4 border-yellow-500/50 pb-8 bg-black/40 backdrop-blur-3xl p-8 rounded-[2rem] shadow-[0_0_50px_rgba(234,179,8,0.1)]">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-yellow-500 rounded-xl shadow-[0_0_30px_rgba(234,179,8,0.5)]">
                        <Gavel className="w-8 h-8 text-black animate-bounce" />
                    </div>
                    <div>
                        <h1 className="text-4xl font-black tracking-tighter text-yellow-500 uppercase italic">Authenticity <span className="text-white">Bureau</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-white/40 italic">Case_ID: {caseName.toUpperCase()} // Recording Active</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <BureauStat label="Bullshit Meter" value={`${suspicion}%`} icon={<AlertTriangle className="w-4 h-4 text-red-500" />} />
                    <div className="w-1 h-10 bg-yellow-500/20" />
                    <BureauStat label="Suspect Stress" value={`${stress}%`} icon={<TrendingUp className="text-orange-500 w-4 h-4" />} />
                    <div className="w-1 h-10 bg-yellow-500/20" />
                    <BureauStat label="Case Status" value="Open" icon={<FileSearch className="w-4 h-4 text-yellow-500" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Interrogation Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex-grow bg-[#1a1a1a] border-4 border-yellow-500/10 rounded-[2.5rem] p-12 relative overflow-hidden flex flex-col justify-center shadow-2xl"
                    >
                        <div className="absolute top-10 right-10 opacity-[0.05] animate-pulse">
                            <Cpu className="w-48 h-48" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto">
                            <div className="flex items-center gap-2 mb-10 text-[11px] font-black text-white/20 uppercase tracking-[0.8em]">
                                <SearchCode className="w-4 h-4" /> Evidence_Stream_Delta
                            </div>

                            <p className="text-2xl md:text-3xl font-light leading-relaxed text-zinc-300 italic selection:bg-yellow-500 selection:text-black">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-8 last:mb-0 border-l-4 border-yellow-500/20 pl-10 hover:border-yellow-500 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Interrogator Actions */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((move: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(move)}
                                    disabled={loading}
                                    className="px-8 py-3 bg-yellow-500/5 border-2 border-yellow-500/20 rounded-xl hover:bg-yellow-500 hover:text-black transition-all text-[11px] font-black uppercase tracking-widest text-yellow-500/40 flex items-center gap-3 group shadow-xl"
                                >
                                    <Fingerprint className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-all scale-50 group-hover:scale-100" />
                                    {move}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-yellow-500/20 rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Press the suspect for more details..."
                                className="w-full bg-[#050505] border-4 border-yellow-500/10 rounded-2xl py-8 px-12 focus:outline-none focus:border-yellow-500 transition-all text-yellow-500 placeholder:text-yellow-900 text-2xl font-light italic text-center shadow-inner"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-16 h-16 bg-yellow-500 text-black rounded-xl flex items-center justify-center hover:bg-white transition-all shadow-2xl"
                            >
                                <Lightbulb className={`w-8 h-8 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Case Analytics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-[#1a1a1a] border-4 border-yellow-500/10 rounded-[2.5rem] p-10 shadow-2xl">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-white/10 mb-10 flex items-center gap-2 border-b-2 border-white/5 pb-5">
                            <TrendingUp className="w-4 h-4" /> Authenticity_Metrics
                        </h3>

                        <div className="space-y-12">
                            <MetricMeter label="Bullshit Level" value={suspicion} color="bg-red-600" />
                            <MetricMeter label="Suspect Pressure" value={stress} color="bg-yellow-500" />
                            <MetricMeter label="Evidence Cohesion" value={45} color="bg-zinc-600" />
                        </div>

                        <div className="mt-14 p-8 bg-yellow-500/5 border border-yellow-500/10 rounded-3xl flex items-start gap-5">
                            <Coffee className="w-6 h-6 text-yellow-500 opacity-20 mt-1" />
                            <p className="text-[10px] uppercase font-black tracking-widest leading-loose text-white/30 italic text-center w-full">
                                "Everyone lies. The trick is to find the lie that keeps them awake at night."
                            </p>
                        </div>
                    </div>

                    <div className="bg-yellow-500/5 border border-yellow-500/10 rounded-[2.5rem] p-8 flex flex-col items-center justify-center gap-4 text-yellow-900">
                        <AlertTriangle className="w-12 h-12 opacity-20 animate-pulse" />
                        <span className="text-[9px] font-black uppercase tracking-[0.6em] text-center">Threat Level: Elevated</span>
                    </div>
                </div>
            </div>

            {status === 'solved' && (
                <div className="fixed inset-0 z-[100] bg-yellow-500 flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Gavel className="w-24 h-24 text-black mx-auto mb-10 shadow-2xl" />
                        <h2 className="text-7xl font-black italic tracking-tighter text-black mb-6 uppercase leading-none">Confession <br />Obtained</h2>
                        <p className="text-black/60 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm px-6">The fake has been exposed. Justice has been served in the hall of authenticity.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-black text-white font-black uppercase tracking-[0.4em] hover:bg-zinc-900 transition-all shadow-2xl rounded-2xl"
                        >
                            Next Case
                        </button>
                    </motion.div>
                </div>
            )}

            {status === 'failed' && (
                <div className="fixed inset-0 z-[100] bg-black flex items-center justify-center p-8 text-yellow-500">
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <AlertTriangle className="w-24 h-24 text-red-600 mx-auto mb-10" />
                        <h2 className="text-7xl font-black italic tracking-tighter mb-6 uppercase">Bureau <br />Failure</h2>
                        <p className="text-yellow-900 mb-14 font-black leading-relaxed tracking-[0.3em] uppercase text-sm">The suspect escaped. The fake remains hidden. The Bureau will remember this.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-yellow-500 text-black font-black uppercase tracking-[0.4em] hover:bg-white transition-all shadow-2xl rounded-2xl"
                        >
                            Try Again
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const BureauStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group cursor-crosshair">
        <div className="flex items-center gap-2 mb-1 justify-center opacity-40 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[9px] uppercase font-black tracking-widest text-white">{label}</span>
        </div>
        <p className="text-3xl font-black italic text-white tracking-tighter group-hover:text-yellow-500 transition-colors uppercase">{value}</p>
    </div>
);

const MetricMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-4">
        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.4em] text-white/20">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-2 bg-black rounded-full overflow-hidden border border-white/5">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-lg`}
            />
        </div>
    </div>
);
