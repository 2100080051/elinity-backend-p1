import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { PremiumButton, PremiumCard, PremiumInput } from '../shared/PremiumComponents';
import { Sparkles, User, Lock, Mail, Phone, LogIn } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const LoginPage = () => {
    const { login, register } = useAuth();
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [formData, setFormData] = useState({
        email: "",
        password: "",
        phone: ""
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            if (isLogin) {
                await login(formData.email || formData.phone, formData.password);
            } else {
                await register(formData.email, formData.password, formData.phone);
            }
        } catch (err: any) {
            setError(err.message || "Authentication failed");
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-midnight relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-900/20 via-black to-black" />
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 50, repeat: Infinity, ease: "linear" }}
                    className="absolute -top-1/2 -right-1/2 w-[100vw] h-[100vw] bg-gold/5 rounded-full blur-[100px]"
                />
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-md p-4 relative z-10"
            >
                <PremiumCard className="p-8 md:p-12 border-white/10 shadow-2xl backdrop-blur-xl bg-black/40">
                    <div className="text-center mb-8">
                        <div className="inline-block p-3 rounded-full bg-white/5 border border-white/10 mb-4">
                            <Sparkles className="text-gold" size={24} />
                        </div>
                        <h2 className="text-3xl font-premium text-white mb-2">{isLogin ? 'Welcome Back' : 'Join the Realm'}</h2>
                        <p className="text-gray-400 text-sm">
                            {isLogin ? 'Enter your credentials to continue your journey.' : 'Begin your adventure with a new identity.'}
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-4">
                            {!isLogin && (
                                <div className="relative">
                                    <PremiumInput
                                        type="text"
                                        placeholder="Phone (Optional)"
                                        value={formData.phone}
                                        onChange={e => setFormData({ ...formData, phone: e.target.value })}
                                        className="pl-10"
                                    />
                                    <Phone size={18} className="absolute left-3 top-3.5 text-gray-500" />
                                </div>
                            )}

                            <div className="relative">
                                <PremiumInput
                                    type="text" // Allow email or phone for login
                                    placeholder={isLogin ? "Email or Phone" : "Email"}
                                    value={formData.email}
                                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                                    className="pl-10"
                                    required={!isLogin || !formData.phone}
                                />
                                <Mail size={18} className="absolute left-3 top-3.5 text-gray-500" />
                            </div>

                            <div className="relative">
                                <PremiumInput
                                    type="password"
                                    placeholder="Password"
                                    value={formData.password}
                                    onChange={e => setFormData({ ...formData, password: e.target.value })}
                                    className="pl-10"
                                    required
                                />
                                <Lock size={18} className="absolute left-3 top-3.5 text-gray-500" />
                            </div>
                        </div>

                        <AnimatePresence>
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="text-red-400 text-sm text-center bg-red-900/20 p-2 rounded border border-red-900/50"
                                >
                                    {error}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <PremiumButton type="submit" className="w-full py-3 mt-6" disabled={loading}>
                            {loading ? (
                                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }} className="inline-block">
                                    <Sparkles size={16} />
                                </motion.div>
                            ) : (
                                <span className="flex items-center justify-center gap-2">
                                    {isLogin ? <LogIn size={16} /> : <User size={16} />}
                                    {isLogin ? 'Sign In' : 'Create Account'}
                                </span>
                            )}
                        </PremiumButton>
                    </form>

                    <div className="mt-8 text-center border-t border-white/5 pt-6">
                        <button
                            type="button"
                            onClick={() => { setIsLogin(!isLogin); setError(""); }}
                            className="text-gold/80 hover:text-gold text-sm underline-offset-4 hover:underline transition-all"
                        >
                            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
                        </button>
                    </div>
                </PremiumCard>
            </motion.div>
        </div>
    );
};
