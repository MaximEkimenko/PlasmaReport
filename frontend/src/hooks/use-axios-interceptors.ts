import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { setupInterceptors } from "../utils/axiosSetup";


/**
 * Добавляет во все запросы токен авторизации из локального хранилища.
 * Обрабатывает принудительный переход на ситраницу логина, если токен становится невалидным.
 */
export function useAxiosInterceptors()  {
    const navigate = useNavigate();
    useEffect(() => {
        setupInterceptors(navigate);
    }, [navigate]);
};