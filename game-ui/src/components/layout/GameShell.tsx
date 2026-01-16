import { ReactNode } from 'react';
import { ChatSidebar } from '../chat/ChatSidebar';
import { useGame } from '../../context/GameContext';

interface GameShellProps {
    children: ReactNode;
}

export const GameShell = ({ children }: GameShellProps) => {
    const { sessionId } = useGame();

    return (
        <div className="min-h-screen bg-midnight text-white font-premium relative overflow-hidden">
            {/* Ambient Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-deep-purple/20 blur-[120px] rounded-full mix-blend-screen" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-gold/10 blur-[120px] rounded-full mix-blend-screen" />
            </div>

            {/* content */}
            <div className={`relative z-10 transition-all duration-300 ${sessionId ? 'mr-12 lg:mr-80' : ''}`}>
                <main className="container mx-auto px-4 py-8 min-h-screen flex flex-col">
                    {children}
                </main>
            </div>

            {/* Chat Sidebar - Only visible if in a session */}
            {sessionId && <ChatSidebar />}
        </div>
    );
};
