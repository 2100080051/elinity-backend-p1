import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Pickaxe,
    Search,
    Zap,
    Activity,
    ShieldAlert,
    Database,
    ChevronRight,
    TrendingUp,
    Fingerprint,
    Layers,
    Sparkles,
    Shrink,
    Axe,
    Hammer,
    Eye,
    Key
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const HiddenTruthsView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        depth = 0,
        layer = 'The Surface',
        revelations = 0,
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
            console.error("Excavator communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#0a0f0d] text-[#22d3ee] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Strata overlay */}
            <div className="absolute inset-0 pointer-events-none opacity-20">
                <div className="absolute top-0 left-0 w-full h-[2px] bg-cyan-500 shadow-[0_0_20px_rgba(34,211,238,0.5)]" style={{ top: '20%' }} />
                <div className="absolute top-0 left-0 w-full h-[2px] bg-cyan-500 shadow-[0_0_20px_rgba(34,211,238,0.5)]" style={{ top: '40%' }} />
                <div className="absolute top-0 left-0 w-full h-[2px] bg-cyan-500 shadow-[0_0_20px_rgba(34,211,238,0.5)]" style={{ top: '60%' }} />
                <div className="absolute top-0 left-0 w-full h-[2px] bg-cyan-500 shadow-[0_0_20px_rgba(34,211,238,0.5)]" style={{ top: '80%' }} />
            </div>

            {/* Header - Excavator HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border border-cyan-500/30 bg-black/40 backdrop-blur-3xl p-8 rounded-[2.5rem] shadow-[0_0_40px_rgba(34,211,238,0.1)]">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-cyan-950 rounded-2xl border border-cyan-400 shadow-[0_0_30px_rgba(34,211,238,0.3)]">
                        <Pickaxe className="w-8 h-8 text-cyan-400 animate-pulse" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tighter text-white uppercase italic">Digital <span className="text-cyan-400">Excavation</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                            <span className="text-[10px] uppercase font-bold tracking-[0.3em] text-cyan-400/40 italic">Site: Operation_Unmask // Layer: {layer.toUpperCase()}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <ExcavatorStat label="Discovery Depth" value={`${depth}m`} icon={<TrendingUp className="w-4 h-4 text-cyan-400" />} />
                    <div className="w-[1px] h-10 bg-cyan-500/20" />
                    <ExcavatorStat label="Revelations" value={revelations.toString()} icon={<Key className="text-amber-400 w-4 h-4" />} />
                    <div className="w-[1px] h-10 bg-cyan-500/20" />
                    <ExcavatorStat label="Site Integrity" value="Stable" icon={<ShieldAlert className="w-4 h-4 text-emerald-400" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Dig Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, filter: 'brightness(2)' }}
                        animate={{ opacity: 1, filter: 'brightness(1)' }}
                        className="flex-grow bg-[#050505] border border-cyan-500/20 rounded-[3rem] p-16 relative overflow-hidden flex flex-col justify-center shadow-inner"
                    >
                        <div className="absolute inset-0 pointer-events-none opacity-5">
                            <Layers className="w-full h-full text-cyan-400 p-20" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto">
                            <div className="flex items-center gap-2 mb-10 text-[11px] font-black text-cyan-900 uppercase tracking-[0.8em]">
                                <Activity className="w-4 h-4" /> Sonar_Echo_Log
                            </div>

                            <p className="text-2xl md:text-3xl font-light leading-relaxed text-cyan-50 italic selection:bg-cyan-500 selection:text-black">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-10 last:mb-0 border-l-2 border-cyan-500/20 pl-12 hover:border-cyan-400 transition-all">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Excavator Moves */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((move: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(move)}
                                    disabled={loading}
                                    className="px-8 py-3.5 bg-cyan-500/5 border border-cyan-500/30 rounded-xl hover:bg-cyan-500 hover:text-black transition-all text-[11px] font-black uppercase tracking-widest text-cyan-400/40 flex items-center gap-4 group shadow-xl"
                                >
                                    <Sparkles className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all rotate-12" />
                                    {move}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-cyan-400/20 rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Choose where to focus the extraction..."
                                className="w-full bg-black border border-cyan-500/40 rounded-2xl py-8 px-12 focus:outline-none focus:border-cyan-400 transition-all text-cyan-400 placeholder:text-cyan-950 text-2xl font-light italic text-center shadow-[inset_0_0_20px_rgba(0,0,0,0.8)]"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-16 h-16 bg-cyan-600 text-black rounded-xl flex items-center justify-center hover:bg-cyan-400 transition-all shadow-2xl"
                            >
                                <Hammer className={`w-8 h-8 ${loading ? 'animate-bounce' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Technical Sensors */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-[#0c1210] border border-cyan-500/20 rounded-[3rem] p-10 shadow-2xl">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.6em] text-cyan-900 mb-12 flex items-center gap-2 border-b border-cyan-500/5 pb-6">
                            <Database className="w-4 h-4" /> Stratigraphic_Analysis
                        </h3>

                        <div className="space-y-14">
                            <SensorMeter label="Discovery Depth" value={depth} color="bg-cyan-400" />
                            <SensorMeter label="Truth Proximity" value={(revelations / 10) * 100} color="bg-amber-400" />
                            <SensorMeter label="Encryption Density" value={75} color="bg-red-400" />
                        </div>

                        <div className="mt-16 p-10 bg-cyan-400/5 border border-cyan-400/10 rounded-[2rem] flex items-start gap-6">
                            <Eye className="w-6 h-6 text-cyan-400 opacity-20 mt-1" />
                            <p className="text-[11px] uppercase font-bold tracking-[0.2em] leading-loose text-cyan-400/30 italic text-center w-full">
                                "The deepest truths are never told; they are found in the silences between the lies."
                            </p>
                        </div>
                    </div>

                    <div className="bg-cyan-400/5 border border-cyan-400/10 rounded-[3rem] p-10 flex flex-col items-center justify-center gap-5 text-cyan-950">
                        <Layers className="w-12 h-12 opacity-20 animate-pulse" />
                        <span className="text-[9px] font-black uppercase tracking-[0.5em] text-center">Depth Calibration Active</span>
                    </div>
                </div>
            </div>

            {status === 'uncovered' && (
                <div className="fixed inset-0 z-[100] bg-black/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Key className="w-24 h-24 text-cyan-400 mx-auto mb-10 shadow-[0_0_80px_rgba(34,211,238,0.3)] animate-bounce" />
                        <h2 className="text-7xl font-black italic tracking-tighter text-white mb-6 uppercase">Truth <br /><span className="text-cyan-400">Exhumed</span></h2>
                        <p className="text-cyan-400/40 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm px-6">The strata have collapsed. The core reality is yours. The mystery ends here.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-cyan-600 text-black font-black uppercase tracking-[0.4em] hover:bg-white transition-all shadow-2xl rounded-2xl"
                        >
                            Return to Surface
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const ExcavatorStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group cursor-help">
        <div className="flex items-center gap-2 mb-2 justify-center opacity-30 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[9px] uppercase font-black tracking-widest text-cyan-200">{label}</span>
        </div>
        <p className="text-3xl font-black italic text-white tracking-tighter group-hover:text-cyan-400 transition-colors uppercase">{value}</p>
    </div>
);

const SensorMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-5">
        <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-[0.4em] text-cyan-900">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-[2px] bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-lg`}
            />
        </div>
    </div>
);
