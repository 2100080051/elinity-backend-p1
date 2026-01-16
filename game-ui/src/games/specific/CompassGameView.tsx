import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumCard, PremiumText } from '../../components/shared/PremiumComponents';
import { Compass, GitBranch, MapPin, Navigation } from 'lucide-react';
import { motion } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const CompassGameView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();

    const narrative = gameState.last_ai_response?.narrative || "You stand at a crossroads, the fog swirling around your ankles. Which path calls to your spirit?";
    const location = gameState.last_ai_response?.location_name || "The Uncharted Crossroads";
    const insights = gameState.last_ai_response?.compass_insights || [];
    const choices = gameState.last_ai_response?.choices || ['Venture North', 'Seek the South', 'Explore East', 'Wander West'];

    const handleChoice = async (c: string) => {
        const resp = await sendAction(gameSlug!, sessionId!, userId, 'choose_path', c);
        if (resp.ok) updateGameState(resp.state);
    };

    return (
        <PremiumGameLayout
            title="The Compass Game"
            subtitle="Wayfinder"
            icon={Compass}
            backgroundVar="nebula"
            guideText="1. Navigate through mysterious locations using your moral compass.\n2. Choose paths based on your inner wayfinding intuition.\n3. The AI provides insights into the significance of your journey.\n4. Discover uncharted areas with other wayfinders."
        >
            <div className="h-full flex flex-col items-center">
                {/* Location Marker */}
                <div className="flex items-center gap-2 text-gold/80 mb-8 border border-gold/20 px-4 py-1 rounded-full bg-black/40 backdrop-blur-md">
                    <MapPin size={14} className="animate-pulse" />
                    <span className="text-xs tracking-[0.2em] font-light uppercase">{location}</span>
                </div>

                <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-12 w-full max-w-4xl">
                    {/* Narrative & Insight */}
                    <div className="flex flex-col justify-center gap-6">
                        <div className="bg-gradient-to-br from-white/10 to-transparent p-1 rounded-2xl">
                            <div className="bg-black/40 backdrop-blur-md p-8 rounded-xl h-full border border-white/5">
                                <h3 className="text-white font-premium text-2xl mb-4 leading-normal">
                                    <PremiumText text={narrative} />
                                </h3>
                                {insights.length > 0 && (
                                    <div className="mt-6 pt-6 border-t border-white/10">
                                        <div className="flex items-center gap-2 text-gold text-xs uppercase tracking-widest mb-2">
                                            <Navigation size={12} /> Insight
                                        </div>
                                        <p className="text-gray-400 italic font-serif leading-relaxed text-sm">
                                            "{insights[0]}"
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Interactive Compass/Choices */}
                    <div className="relative flex flex-col items-center justify-center">
                        {/* Decorative Compass Background */}
                        <div className="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none">
                            <Compass size={400} className="text-white animate-[spin_60s_linear_infinite]" />
                        </div>

                        <div className="space-y-4 w-full max-w-sm relative z-10">
                            {choices.map((c: string, i: number) => (
                                <motion.div
                                    key={c}
                                    initial={{ x: 50, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    transition={{ delay: i * 0.1 }}
                                >
                                    <PremiumButton
                                        variant="secondary"
                                        className="w-full flex items-center justify-between group hover:border-gold hover:bg-gold/10 py-4"
                                        onClick={() => handleChoice(c)}
                                    >
                                        <span className="group-hover:translate-x-1 transition-transform">{c}</span>
                                        <GitBranch size={16} className="opacity-50 group-hover:opacity-100 transition-opacity text-gold" />
                                    </PremiumButton>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </PremiumGameLayout>
    );
};
