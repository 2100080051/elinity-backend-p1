import React, { useEffect, useState } from 'react';
import { useGame } from '../context/GameContext';
import { getRoomDetails, toggleReady, startGameMulti, startGame } from '../api/client';
import { PremiumButton, PremiumCard, PremiumText } from '../components/shared/PremiumComponents';
import { Users, Copy, CheckCircle2, Circle, Play, LogOut, Sparkles, UserPlus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const RoomLobby = () => {
    const { sessionId, roomCode, userId, players, sessionStatus, gameSlug, setGameSession, leaveSession, updateGameState } = useGame();
    const [localPlayers, setLocalPlayers] = useState<any>(players || {});
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        setLocalPlayers(players);
    }, [players]);

    const isHost = localPlayers[userId]?.role === 'Host';
    const allReady = Object.values(localPlayers).every((p: any) => p.is_ready || p.role === 'Host');

    // Polling is now handled globally in GameContext
    const refreshRoom = async () => {
        // This is now optional but kept for manual refresh if needed
        setIsRefreshing(true);
        try {
            const resp = await getRoomDetails(sessionId!);
            if (resp.ok) setLocalPlayers(resp.players);
        } catch (e) { }
        setIsRefreshing(false);
    };

    const handleToggleReady = async () => {
        if (!sessionId) return;
        const currentReady = localPlayers[userId]?.is_ready || false;
        const resp = await toggleReady(sessionId, !currentReady, userId);
        if (resp.ok) setLocalPlayers(resp.players);
    };

    const handleUpdatePreferences = async (enabled: boolean, persona: string) => {
        if (!sessionId) return;
        const currentReady = localPlayers[userId]?.is_ready || false;
        const resp = await toggleReady(sessionId, currentReady, userId, enabled, persona);
        if (resp.ok) setLocalPlayers(resp.players);
    };

    const handleStart = async () => {
        if (!sessionId || !gameSlug) return;

        // 1. Initialize the specific game logic (call /start)
        const startResp = await startGame(gameSlug, userId);
        if (startResp.ok) {
            // 2. Set room status to active
            await startGameMulti(sessionId);
            setGameSession(sessionId, startResp.group_id, gameSlug, startResp.state, roomCode || "", 'active', localPlayers);
        }
    };

    const copyCode = () => {
        if (roomCode) {
            navigator.clipboard.writeText(roomCode);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="max-w-4xl mx-auto py-12 px-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
            >
                {/* Header Card */}
                <PremiumCard className="text-center py-10">
                    <div className="inline-block p-4 rounded-full bg-gold/10 text-gold mb-6 border border-gold/20 shadow-lg">
                        <Users size={40} />
                    </div>
                    <h1 className="text-4xl font-premium font-bold text-white mb-2 uppercase tracking-widest">
                        {gameSlug?.replace(/-/g, ' ')}
                    </h1>
                    <p className="text-gold/60 uppercase tracking-[0.3em] text-xs font-bold mb-8">Multiplayer Chamber</p>

                    <div className="flex flex-col md:flex-row items-center justify-center gap-4 mt-8">
                        <div className="bg-black/40 border border-white/10 rounded-2xl px-8 py-4 flex items-center gap-6">
                            <div>
                                <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Room Code</p>
                                <p className="text-3xl font-mono font-bold text-white tracking-widest">{roomCode}</p>
                            </div>
                            <button
                                onClick={copyCode}
                                className="p-3 rounded-xl bg-white/5 hover:bg-gold/10 text-gold transition-all border border-white/10"
                            >
                                {copied ? <CheckCircle2 size={24} /> : <Copy size={24} />}
                            </button>
                        </div>

                        <div className="flex items-center gap-2 px-6 py-4 bg-white/5 rounded-2xl border border-white/10">
                            <Sparkles size={16} className="text-gold" />
                            <span className="text-white/80 font-medium">{Object.keys(localPlayers).length} / 5 Players</span>
                        </div>
                    </div>
                </PremiumCard>

                {/* Players Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <AnimatePresence>
                        {Object.entries(localPlayers).map(([pid, p]: [string, any]) => (
                            <motion.div
                                key={pid}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className={`relative p-6 rounded-2xl border transition-all duration-500 ${pid === userId ? 'bg-gold/5 border-gold/30 shadow-[0_0_20px_rgba(251,191,36,0.1)]' : 'bg-black/40 border-white/10'
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold ${pid === userId ? 'bg-gold text-midnight' : 'bg-white/10 text-white'
                                            }`}>
                                            {p.name?.[0].toUpperCase() || 'P'}
                                        </div>
                                        <div>
                                            <p className="font-bold text-white">{p.name || 'Anonymous'}</p>
                                            <div className="flex items-center gap-2">
                                                <p className="text-[10px] text-gray-500 uppercase tracking-widest">
                                                    {p.role === 'Host' ? 'Chamber Master' : 'Seeker'}
                                                </p>
                                                {p.score > 0 && (
                                                    <span className="text-[10px] bg-gold/20 text-gold px-1.5 py-0.5 rounded border border-gold/30 font-bold flex items-center gap-1">
                                                        <Sparkles size={8} /> {p.score} IP
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    {p.role === 'Host' ? (
                                        <div className="text-gold"><Sparkles size={16} /></div>
                                    ) : (
                                        p.is_ready ? <CheckCircle2 size={20} className="text-green-500" /> : <Circle size={20} className="text-gray-600" />
                                    )}
                                </div>

                                {pid === userId ? (
                                    <div className="space-y-3 mt-4 pt-4 border-t border-white/5">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[10px] text-gray-400 uppercase tracking-widest font-bold">Truth Analysis</span>
                                            <button
                                                onClick={() => handleUpdatePreferences(!p.truth_analysis_enabled, p.persona)}
                                                className={`w-10 h-5 rounded-full relative transition-colors ${p.truth_analysis_enabled ? 'bg-indigo-600' : 'bg-white/10'}`}
                                            >
                                                <div className={`absolute top-1 left-1 w-3 h-3 rounded-full bg-white transition-transform ${p.truth_analysis_enabled ? 'translate-x-5' : 'translate-x-0'}`} />
                                            </button>
                                        </div>
                                        <input
                                            value={p.persona || ""}
                                            onChange={(e) => handleUpdatePreferences(p.truth_analysis_enabled, e.target.value)}
                                            placeholder="Set your Persona (e.g. The Rogue)"
                                            className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-xs text-white focus:border-gold/30 outline-none"
                                        />
                                    </div>
                                ) : (
                                    <div className="flex flex-wrap gap-2 mt-4">
                                        <span className={`text-[8px] px-2 py-0.5 rounded-full border ${p.truth_analysis_enabled ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400' : 'bg-white/5 border-white/10 text-gray-500'}`}>
                                            {p.truth_analysis_enabled ? 'Truth Mode Active' : 'Truth Mode Off'}
                                        </span>
                                        {p.persona && (
                                            <span className="text-[8px] px-2 py-0.5 rounded-full bg-gold/5 border border-gold/20 text-gold/60">
                                                Persona: {p.persona}
                                            </span>
                                        )}
                                    </div>
                                )}

                                {p.last_commentary && (
                                    <div className={`mt-4 p-3 rounded-xl text-[10px] italic border ${p.truth_mismatch ? 'bg-red-500/5 border-red-500/20 text-red-300' : 'bg-white/5 border-white/10 text-gold/60'}`}>
                                        "{p.last_commentary}"
                                    </div>
                                )}

                                <div className="flex justify-between items-center mt-6 pt-4 border-t border-white/5">
                                    <div className="text-[10px] text-gray-500 font-medium">
                                        Joined: {p.joined_at?.split(' ')[1]?.substring(0, 5) || 'Now'}
                                    </div>
                                    {p.is_ready && (
                                        <span className="text-[10px] font-bold text-green-500 uppercase tracking-widest flex items-center gap-1">
                                            <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" /> Ready
                                        </span>
                                    )}
                                </div>
                            </motion.div>
                        ))}

                        {/* Invite Slot */}
                        {Object.keys(localPlayers).length < 5 && (
                            <motion.div
                                className="border-2 border-dashed border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center text-gray-500 hover:border-gold/30 hover:text-gold/50 transition-all cursor-pointer group"
                                onClick={copyCode}
                            >
                                <UserPlus size={24} className="mb-2 opacity-20 group-hover:opacity-100" />
                                <span className="text-xs uppercase tracking-widest font-bold">Invite Friend</span>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Footer Actions */}
                <div className="flex flex-col md:flex-row items-center justify-between bg-black/60 p-6 rounded-3xl border border-white/10 backdrop-blur-xl gap-4">
                    <button
                        onClick={leaveSession}
                        className="flex items-center gap-2 text-gray-500 hover:text-red-400 transition-colors uppercase tracking-widest text-xs font-bold"
                    >
                        <LogOut size={16} /> Leave Chamber
                    </button>

                    <div className="flex items-center gap-4 w-full md:w-auto">
                        {!isHost && (
                            <PremiumButton
                                variant={localPlayers[userId]?.is_ready ? 'secondary' : 'primary'}
                                onClick={handleToggleReady}
                                className="flex-1 md:flex-none"
                            >
                                {localPlayers[userId]?.is_ready ? 'Unready' : 'I am Ready'}
                            </PremiumButton>
                        )}

                        {isHost && (
                            <PremiumButton
                                onClick={handleStart}
                                disabled={!allReady || Object.keys(localPlayers).length < 1}
                                className="flex-1 md:flex-none flex items-center justify-center gap-2"
                            >
                                Forge Legend <Play size={18} />
                            </PremiumButton>
                        )}
                    </div>
                </div>

                {!isHost && !allReady && (
                    <p className="text-center text-gold/40 text-[10px] uppercase tracking-[0.3em] animate-pulse">
                        Waiting for all Seekers to be Ready...
                    </p>
                )}
            </motion.div>
        </div>
    );
};
