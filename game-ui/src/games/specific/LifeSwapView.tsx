import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    UserCircle,
    RefreshCcw,
    Zap,
    Activity,
    ShieldAlert,
    Briefcase,
    ChevronRight,
    TrendingUp,
    Fingerprint,
    Layers,
    Sparkles,
    CreditCard,
    Building,
    Home,
    Heart,
    Smartphone
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const LifeSwapView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        sync = 50,
        persona = 'The Corporate Titan',
        status = 'active',
        available_actions = []
    } = gameState;

    const handleAction = async (action: string) => {
        if (!action.trim() || !sessionId || !gameSlug || loading) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'action', action);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("Proxy communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#f8fafc] text-[#1e293b] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Split UI design (Clean vs Dirty overlay) */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 right-0 w-1/2 h-full bg-slate-100/50" />
                <div className="absolute top-0 left-0 w-full h-[4px] bg-sky-500 shadow-[0_0_20px_rgba(14,165,233,0.3)]" />
            </div>

            {/* Header - Proxy HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 bg-white/80 backdrop-blur-3xl p-8 rounded-[2rem] border border-slate-200 shadow-xl">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-sky-500 rounded-2xl shadow-[0_0_30px_rgba(14,165,233,0.3)]">
                        <UserCircle className="w-8 h-8 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tight text-slate-900 uppercase">Life <span className="text-sky-600">Exchange</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-sky-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-[0.3em] text-slate-400 italic">Persona_Active: {persona.toUpperCase()} // Sync_Stability: High</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <ProxyStat label="Integration Sync" value={`${sync}%`} icon={<RefreshCcw className="w-4 h-4 text-sky-500" />} />
                    <div className="w-[1px] h-10 bg-slate-200" />
                    <ProxyStat label="Vibe Check" value="Pass" icon={<Activity className="text-emerald-500 w-4 h-4" />} />
                    <div className="w-[1px] h-10 bg-slate-200" />
                    <ProxyStat label="Lifestyle" value="Premium" icon={<CreditCard className="w-4 h-4 text-amber-500" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Life Stream */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex-grow bg-white border border-slate-200 rounded-[3rem] p-16 relative overflow-hidden flex flex-col justify-center shadow-2xl"
                    >
                        <div className="absolute top-10 right-10 opacity-[0.05]">
                            <Briefcase className="w-48 h-48" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto">
                            <div className="flex items-center gap-2 mb-10 text-[11px] font-black text-slate-300 uppercase tracking-[0.8em]">
                                <Smartphone className="w-4 h-4" /> Persona_Notification_Center
                            </div>

                            <p className="text-2xl md:text-3xl font-light leading-relaxed text-slate-600 italic selection:bg-sky-500 selection:text-white">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-10 last:mb-0 border-l-4 border-sky-500/20 pl-12 hover:border-sky-500 transition-all">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Proxy Choices */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((move: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(move)}
                                    disabled={loading}
                                    className="px-8 py-3.5 bg-sky-50 border border-sky-200 rounded-xl hover:bg-sky-600 hover:text-white transition-all text-[11px] font-black uppercase tracking-widest text-sky-700 flex items-center gap-4 group shadow-md"
                                >
                                    <Sparkles className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-all" />
                                    {move}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-sky-500/10 rounded-full blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Act as the persona... what is your next move?"
                                className="w-full bg-white border-2 border-slate-100 rounded-full py-8 px-14 focus:outline-none focus:border-sky-500 transition-all text-slate-800 placeholder:text-slate-300 text-2xl font-light italic text-center shadow-lg"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-6 top-1/2 -translate-y-1/2 w-16 h-16 bg-sky-600 text-white rounded-full flex items-center justify-center hover:bg-slate-900 transition-all shadow-xl"
                            >
                                <Fingerprint className={`w-8 h-8 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Persona Health */}
                <div className="lg:col-span-4 flex flex-col gap-8">
                    <div className="bg-white border border-slate-200 rounded-[3rem] p-10 shadow-2xl">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.6em] text-slate-300 mb-12 flex items-center gap-2 border-b border-slate-100 pb-6">
                            <TrendingUp className="w-4 h-4" /> Persona_Sync_Diagnostics
                        </h3>

                        <div className="space-y-14">
                            <SyncMeter label="Integration Depth" value={sync} color="bg-sky-500" />
                            <SyncMeter label="Social Approval" value={75} color="bg-indigo-500" />
                            <SyncMeter label="Authenticity Score" value={40} color="bg-rose-500" />
                        </div>

                        <div className="mt-16 p-10 bg-slate-50 border border-slate-100 rounded-[2rem] flex items-start gap-6">
                            <Heart className="w-6 h-6 text-slate-300 mt-1" />
                            <p className="text-[11px] uppercase font-bold tracking-[0.2em] leading-loose text-slate-400 italic text-center w-full">
                                "The key to living another's life is forgetting your own for a moment."
                            </p>
                        </div>
                    </div>

                    <div className="bg-sky-50 border border-sky-100 rounded-[3rem] p-10 flex flex-col items-center justify-center gap-5 text-sky-900 shadow-inner">
                        <Building className="w-12 h-12 opacity-20" />
                        <span className="text-[10px] font-black uppercase tracking-[0.5em] text-center">Simulation Sync: Active</span>
                    </div>
                </div>
            </div>

            {status === 'integrated' && (
                <div className="fixed inset-0 z-[100] bg-white/95 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Heart className="w-24 h-24 text-sky-600 mx-auto mb-10 shadow-[0_0_80px_rgba(14,165,233,0.2)]" />
                        <h2 className="text-7xl font-black italic tracking-tighter text-slate-900 mb-6 uppercase leading-none">Total <br /><span className="text-sky-600">Sync</span></h2>
                        <p className="text-slate-400 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm px-6">The transition is complete. This life is yours. The Exchange was a success.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-slate-900 text-white font-black uppercase tracking-[0.4em] hover:bg-sky-600 transition-all shadow-2xl rounded-full"
                        >
                            End Simulation
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const ProxyStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group cursor-pointer">
        <div className="flex items-center gap-2 mb-2 justify-center opacity-30 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[10px] uppercase font-black tracking-widest text-slate-500">{label}</span>
        </div>
        <p className="text-3xl font-black italic text-slate-800 tracking-tighter group-hover:text-sky-600 transition-colors uppercase">{value}</p>
    </div>
);

const SyncMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-5">
        <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-[0.4em] text-slate-300">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-[2px] bg-slate-100 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-lg`}
            />
        </div>
    </div>
);
