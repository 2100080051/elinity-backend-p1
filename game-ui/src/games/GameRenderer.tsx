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

export const GameRenderer = () => {
    const { gameSlug, sessionId, gameState, sessionStatus } = useGame();

    const renderGame = () => {
        if (sessionStatus === 'lobby') return <RoomLobby />;

        switch (gameSlug) {
            case 'story-weaver':
                return <StoryWeaverView />;
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
