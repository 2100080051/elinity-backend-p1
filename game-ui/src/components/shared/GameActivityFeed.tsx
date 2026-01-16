import { motion, AnimatePresence } from 'framer-motion';
import { Scroll, User } from 'lucide-react';
import { useGame } from '../../context/GameContext';

interface ActivityEntry {
    user: string;
    action: string;
    content: string;
    timestamp?: string;
}

export const GameActivityFeed = () => {
    const { gameState, players } = useGame();

    // Safety check
    if (!gameState?.history || gameState.history.length === 0) return null;

    // Get last 20 events, reversed for feed style (newest top)
    const events: ActivityEntry[] = [...gameState.history].reverse().slice(0, 20);

    return (
        <div className="absolute top-[100px] left-6 w-72 bg-black/60 backdrop-blur-xl rounded-xl border border-white/10 overflow-hidden z-40 shadow-2xl flex flex-col max-h-[50vh]">
            <div className="p-3 border-b border-white/5 bg-white/5 flex items-center justify-between sticky top-0 z-10">
                <h3 className="text-gold font-bold text-[10px] uppercase tracking-widest flex items-center gap-2">
                    <Scroll size={12} /> Game Log
                </h3>
                <span className="flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
            </div>

            <div className="overflow-y-auto custom-scrollbar p-3 space-y-4 flex-1">
                <AnimatePresence initial={false}>
                    {events.map((entry, i) => {
                        const playerName = players[entry.user]?.name || 'Unknown Seeker';
                        const isMe = entry.user === 'me' || false; // Logic handled in context usually, but here we rely on string

                        return (
                            <motion.div
                                key={`${i}-${entry.timestamp}`}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.3, delay: i * 0.05 }}
                                className="relative pl-3"
                            >
                                <div className="absolute left-0 top-1.5 bottom-0 w-[1px] bg-white/10" />
                                <div className="absolute left-[-2px] top-1.5 w-1 h-1 rounded-full bg-gold/50" />

                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-[10px] font-bold text-purp-200 uppercase tracking-wider flex items-center gap-1">
                                        <User size={8} /> {playerName}
                                    </span>
                                    <span className="text-[9px] text-white/20 uppercase">{entry.action}</span>
                                </div>

                                <p className="text-xs text-gray-300 font-serif leading-relaxed italic border-l-2 border-gold/10 pl-2">
                                    "{entry.content}"
                                </p>
                            </motion.div>
                        );
                    })}
                </AnimatePresence>
            </div>
        </div>
    );
};
