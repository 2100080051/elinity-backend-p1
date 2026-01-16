import React from 'react';
import { GameProvider, useGame } from './context/GameContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { GameShell } from './components/layout/GameShell';
import { GameLobby } from './games/GameLobby';
import { GameRenderer } from './games/GameRenderer';
import { LoginPage } from './components/auth/LoginPage';
import { Sparkles } from 'lucide-react';

const AppContent = () => {
  const { sessionId } = useGame();
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-midnight flex items-center justify-center text-gold">
        <Sparkles className="animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <GameShell>
      {sessionId ? <GameRenderer /> : <GameLobby />}
      <div className="fixed bottom-2 right-2 text-xs text-white/20 pointer-events-none">v2.3 Premium & Secure</div>
    </GameShell>
  );
};

function App() {
  return (
    <AuthProvider>
      <GameProvider>
        <AppContent />
      </GameProvider>
    </AuthProvider>
  );
}

export default App;
