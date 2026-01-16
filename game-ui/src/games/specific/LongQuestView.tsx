import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumCard, PremiumText } from '../../components/shared/PremiumComponents';
import { Scroll, Map, Backpack, Sword, Compass, Tent } from 'lucide-react';
import { motion } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const LongQuestView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();

    const narrative = gameState.last_ai_response?.narrative || "The adventure begins. The road ahead is long, but glory awaits.";
    const questLog = gameState.quest_log || [];
    const options = gameState.last_ai_response?.options || ['Travel North', 'Make Camp', 'Check Supplies', 'Scout Area'];
    const visual = gameState.last_ai_response?.visual_cue || "Forest Edge";

    const handleAction = async (act: string) => {
        const resp = await sendAction(gameSlug!, sessionId!, userId, 'action', act);
        if (resp.ok) updateGameState(resp.state);
    };

    return (
        <PremiumGameLayout
            title="The Long Quest"
            subtitle="Epic Journey"
            icon={Map}
            backgroundVar="starfield"
            guideText="1. Embark on a collaborative epic journey across vast digital realms.\n2. In each turn, choose from narrative options to advance the quest.\n3. Keep track of your legacy in the Quest Journal.\n4. Complete the journey with other members of your party."
        >
            <div className="h-full flex flex-col md:flex-row gap-6">
                {/* Left: Quest Log / Sidebar */}
                <div className="hidden md:flex flex-col w-64 bg-black/40 border border-white/5 rounded-2xl overflow-hidden shrink-0">
                    <div className="p-4 bg-white/5 border-b border-white/5 flex items-center justify-between">
                        <span className="text-gold font-bold text-xs uppercase tracking-widest flex items-center gap-2"><Scroll size={14} /> Journal</span>
                    </div>
                    <div className="flex-1 p-4 overflow-y-auto space-y-4 custom-scrollbar">
                        {questLog.length === 0 && <p className="text-gray-500 text-xs italic text-center mt-4">Your journal is blank.</p>}
                        {questLog.map((q: string, i: number) => (
                            <div key={i} className="text-sm font-serif text-gray-300 border-l-2 border-gold/30 pl-3">
                                {q}
                            </div>
                        ))}
                    </div>
                    <div className="p-4 border-t border-white/5 bg-white/5 flex justify-around text-gray-400">
                        <Backpack size={18} className="hover:text-gold cursor-pointer transition-colors" />
                        <Sword size={18} className="hover:text-gold cursor-pointer transition-colors" />
                        <Compass size={18} className="hover:text-gold cursor-pointer transition-colors" />
                    </div>
                </div>

                {/* Right: Main View */}
                <div className="flex-1 flex flex-col gap-6">
                    {/* Visual Header */}
                    <div className="relative h-48 md:h-64 rounded-2xl overflow-hidden group border border-white/5">
                        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent z-10" />
                        {/* Placeholder for dynamic image if available, else CSS pattern */}
                        <div className="absolute inset-0 bg-[#1a2e1a] opacity-50 bg-[url('https://www.transparenttextures.com/patterns/dark-matter.png')]" />

                        <div className="absolute bottom-6 left-6 z-20">
                            <div className="flex items-center gap-2 text-gold text-xs uppercase mb-2 bg-black/60 px-3 py-1 rounded-full backdrop-blur-md inline-flex border border-gold/10">
                                <Map size={12} /> {visual}
                            </div>
                            <h2 className="text-3xl md:text-4xl font-serif text-white text-shadow-lg">Current Location</h2>
                        </div>
                    </div>

                    {/* Narrative */}
                    <div className="flex-1 bg-gradient-to-br from-white/5 to-transparent rounded-2xl p-6 md:p-8 border border-white/5 shadow-2xl relative">
                        <p className="font-serif text-lg md:text-xl leading-relaxed text-gray-200 drop-shadow-sm">
                            <PremiumText text={narrative} />
                        </p>
                    </div>

                    {/* Actions Bar */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                        {options.map((opt: string, i: number) => (
                            <PremiumButton
                                key={opt}
                                variant="secondary"
                                onClick={() => handleAction(opt)}
                                className="text-sm font-serif h-auto py-3 hover:bg-gold/10 hover:border-gold/50 transition-all border-white/5"
                            >
                                {opt}
                            </PremiumButton>
                        ))}
                    </div>
                </div>
            </div>
        </PremiumGameLayout>
    );
};
