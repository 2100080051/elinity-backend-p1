import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Clock,
    Package,
    Settings,
    Zap,
    Shield,
    Activity,
    Cpu,
    Terminal,
    AlertTriangle,
    ChevronRight,
    Unlock,
    Key
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const EscapeRoomView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        time_left = 60,
        inventory = [],
        room_state = {},
        puzzles = [],
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
            console.error("Architect communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        handleAction(input);
    };

    return (
        <div className="min-h-screen bg-[#0a0a0c] text-[#a0a0a0] font-mono p-4 md:p-8 flex flex-col gap-6">
            {/* Header - System Status */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/5 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-green-500/10 rounded-xl border border-green-500/20 shadow-[0_0_15px_rgba(34,197,94,0.1)]">
                        <Cpu className="w-6 h-6 text-green-500" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-white tracking-widest uppercase">The Architect</h1>
                        <div className="flex items-center gap-2 text-xs">
                            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-green-500/70">LIMITAL SIMULATION ACTIVE</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-6">
                    <div className="text-right">
                        <p className="text-[10px] uppercase tracking-tighter text-white/40">Chronographic Integrity</p>
                        <div className="flex items-center gap-3">
                            <Clock className="w-5 h-5 text-yellow-500" />
                            <span className={`text-2xl font-black ${time_left < 10 ? 'text-red-500 animate-pulse' : 'text-white'}`}>
                                {time_left}:00
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-grow">
                {/* Left Side - Narrative & Input */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    {/* Main Display */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex-grow bg-white/5 border border-white/10 rounded-2xl p-6 relative overflow-hidden group"
                    >
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-green-500/20 to-transparent" />

                        <div className="flex items-center gap-2 mb-4 text-xs font-bold text-white/40 uppercase tracking-widest">
                            <Terminal className="w-4 h-4" />
                            Visual Feed // {room_state.name || 'Unknown Node'}
                        </div>

                        <div className="prose prose-invert max-w-none text-lg leading-relaxed text-gray-300">
                            {scene.split('\n').map((line: string, i: number) => (
                                <p key={i} className="mb-4">{line}</p>
                            ))}
                        </div>

                        {status === 'failed' && (
                            <div className="mt-8 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-4 text-red-500 font-bold uppercase tracking-widest">
                                <AlertTriangle className="w-6 h-6" />
                                DANGER: Chronographic Collapse Imminent
                            </div>
                        )}
                    </motion.div>

                    {/* Action Interface */}
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-wrap gap-2">
                            {available_actions.map((action: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(action)}
                                    disabled={loading}
                                    className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm hover:bg-white/10 hover:border-white/20 transition-all flex items-center gap-2 group"
                                >
                                    <ChevronRight className="w-4 h-4 text-green-500 opacity-0 group-hover:opacity-100 transition-all" />
                                    {action}
                                </button>
                            ))}
                        </div>

                        <form onSubmit={handleSubmit} className="relative">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Submit neural intent..."
                                className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-6 pr-16 focus:outline-none focus:ring-1 focus:ring-green-500/50 transition-all text-white placeholder:text-white/20"
                            />
                            <button
                                type="submit"
                                className="absolute right-4 top-1/2 -translate-y-1/2 p-2 bg-green-500/10 text-green-500 rounded-lg hover:bg-green-500/20 transition-all"
                            >
                                <Zap className="w-5 h-5" />
                            </button>
                        </form>
                    </div>
                </div>

                {/* Right Side - State Panels */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    {/* Room Metrics */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                        <h2 className="text-xs font-bold text-white/40 uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Activity className="w-4 h-4" />
                            Node Metrics
                        </h2>

                        <div className="space-y-6">
                            <MetricRow
                                icon={<Zap className="w-4 h-4" />}
                                label="Lighting"
                                value={room_state.lighting || 'Unknown'}
                                color="yellow"
                            />
                            <MetricRow
                                icon={<Shield className="w-4 h-4" />}
                                label="Security"
                                value={room_state.security_level || '0'}
                                color="blue"
                            />
                            <MetricRow
                                icon={<Activity className="w-4 h-4" />}
                                label="Structural Integrity"
                                value={`${room_state.integrity || 100}%`}
                                color="green"
                            />
                        </div>
                    </div>

                    {/* Inventory */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                        <h2 className="text-xs font-bold text-white/40 uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Package className="w-4 h-4" />
                            Payload Inventory
                        </h2>

                        {inventory.length > 0 ? (
                            <div className="grid grid-cols-2 gap-3">
                                {inventory.map((item: string, idx: number) => (
                                    <div key={idx} className="p-3 bg-white/5 border border-white/10 rounded-xl flex items-center gap-3 group hover:border-green-500/30 transition-all cursor-default">
                                        <Key className="w-4 h-4 text-green-500" />
                                        <span className="text-xs text-white/80">{item}</span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="border border-dashed border-white/10 rounded-xl p-8 flex flex-col items-center justify-center gap-3 text-white/20">
                                <Package className="w-8 h-8 opacity-20" />
                                <span className="text-[10px] uppercase tracking-widest">Empty Payload</span>
                            </div>
                        )}
                    </div>

                    {/* Puzzle List */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                        <h2 className="text-xs font-bold text-white/40 uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Settings className="w-4 h-4" />
                            Logic Nodes
                        </h2>
                        <div className="space-y-3">
                            {puzzles.map((puzzle: any, idx: number) => (
                                <div key={idx} className="flex items-center justify-between p-3 bg-white/5 border border-white/10 rounded-xl">
                                    <div className="flex items-center gap-3">
                                        <div className={`p-1.5 rounded-lg ${puzzle.status === 'solved' ? 'bg-green-500/20 text-green-500' : 'bg-yellow-500/20 text-yellow-500'}`}>
                                            {puzzle.status === 'solved' ? <Unlock className="w-4 h-4" /> : <Shield className="w-4 h-4" />}
                                        </div>
                                        <div>
                                            <p className="text-xs font-bold text-white">{puzzle.id}</p>
                                            <p className="text-[10px] text-white/40 uppercase">{puzzle.status}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {puzzles.length === 0 && (
                                <p className="text-[10px] text-white/20 text-center uppercase py-4">No active logic nodes</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const MetricRow = ({ icon, label, value, color }: { icon: React.ReactNode, label: string, value: string, color: string }) => (
    <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
            <div className={`text-${color}-500 opacity-50`}>{icon}</div>
            <span className="text-[10px] uppercase tracking-widest text-white/40">{label}</span>
        </div>
        <span className="text-sm font-bold text-white">{value}</span>
    </div>
);
