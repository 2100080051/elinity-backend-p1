import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { useAuth } from './AuthContext';

interface GameContextType {
    sessionId: string | null;
    groupId: string | null;
    userId: string;
    gameSlug: string | null;
    gameState: any;
    roomCode: string | null;
    sessionStatus: string;
    players: any;
    setGameSession: (sid: string, gid: string, slug: string, state: any, roomCode?: string, status?: string, players?: any) => void;
    updateGameState: (newState: any) => void;
    leaveSession: () => void;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

export const GameProvider = ({ children }: { children: ReactNode }) => {
    const { user } = useAuth();
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [groupId, setGroupId] = useState<string | null>(null);
    const [gameSlug, setGameSlug] = useState<string | null>(null);
    const [gameState, setGameState] = useState<any>({});
    const [roomCode, setRoomCode] = useState<string | null>(null);
    const [sessionStatus, setSessionStatus] = useState<string>("lobby");
    const [players, setPlayers] = useState<any>({});

    const [guestId] = useState(() => {
        const saved = localStorage.getItem('elinity_guest_id');
        if (saved) return saved;
        const newId = `guest_${Math.floor(Math.random() * 100000)}`;
        localStorage.setItem('elinity_guest_id', newId);
        return newId;
    });
    const userId = user?.id || guestId;

    const setGameSession = (sid: string, gid: string, slug: string, state: any, code?: string, status?: string, p?: any) => {
        setSessionId(sid);
        setGroupId(gid);
        setGameSlug(slug);
        setGameState(state || {});
        if (code) setRoomCode(code);
        if (status) setSessionStatus(status);
        if (p) setPlayers(p);
    };

    const updateGameState = (newState: any) => {
        setGameState((prev: any) => ({ ...prev, ...(newState || {}) }));
    };

    const leaveSession = () => {
        setSessionId(null);
        setGroupId(null);
        setGameSlug(null);
        setGameState({});
        setRoomCode(null);
        setSessionStatus("lobby");
        setPlayers({});
    };

    // GLOBAL POLLING for Game Sync
    useEffect(() => {
        if (!sessionId) return;

        const poll = async () => {
            try {
                const { getRoomDetails } = await import('../api/client');
                const resp = await getRoomDetails(sessionId);
                if (resp.ok) {
                    if (resp.status !== sessionStatus) setSessionStatus(resp.status);
                    if (JSON.stringify(resp.players) !== JSON.stringify(players)) setPlayers(resp.players);
                    if (JSON.stringify(resp.state) !== JSON.stringify(gameState)) setGameState(resp.state);
                    if (resp.group_id && resp.group_id !== groupId) setGroupId(resp.group_id);
                }
            } catch (e) {
                console.error("Poll Error:", e);
            }
        };

        const interval = setInterval(poll, 3000);
        return () => clearInterval(interval);
    }, [sessionId, sessionStatus, players, gameState, groupId]);

    return (
        <GameContext.Provider value={{
            sessionId, groupId, userId, gameSlug, gameState, roomCode, sessionStatus, players,
            setGameSession, updateGameState, leaveSession
        }}>
            {children}
        </GameContext.Provider>
    );
};

export const useGame = () => {
    const context = useContext(GameContext);
    if (!context) throw new Error("useGame must be used within GameProvider");
    return context;
};
