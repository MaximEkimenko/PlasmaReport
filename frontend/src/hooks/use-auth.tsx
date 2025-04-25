import { useContext } from "react";
import { UserContextType, AuthContext } from "../AuthContext";


export function useAuth(): UserContextType | undefined {
    return useContext(AuthContext);
}
