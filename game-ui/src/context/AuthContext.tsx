import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, register as apiRegister } from '../api/auth';

interface AuthContextType {
    user: any | null;
    token: string | null;
    isLoading: boolean;
    login: (e: string, p: string) => Promise<void>;
    register: (e: string, p: string, ph?: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<any | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setUser({ id: payload.sub, role: payload.role });
            } catch (e) {
                console.error("Invalid token", e);
                logout();
            }
        }
        setIsLoading(false);
    }, [token]);

    const login = async (email: string, pass: string) => {
        const data = await apiLogin(email, pass);
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
    };

    const register = async (email: string, pass: string, phone: string = "") => {
        const data = await apiRegister(email, pass, phone);
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, isLoading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error("useAuth must be used within AuthProvider");
    return context;
};
