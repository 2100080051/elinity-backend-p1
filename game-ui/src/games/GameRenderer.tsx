import React from 'react';
import { useGame } from '../context/GameContext';
import { GenericGameView } from './GenericGameView';

import { StoryWeaverView } from './specific/StoryWeaverView';
import { WorldBuildersView } from './specific/WorldBuildersView';
import { TruthLayerView } from './specific/TruthLayerView';
import { MemoryMosaicView } from './specific/MemoryMosaicView';
import { AlignmentGameView } from './specific/AlignmentGameView';
import { MythMakerView } from './specific/MythMakerView';
import { CompassGameView } from './specific/CompassGameView';
import { EchoesView } from './specific/EchoesView';
import { SerendipityStringsView } from './specific/SerendipityStringsView';
import { LongQuestView } from './specific/LongQuestView';
import { RoomLobby } from './RoomLobby';

import { ChatSidebar } from '../components/chat/ChatSidebar';
import { ErrorBoundary } from '../components/shared/ErrorBoundary';

import { AdventureDungeonView } from './specific/AdventureDungeonView';
import { EscapeRoomView } from './specific/EscapeRoomView';
import { EmojiWarView } from './specific/EmojiWarView';
import { ComicCreatorView } from './specific/ComicCreatorView';
import { FortuneTellerView } from './specific/FortuneTellerView';
import { RapBattleView } from './specific/RapBattleView';
import { RoastToastView } from './specific/RoastToastView';
import { ImprovTheaterView } from './specific/ImprovTheaterView';
import { RoleSwapView } from './specific/RoleSwapView';
import { PoetryGardenView } from './specific/PoetryGardenView';
import { MemeForgeView } from './specific/MemeForgeView';
import { AIHeistView } from './specific/AIHeistView';
import { PuzzleArchitectView } from './specific/PuzzleArchitectView';
import { MoodDJView } from './specific/MoodDJView';
import { DreamBuilderView } from './specific/DreamBuilderView';
import { AIFutureForecastView } from './specific/AIFutureForecastView';
import { SymbolQuestView } from './specific/SymbolQuestView';
import { MusicJourneyView } from './specific/MusicJourneyView';
import { CreativeDuelView } from './specific/CreativeDuelView';
import { CulturalExchangeView } from './specific/CulturalExchangeView';
import { MicroMysteriesView } from './specific/MicroMysteriesView';
import { ArtifactMakerView } from './specific/ArtifactMakerView';
import { CharacterSwapView } from './specific/CharacterSwapView';
import { BeastBuilderView } from './specific/BeastBuilderView';
import { SocialLabyrinthView } from './specific/SocialLabyrinthView';
import { TimeTravelersView } from './specific/TimeTravelersView';
import { GuessTheFakeView } from './specific/GuessTheFakeView';
import { HiddenTruthsView } from './specific/HiddenTruthsView';
import { InnerWorldQuestView } from './specific/InnerWorldQuestView';
import { LifeSwapView } from './specific/LifeSwapView';

export const GameRenderer = () => {
    const { gameSlug, sessionId, gameState, sessionStatus } = useGame();

    const renderGame = () => {
        if (sessionStatus === 'lobby') return <RoomLobby />;

        switch (gameSlug) {
            case 'story-weaver':
                return <StoryWeaverView />;
            case 'ai-adventure-dungeon':
                return <AdventureDungeonView />;
            case 'ai-escape-room':
                return <EscapeRoomView />;
            case 'ai-emoji-war':
                return <EmojiWarView />;
            case 'ai-comic-creator':
                return <ComicCreatorView />;
            case 'ai-fortune-teller':
                return <FortuneTellerView />;
            case 'ai-rap-battle':
                return <RapBattleView />;
            case 'ai-roast-tost':
                return <RoastToastView />;
            case 'ai-improv-theater':
                return <ImprovTheaterView />;
            case 'ai-role-swap':
                return <RoleSwapView />;
            case 'ai-poetry-garden':
                return <PoetryGardenView />;
            case 'elinity-meme-forge':
                return <MemeForgeView />;
            case 'ai-heist':
                return <AIHeistView />;
            case 'ai-puzzle-architect':
                return <PuzzleArchitectView />;
            case 'ai-mood-dj':
                return <MoodDJView />;
            case 'ai-dream-builder':
                return <DreamBuilderView />;
            case 'ai-future-forecast':
                return <AIFutureForecastView />;
            case 'ai-symbol-quest':
                return <SymbolQuestView />;
            case 'ai-music-journey':
                return <MusicJourneyView />;
            case 'ai-creative-duel':
                return <CreativeDuelView />;
            case 'ai-cultural-exchange':
                return <CulturalExchangeView />;
            case 'ai-micro-mysteries':
                return <MicroMysteriesView />;
            case 'ai-artifact-maker':
                return <ArtifactMakerView />;
            case 'ai-character-swap':
                return <CharacterSwapView />;
            case 'ai-beast-builder':
                return <BeastBuilderView />;
            case 'ai-social-labyrinth':
                return <SocialLabyrinthView />;
            case 'ai-time-travelers':
                return <TimeTravelersView />;
            case 'ai-guess-the-fake':
                return <GuessTheFakeView />;
            case 'ai-hidden-truths':
                return <HiddenTruthsView />;
            case 'ai-inner-world-quest':
                return <InnerWorldQuestView />;
            case 'ai-life-swap':
                return <LifeSwapView />;
            case 'world-builders':
                return <WorldBuildersView />;
            case 'truth-layer':
                return <TruthLayerView />;
            case 'memory-mosaic':
                return <MemoryMosaicView />;
            case 'alignment-game':
                return <AlignmentGameView />;
            case 'myth-maker':
                return <MythMakerView />;
            case 'compass-game':
                return <CompassGameView />;
            case 'echoes':
                return <EchoesView />;
            case 'serendipity':
                return <SerendipityStringsView />;
            case 'long-quest':
                return <LongQuestView />;
            default:
                return <GenericGameView />;
        }
    };

    return (
        <ErrorBoundary>
            {renderGame()}
            <ChatSidebar />
        </ErrorBoundary>
    );
};
