import React, { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { UserType } from "./pages/Login/Login.types";
import {
    getUserFromStore,
    getTokenFromStore,
    saveTokenToStore,
    saveUserToStore,
    clearStore,
} from "./utils/local-storage";
import { logout as apiLogout } from "./utils/requests";
import { getCurrentUser } from "./utils/requests";


export type UserContextType = {
    token: string | undefined;
    currentUser: UserType | undefined;
    login: (newToken: string) => void;
    logout: () => void;
};
export const AuthContext = createContext<UserContextType | undefined>(undefined);

type childrenProps = { children: React.ReactNode };

export function AuthProvider({ children }: childrenProps) {
    const [token, setToken] = useState<string | undefined>(getTokenFromStore);
    const [currentUser, setCurrentUser] = useState<UserType | undefined>(getUserFromStore);

    const login = useCallback((newToken: string) => {
        setToken(newToken);
    }, []);

    const logout = useCallback(() => {
        setToken(undefined);
        setCurrentUser(undefined);
        apiLogout();
    }, []);

    useEffect(() => {
        const fetchuser = async () => {
            if (token) {
                saveTokenToStore(token);
                try {
                    const user = await getCurrentUser();
                    setCurrentUser(user);
                    saveUserToStore(user);
                } catch (error) {
                    console.error("Ошибка загрузки пользователя:", error);
                    logout(); // если не удалось получить пользователя — разлогинивае
                }
            } else {
                clearStore();
            }
        };
        fetchuser();
    }, [logout, token]);

    const contextObject = useMemo(() => ({ currentUser, token, login, logout }), [currentUser, login, logout, token]);

    return <AuthContext.Provider value={contextObject}>{children}</AuthContext.Provider>;
}


