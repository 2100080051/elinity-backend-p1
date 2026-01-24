import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Globe,
    Map,
    Zap,
    ShieldCheck,
    PenTool,
    MessageSquare,
    ChevronRight,
    Sparkles,
    Award,
    BookOpen,
    Gavel,
    History,
    Anchor
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const CulturalExchangeView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        trust = 30,
        insight = 0,
        artifact = 'Unknown',
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
            console.error("Envoy communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#f8fafc] text-[#1e293b] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Elegant topographical background */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
                <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-blue-600/10 rounded-full blur-[120px]" />
                <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-amber-600/10 rounded-full blur-[100px]" />
            </div>

            {/* Header - Envoy HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b-2 border-slate-200 pb-8 bg-white/50 backdrop-blur-xl p-8 rounded-[2rem] shadow-sm">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-blue-600 rounded-3xl shadow-lg">
                        <Globe className="w-8 h-8 text-white animate-spin-slow" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-light tracking-tight text-slate-900">Interstellar <span className="font-black italic text-blue-600">Accord</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-black tracking-widest text-slate-400">Neutral Mediation Site // Protocol: Green</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <MetricBox label="Diplomatic Trust" value={`${trust}%`} sub="Stability" color="text-blue-600" />
                    <div className="w-px h-12 bg-slate-200" />
                    <MetricBox label="Cultural Insight" value={`${insight}`} sub="Score" color="text-amber-600" />
                    <div className="w-px h-12 bg-slate-200" />
                    <div className="flex flex-col items-center">
                        <span className="text-[10px] uppercase font-black tracking-widest text-slate-300 mb-2">Artifact</span>
                        <span className="px-4 py-1 bg-slate-100 rounded-full text-[11px] font-bold text-slate-700 uppercase italic tracking-tighter">{artifact}</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Negotiation Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, scale: 0.99 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-white border border-slate-200 rounded-[3rem] p-12 relative overflow-hidden flex flex-col justify-center shadow-sm"
                    >
                        <div className="absolute top-10 left-10 opacity-[0.03]">
                            <BookOpen className="w-40 h-40" />
                        </div>

                        <div className="relative z-10 max-w-4xl">
                            <div className="flex items-center gap-2 mb-10 text-[11px] font-black text-slate-300 uppercase tracking-[0.6em]">
                                <Gavel className="w-4 h-4" /> Mediation_Session_Log
                            </div>

                            <p className="text-2xl md:text-3xl font-light leading-relaxed text-slate-700 italic selection:bg-blue-100">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-8 last:mb-0 border-l-4 border-slate-100 pl-12 hover:border-blue-400 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Diplomatic Gestures */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((gesture: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(gesture)}
                                    disabled={loading}
                                    className="px-8 py-3 bg-white border-2 border-slate-100 rounded-2xl hover:bg-blue-50 hover:border-blue-600 hover:text-blue-600 transition-all text-xs font-black uppercase tracking-widest text-slate-400 flex items-center gap-3 group shadow-sm"
                                >
                                    <Sparkles className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-all" />
                                    {gesture}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Formalize your diplomatic proposal..."
                                className="w-full bg-white border-2 border-slate-100 rounded-[2rem] py-8 px-12 focus:outline-none focus:border-blue-600 transition-all text-slate-900 placeholder:text-slate-300 text-2xl font-light italic text-center shadow-lg shadow-blue-900/5"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-16 h-16 bg-blue-600 text-white rounded-2xl flex items-center justify-center hover:bg-slate-900 transition-all shadow-xl"
                            >
                                <PenTool className={`w-8 h-8 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Societal Synergy */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-white border border-slate-200 rounded-[2.5rem] p-10 shadow-sm">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-slate-300 mb-10 flex items-center gap-2 border-b border-slate-100 pb-5">
                            <History className="w-4 h-4" /> Civilizational_Synergy
                        </h3>

                        <div className="space-y-12">
                            <SynergyMeter label="Linguistic Overlap" value={trust} color="bg-blue-600" />
                            <SynergyMeter label="Biological Compatibility" value={85} color="bg-emerald-500" />
                            <SynergyMeter label="Resource Synergy" value={insight % 100} color="bg-amber-500" />
                        </div>

                        <div className="mt-14 p-8 bg-blue-50 border border-blue-100 rounded-[2rem] flex items-start gap-5">
                            <Anchor className="w-6 h-6 text-blue-400 opacity-30 mt-1" />
                            <p className="text-[10px] uppercase font-black tracking-widest leading-loose text-slate-400 italic text-center w-full">
                                "Peace is not the absence of difference, but the mastery of its resonance."
                            </p>
                        </div>
                    </div>

                    <div className="bg-slate-100 border border-slate-200 rounded-[2.5rem] p-8 flex flex-col items-center justify-center gap-4 text-slate-300">
                        <ShieldCheck className="w-12 h-12 opacity-20" />
                        <span className="text-[9px] font-black uppercase tracking-[0.5em] text-center">Safety Protocol Active</span>
                    </div>
                </div>
            </div>

            {status === 'unified' && (
                <div className="fixed inset-0 z-[100] bg-white/95 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Award className="w-24 h-24 text-blue-600 mx-auto mb-10" />
                        <h2 className="text-6xl font-light tracking-tighter text-slate-900 mb-6 uppercase">Universal <span className="font-black italic text-blue-600">Accord</span></h2>
                        <p className="text-slate-400 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm">A new era has dawned. The stars are no longer silent, but sing with the voice of unified worlds.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-slate-900 rounded-3xl text-white font-black uppercase tracking-[0.3em] hover:bg-blue-600 transition-all shadow-2xl"
                        >
                            Log Transmission
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const MetricBox = ({ label, value, sub, color }: { label: string, value: string, sub: string, color: string }) => (
    <div className="text-center">
        <p className="text-[9px] uppercase font-black text-slate-300 tracking-widest mb-1">{label}</p>
        <p className={`text-3xl font-black italic tracking-tighter ${color}`}>{value}</p>
        <p className="text-[8px] uppercase font-bold text-slate-400 tracking-tight">{sub}</p>
    </div>
);

const SynergyMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-4">
        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.4em] text-slate-400">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-sm`}
            />
        </div>
    </div>
);
